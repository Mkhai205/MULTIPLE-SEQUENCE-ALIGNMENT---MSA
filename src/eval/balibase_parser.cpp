#include "msa/eval/balibase_parser.hpp"
#include "msa/io/fasta_io.hpp"

#include <fstream>
#include <sstream>
#include <stdexcept>
#include <algorithm>
#include <cctype>
#include <unordered_map>

namespace msa::eval {

namespace {

std::string trim(std::string_view s) {
    size_t start = 0;
    while (start < s.length() && std::isspace(static_cast<unsigned char>(s[start]))) {
        start++;
    }
    size_t end = s.length();
    while (end > start && std::isspace(static_cast<unsigned char>(s[end - 1]))) {
        end--;
    }
    return std::string(s.substr(start, end - start));
}

} // anonymous namespace

bool BalibaseReference::isCoreColumn(size_t col) const noexcept {
    for (const auto& cb : core_blocks) {
        if (col >= cb.start_col && col <= cb.end_col) {
            return true;
        }
    }
    return false;
}

size_t BalibaseReference::numCoreColumns() const noexcept {
    size_t count = 0;
    for (const auto& cb : core_blocks) {
        if (cb.end_col >= cb.start_col) {
            count += (cb.end_col - cb.start_col + 1);
        }
    }
    return count;
}

std::vector<core::Sequence> BalibaseReference::extractRawSequences() const {
    std::vector<core::Sequence> raw;
    raw.reserve(sequence_ids.size());

    for (size_t i = 0; i < sequence_ids.size(); ++i) {
        std::string ungap;
        ungap.reserve(aligned_sequences[i].size());
        for (char c : aligned_sequences[i]) {
            if (c != '-' && c != '.' && c != '~' && !std::isspace(static_cast<unsigned char>(c))) {
                ungap.push_back(static_cast<char>(std::toupper(static_cast<unsigned char>(c))));
            }
        }
        raw.emplace_back(sequence_ids[i], ungap);
    }

    return raw;
}

BalibaseReference BalibaseParser::parseMSF(const std::filesystem::path& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("BalibaseParser: Unable to open MSF file: " + path.string());
    }
    std::string stem = path.stem().string();
    return parseMSF(file, stem);
}

BalibaseReference BalibaseParser::parseMSF(std::istream& stream, const std::string& id) {
    BalibaseReference ref;
    ref.id = id;

    std::string line;
    bool in_data_block = false;
    std::vector<std::string> ordered_names;
    std::unordered_map<std::string, std::string> seq_data;

    while (std::getline(stream, line)) {
        std::string trimmed = trim(line);
        if (trimmed.empty()) continue;

        if (!in_data_block) {
            if (trimmed == "//" || trimmed.find("//") != std::string::npos) {
                in_data_block = true;
                continue;
            }

            // Look for "Name: <seq_name>"
            size_t name_pos = trimmed.find("Name:");
            if (name_pos != std::string::npos) {
                std::istringstream iss(trimmed.substr(name_pos + 5));
                std::string sname;
                if (iss >> sname) {
                    if (std::find(ordered_names.begin(), ordered_names.end(), sname) == ordered_names.end()) {
                        ordered_names.push_back(sname);
                        seq_data[sname] = "";
                    }
                }
            }
        } else {
            // In alignment data block
            std::istringstream iss(trimmed);
            std::string sname;
            if (iss >> sname) {
                auto it = seq_data.find(sname);
                if (it != seq_data.end()) {
                    std::string chunk;
                    while (iss >> chunk) {
                        for (char c : chunk) {
                            if (c == '.' || c == '~') {
                                it->second.push_back('-');
                            } else if (std::isalpha(static_cast<unsigned char>(c)) || c == '-') {
                                it->second.push_back(c);
                            }
                        }
                    }
                }
            }
        }
    }

    if (ordered_names.empty()) {
        return ref;
    }

    size_t expected_len = seq_data[ordered_names[0]].length();
    for (const auto& name : ordered_names) {
        if (seq_data[name].length() != expected_len) {
            throw std::runtime_error("BalibaseParser: Inconsistent sequence lengths in MSF: " + name);
        }
        ref.sequence_ids.push_back(name);
        ref.aligned_sequences.push_back(seq_data[name]);
    }

    detectCoreBlocksFromResidues(ref);
    return ref;
}

