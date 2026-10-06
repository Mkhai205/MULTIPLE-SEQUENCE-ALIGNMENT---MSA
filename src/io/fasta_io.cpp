#include "msa/io/fasta_io.hpp"
#include <fstream>
#include <sstream>
#include <cctype>
#include <unordered_set>

namespace msa::io {

// 256-byte ASCII lookup table
const std::array<uint8_t, 256> ResidueValidator::CHAR_TABLE = []() {
    std::array<uint8_t, 256> table{};
    table.fill(0);

    // Whitespace
    table[static_cast<unsigned char>(' ')] = CHAR_WHITESPACE;
    table[static_cast<unsigned char>('\t')] = CHAR_WHITESPACE;
    table[static_cast<unsigned char>('\r')] = CHAR_WHITESPACE;
    table[static_cast<unsigned char>('\n')] = CHAR_WHITESPACE;

    // Gaps
    table[static_cast<unsigned char>('-')] = CHAR_GAP;
    table[static_cast<unsigned char>('.')] = CHAR_GAP;

    // Standard 20 amino acids
    const char standard_aa[] = "ACDEFGHIKLMNPQRSTVWYacdefghiklmnpqrstvwy";
    for (const char* p = standard_aa; *p != '\0'; ++p) {
        table[static_cast<unsigned char>(*p)] = CHAR_STANDARD;
    }

    // Ambiguity codes: B, Z, X, *
    const char ambiguity[] = "BZX*bzx";
    for (const char* p = ambiguity; *p != '\0'; ++p) {
        table[static_cast<unsigned char>(*p)] = CHAR_AMBIGUITY;
    }

    // Extended codes: U, O, J
    const char extended[] = "UOJuoj";
    for (const char* p = extended; *p != '\0'; ++p) {
        table[static_cast<unsigned char>(*p)] = CHAR_EXTENDED;
    }

    return table;
}();

const std::array<char, 256> ResidueValidator::NORMALIZE_UPPER = []() {
    std::array<char, 256> tbl{};
    for (int i = 0; i < 256; ++i) {
        if (i >= 'a' && i <= 'z') {
            tbl[static_cast<size_t>(i)] = static_cast<char>(i - ('a' - 'A'));
        } else {
            tbl[static_cast<size_t>(i)] = static_cast<char>(i);
        }
    }
    return tbl;
}();

bool ResidueValidator::is_valid(char c, ValidationMode mode) noexcept {
    const auto uc = static_cast<unsigned char>(c);
    const uint8_t flags = CHAR_TABLE[uc];
    switch (mode) {
        case ValidationMode::STRICT_CANONICAL:
            return (flags & CHAR_STANDARD) != 0;
        case ValidationMode::STANDARD_BLOSUM62:
            return (flags & (CHAR_STANDARD | CHAR_AMBIGUITY)) != 0;
        case ValidationMode::PERMISSIVE:
            return (flags & (CHAR_STANDARD | CHAR_AMBIGUITY | CHAR_EXTENDED | CHAR_GAP)) != 0;
        case ValidationMode::ALIGNED_FASTA:
            return (flags & (CHAR_STANDARD | CHAR_AMBIGUITY | CHAR_GAP)) != 0;
    }
    return false;
}

char ResidueValidator::normalize(char c) noexcept {
    const auto uc = static_cast<unsigned char>(c);
    char upper = NORMALIZE_UPPER[uc];
    if (upper == '.') return '-';
    if (upper == 'U') return 'C';
    if (upper == 'O') return 'K';
    if (upper == 'J') return 'X';
    return upper;
}

std::vector<msa::core::Sequence> FastaParser::read_stream(std::istream& is, const Options& options) {
    std::vector<msa::core::Sequence> sequences;
    std::unordered_set<std::string> seen_ids;

    std::string current_id;
    std::string current_desc;
    std::string current_seq;
    current_seq.reserve(1024);

    std::string line;
    size_t line_num = 0;
    bool in_record = false;

    auto flush_record = [&]() {
        if (!in_record) return;
        if (current_seq.empty() && !options.allow_empty_sequences) {
            throw FastaParseException("Empty sequence body for record '" + current_id + "'", line_num, 0, current_id);
        }
        if (options.check_duplicate_ids) {
            if (seen_ids.count(current_id)) {
                throw FastaParseException("Duplicate sequence identifier '" + current_id + "' detected", line_num, 0, current_id);
            }
            seen_ids.insert(current_id);
        }
        // Sequence constructor: (id, raw_seq, description, validate)
        sequences.emplace_back(current_id, current_seq, current_desc, false);
        current_seq.clear();
        current_seq.reserve(1024);
        in_record = false;
    };

    while (std::getline(is, line)) {
        ++line_num;

        // Strip carriage return '\r' if present
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }

        // Skip blank lines
        if (line.empty()) continue;

        // Skip comment lines
        if (line.front() == ';') continue;

        if (line.front() == '>') {
            flush_record();

            // Parse header: >ID[ description]
            size_t start = 1;
            while (start < line.size() && std::isspace(static_cast<unsigned char>(line[start]))) {
                ++start;
            }
            if (start >= line.size()) {
                throw FastaParseException("Header line contains no identifier", line_num, 1);
            }

            size_t id_end = start;
            while (id_end < line.size() && !std::isspace(static_cast<unsigned char>(line[id_end]))) {
                ++id_end;
            }

            current_id = line.substr(start, id_end - start);

            size_t desc_start = id_end;
            while (desc_start < line.size() && std::isspace(static_cast<unsigned char>(line[desc_start]))) {
                ++desc_start;
            }

            if (desc_start < line.size()) {
                size_t desc_end = line.size();
                while (desc_end > desc_start && std::isspace(static_cast<unsigned char>(line[desc_end - 1]))) {
                    --desc_end;
                }
                current_desc = line.substr(desc_start, desc_end - desc_start);
            } else {
                current_desc.clear();
            }

            in_record = true;
        } else {
            if (!in_record) {
                throw FastaParseException("Expected '>' header line, encountered sequence data", line_num, 1);
            }

            // Parse sequence residues
            for (size_t col = 0; col < line.size(); ++col) {
                char c = line[col];
                if (std::isspace(static_cast<unsigned char>(c))) continue;

                if (!ResidueValidator::is_valid(c, options.mode)) {
                    throw FastaParseException(
                        std::string("Invalid amino acid character '") + c + "' (ASCII " + std::to_string(static_cast<int>(c)) + ")",
                        line_num, col + 1, current_id
                    );
                }

                current_seq.push_back(ResidueValidator::normalize(c));
            }
        }
    }

