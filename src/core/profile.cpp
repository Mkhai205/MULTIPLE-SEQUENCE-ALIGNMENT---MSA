#include "msa/core/profile.hpp"
#include <stdexcept>
#include <algorithm>
#include <cmath>

namespace msa::core {

Profile::Profile(const Sequence& seq)
    : length_(seq.length()),
      num_sequences_(seq.empty() ? 0 : 1),
      sequence_ids_(seq.empty() ? std::vector<std::string>{} : std::vector<std::string>{seq.id()}),
      aligned_sequences_(seq.empty() ? std::vector<std::string>{} : std::vector<std::string>{seq.raw_seq()}) {
    buildMatrix();
}

Profile::Profile(std::vector<std::string> ids, std::vector<std::string> aligned_sequences)
    : sequence_ids_(std::move(ids)),
      aligned_sequences_(std::move(aligned_sequences)) {
    num_sequences_ = aligned_sequences_.size();
    if (sequence_ids_.size() != num_sequences_) {
        throw std::invalid_argument("Profile: sequence IDs count must match aligned sequences count");
    }
    if (num_sequences_ == 0) {
        length_ = 0;
        return;
    }

    length_ = aligned_sequences_[0].length();
    for (size_t k = 1; k < num_sequences_; ++k) {
        if (aligned_sequences_[k].length() != length_) {
            throw std::invalid_argument("Profile: all aligned sequences must have equal length");
        }
    }

    buildMatrix();
}

void Profile::buildMatrix() {
    column_frequencies_.assign(length_, std::array<double, ALPHABET_SIZE>{});
    column_gap_frequencies_.assign(length_, 0.0);
    column_counts_.assign(length_, std::array<int, ALPHABET_SIZE>{});
    column_gap_counts_.assign(length_, 0);

    if (num_sequences_ == 0 || length_ == 0) {
        return;
    }

    double inv_k = 1.0 / static_cast<double>(num_sequences_);

    for (size_t c = 0; c < length_; ++c) {
        for (size_t k = 0; k < num_sequences_; ++k) {
            char ch = aligned_sequences_[k][c];
            if (ch == '-' || ch == '.') {
                column_gap_counts_[c]++;
            } else {
                int aa_idx = Blosum62::charToIndex(ch);
                column_counts_[c][static_cast<size_t>(aa_idx)]++;
            }
        }

        column_gap_frequencies_[c] = static_cast<double>(column_gap_counts_[c]) * inv_k;
        for (size_t a = 0; a < ALPHABET_SIZE; ++a) {
            column_frequencies_[c][a] = static_cast<double>(column_counts_[c][a]) * inv_k;
        }
    }
}

double Profile::aminoAcidFrequency(size_t col, char aa) const {
    if (col >= length_) return 0.0;
    int idx = Blosum62::charToIndex(aa);
    return column_frequencies_[col][static_cast<size_t>(idx)];
}

std::array<double, 26> Profile::getLetterFrequencies(size_t col) const {
    std::array<double, 26> letter_freq{};
    letter_freq.fill(0.0);
    if (col >= length_) return letter_freq;

    for (size_t idx = 0; idx < ALPHABET_SIZE; ++idx) {
        char ch = Blosum62::indexToChar(static_cast<int>(idx));
        if (ch >= 'A' && ch <= 'Z') {
            letter_freq[static_cast<size_t>(ch - 'A')] += column_frequencies_[col][idx];
        }
    }
    return letter_freq;
}

double Profile::scoreColumns(
    const Profile& p1, size_t col1,
    const Profile& p2, size_t col2,
    const Blosum62& blosum
) noexcept {
    const auto& f1 = p1.column_frequencies_[col1];
    const auto& f2 = p2.column_frequencies_[col2];
    const auto& mat = blosum.matrix();

    double total_score = 0.0;

    // Sparsity-aware Sum-of-Pairs calculation
    for (size_t a = 0; a < ALPHABET_SIZE; ++a) {
        double fa = f1[a];
        if (fa == 0.0) continue;

        for (size_t b = 0; b < ALPHABET_SIZE; ++b) {
            double fb = f2[b];
            if (fb == 0.0) continue;

            total_score += fa * fb * static_cast<double>(mat[a][b]);
        }
    }

    return total_score;
}

Profile Profile::mergeProfiles(
    const Profile& p1,
    const Profile& p2,
    const std::string& aligned_trace1,
    const std::string& aligned_trace2
) {
    if (aligned_trace1.length() != aligned_trace2.length()) {
        throw std::invalid_argument("Profile::mergeProfiles: aligned traces must have equal length");
    }

    size_t new_len = aligned_trace1.length();
    size_t k1 = p1.numSequences();
    size_t k2 = p2.numSequences();

    std::vector<std::string> new_ids;
    new_ids.reserve(k1 + k2);
    for (const auto& id : p1.sequenceIds()) new_ids.push_back(id);
    for (const auto& id : p2.sequenceIds()) new_ids.push_back(id);

    std::vector<std::string> new_seqs(k1 + k2);
    for (auto& s : new_seqs) {
        s.reserve(new_len);
    }

    size_t col_p1 = 0;
    size_t col_p2 = 0;

    for (size_t pos = 0; pos < new_len; ++pos) {
        char t1 = aligned_trace1[pos];
        char t2 = aligned_trace2[pos];

        // Trace 1 handling: if gap was inserted against p1, append '-' to all sequences of p1
        if (t1 == '-') {
            for (size_t k = 0; k < k1; ++k) {
                new_seqs[k].push_back('-');
            }
        } else {
            for (size_t k = 0; k < k1; ++k) {
                new_seqs[k].push_back(p1.alignedSequences()[k][col_p1]);
            }
            col_p1++;
        }

        // Trace 2 handling: if gap was inserted against p2, append '-' to all sequences of p2
        if (t2 == '-') {
            for (size_t k = 0; k < k2; ++k) {
                new_seqs[k1 + k].push_back('-');
            }
        } else {
            for (size_t k = 0; k < k2; ++k) {
                new_seqs[k1 + k].push_back(p2.alignedSequences()[k][col_p2]);
            }
            col_p2++;
        }
    }

    return Profile(std::move(new_ids), std::move(new_seqs));
}

std::string Profile::consensusSequence() const {
    std::string consensus;
    consensus.reserve(length_);

    for (size_t c = 0; c < length_; ++c) {
        if (column_gap_frequencies_[c] > 0.5) {
            consensus.push_back('-');
            continue;
        }

        int best_aa = 22; // default 'X'
        double max_freq = -1.0;

        for (size_t a = 0; a < ALPHABET_SIZE; ++a) {
            if (column_frequencies_[c][a] > max_freq) {
                max_freq = column_frequencies_[c][a];
                best_aa = static_cast<int>(a);
            }
        }

        consensus.push_back(Blosum62::indexToChar(best_aa));
    }

    return consensus;
}

double Profile::conservationScore(size_t col) const {
    if (col >= length_) return 0.0;
    double max_freq = 0.0;
    for (size_t a = 0; a < ALPHABET_SIZE; ++a) {
        if (column_frequencies_[col][a] > max_freq) {
            max_freq = column_frequencies_[col][a];
        }
    }
    return max_freq;
}

} // namespace msa::core