BalibaseReference BalibaseParser::parseFASTA(const std::filesystem::path& path) {
    std::ifstream file(path);
    if (!file.is_open()) {
        throw std::runtime_error("BalibaseParser: Unable to open FASTA file: " + path.string());
    }
    std::string stem = path.stem().string();
    return parseFASTA(file, stem);
}

BalibaseReference BalibaseParser::parseFASTA(std::istream& stream, const std::string& id) {
    BalibaseReference ref;
    ref.id = id;

    std::string line;
    std::string curr_id;
    std::string curr_seq;

    auto flush_seq = [&]() {
        if (!curr_id.empty()) {
            ref.sequence_ids.push_back(curr_id);
            for (char& c : curr_seq) {
                if (c == '.' || c == '~') c = '-';
            }
            ref.aligned_sequences.push_back(curr_seq);
            curr_seq.clear();
        }
    };

    while (std::getline(stream, line)) {
        std::string trimmed = trim(line);
        if (trimmed.empty()) continue;

        if (trimmed[0] == '>') {
            flush_seq();
            size_t space_idx = trimmed.find_first_of(" \t");
            if (space_idx != std::string::npos) {
                curr_id = trimmed.substr(1, space_idx - 1);
            } else {
                curr_id = trimmed.substr(1);
            }
        } else {
            for (char c : trimmed) {
                if (!std::isspace(static_cast<unsigned char>(c))) {
                    curr_seq.push_back(c);
                }
            }
        }
    }
    flush_seq();

    if (!ref.aligned_sequences.empty()) {
        size_t len = ref.aligned_sequences[0].length();
        for (const auto& s : ref.aligned_sequences) {
            if (s.length() != len) {
                throw std::runtime_error("BalibaseParser: Inconsistent sequence lengths in aligned FASTA");
            }
        }
    }

    detectCoreBlocksFromResidues(ref);
    return ref;
}

void BalibaseParser::detectCoreBlocksFromResidues(BalibaseReference& ref) {
    ref.core_blocks.clear();
    if (ref.aligned_sequences.empty() || ref.length() == 0) {
        return;
    }

    size_t len = ref.length();
    size_t num_seqs = ref.numSequences();

    // Check if there are mixed uppercase/lowercase residues (standard BAliBASE MSF notation)
    bool has_lowercase = false;
    bool has_uppercase = false;
    for (const auto& s : ref.aligned_sequences) {
        for (char c : s) {
            if (std::islower(static_cast<unsigned char>(c))) has_lowercase = true;
            if (std::isupper(static_cast<unsigned char>(c))) has_uppercase = true;
        }
    }

    std::vector<bool> is_core_col(len, false);

    if (has_lowercase && has_uppercase) {
        // Core columns are columns where ALL non-gap residues are uppercase
        for (size_t c = 0; c < len; ++c) {
            bool all_upper_non_gap = true;
            size_t non_gaps = 0;
            for (size_t k = 0; k < num_seqs; ++k) {
                char ch = ref.aligned_sequences[k][c];
                if (ch == '-') continue;
                non_gaps++;
                if (!std::isupper(static_cast<unsigned char>(ch))) {
                    all_upper_non_gap = false;
                    break;
                }
            }
            if (all_upper_non_gap && non_gaps > 0) {
                is_core_col[c] = true;
            }
        }
    } else {
        // If no lowercase convention is present, core columns are gapless columns
        for (size_t c = 0; c < len; ++c) {
            bool gapless = true;
            for (size_t k = 0; k < num_seqs; ++k) {
                if (ref.aligned_sequences[k][c] == '-') {
                    gapless = false;
                    break;
                }
            }
            is_core_col[c] = gapless;
        }
    }

    // Convert contiguous runs of core columns into CoreBlock intervals
    size_t col = 0;
    while (col < len) {
        if (is_core_col[col]) {
            size_t start = col;
            while (col + 1 < len && is_core_col[col + 1]) {
                col++;
            }
            ref.core_blocks.push_back(CoreBlock{start, col});
        }
        col++;
    }
}

} // namespace msa::eval