    flush_record();

    if (sequences.empty()) {
        throw FastaParseException("FASTA input contains zero valid sequence records", line_num);
    }

    return sequences;
}

std::vector<msa::core::Sequence> FastaParser::read_file(const std::filesystem::path& filepath, const Options& options) {
    if (!std::filesystem::exists(filepath)) {
        throw FastaParseException("File not found: " + filepath.string());
    }
    std::ifstream file(filepath, std::ios::in);
    if (!file.is_open()) {
        throw FastaParseException("Failed to open file for reading: " + filepath.string());
    }
    return read_stream(file, options);
}

std::vector<msa::core::Sequence> FastaParser::read_string(std::string_view fasta_content, const Options& options) {
    std::istringstream iss{std::string(fasta_content)};
    return read_stream(iss, options);
}

void FastaWriter::write_stream(std::ostream& os, const std::vector<msa::core::Sequence>& sequences, const Options& options) {
    for (const auto& seq : sequences) {
        os << '>' << seq.id();
        if (options.write_description && !seq.description().empty()) {
            os << ' ' << seq.description();
        }
        os << '\n';

        const std::string& data = seq.raw_seq();
        if (options.line_width == 0 || data.size() <= options.line_width) {
            os << data << '\n';
        } else {
            for (size_t i = 0; i < data.size(); i += options.line_width) {
                os << data.substr(i, options.line_width) << '\n';
            }
        }
    }
}

void FastaWriter::write_file(const std::filesystem::path& filepath, const std::vector<msa::core::Sequence>& sequences, const Options& options) {
    std::ofstream file(filepath, std::ios::out | std::ios::trunc);
    if (!file.is_open()) {
        throw std::runtime_error("[FastaWriter] Failed to open file for reading/writing: " + filepath.string());
    }
    write_stream(file, sequences, options);
}

std::string FastaWriter::write_string(const std::vector<msa::core::Sequence>& sequences, const Options& options) {
    std::ostringstream oss;
    write_stream(oss, sequences, options);
    return oss.str();
}

bool FastaWriter::verify_alignment_integrity(
    const std::vector<msa::core::Sequence>& raw_sequences,
    const std::vector<msa::core::Sequence>& aligned_sequences,
    std::string* error_msg
) {
    if (raw_sequences.size() != aligned_sequences.size()) {
        if (error_msg) *error_msg = "Sequence count mismatch: raw=" + std::to_string(raw_sequences.size()) + ", aligned=" + std::to_string(aligned_sequences.size());
        return false;
    }

    if (aligned_sequences.empty()) {
        if (error_msg) *error_msg = "Alignment is empty (0 sequences)";
        return false;
    }

    const size_t expected_aln_len = aligned_sequences[0].length();
    for (size_t i = 0; i < aligned_sequences.size(); ++i) {
        if (aligned_sequences[i].length() != expected_aln_len) {
            if (error_msg) *error_msg = "Aligned length mismatch at sequence " + std::to_string(i) + " ('" + aligned_sequences[i].id() + "'): expected " + std::to_string(expected_aln_len) + ", got " + std::to_string(aligned_sequences[i].length());
            return false;
        }

        // Verify ID match
        if (raw_sequences[i].id() != aligned_sequences[i].id()) {
            if (error_msg) *error_msg = "Sequence ID mismatch at index " + std::to_string(i) + ": raw='" + raw_sequences[i].id() + "', aligned='" + aligned_sequences[i].id() + "'";
            return false;
        }

        // Verify residue conservation
        std::string stripped;
        stripped.reserve(aligned_sequences[i].length());
        for (char c : aligned_sequences[i].raw_seq()) {
            if (c != '-' && c != '.') {
                stripped.push_back(c);
            }
        }

        if (stripped != raw_sequences[i].raw_seq()) {
            if (error_msg) *error_msg = "Residue conservation violated for sequence '" + raw_sequences[i].id() + "'";
            return false;
        }
    }

    return true;
}

} // namespace msa::io
