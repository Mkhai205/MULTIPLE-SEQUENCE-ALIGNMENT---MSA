#ifndef MSA_CORE_PROFILE_HPP
#define MSA_CORE_PROFILE_HPP

#include "msa/core/sequence.hpp"
#include "msa/core/blosum62.hpp"
#include <vector>
#include <string>
#include <array>
#include <cstddef>

namespace msa::core {

class Profile {
public:
    static constexpr size_t ALPHABET_SIZE = Blosum62::DIMENSION; // 24

    // Constructors
    Profile() = default;
    explicit Profile(const Sequence& seq);
    Profile(std::vector<std::string> ids, std::vector<std::string> aligned_sequences);

    // Rule of 5
    Profile(const Profile&) = default;
    Profile(Profile&&) noexcept = default;
    Profile& operator=(const Profile&) = default;
    Profile& operator=(Profile&&) noexcept = default;
    ~Profile() = default;

    // Dimensions
    [[nodiscard]] size_t length() const noexcept { return length_; }
    [[nodiscard]] size_t size() const noexcept { return num_sequences_; }
    [[nodiscard]] size_t numSequences() const noexcept { return num_sequences_; }
    [[nodiscard]] bool empty() const noexcept { return length_ == 0 || num_sequences_ == 0; }

    // Sequence access
    [[nodiscard]] const std::vector<std::string>& sequenceIds() const noexcept { return sequence_ids_; }
    [[nodiscard]] const std::vector<std::string>& alignedSequences() const noexcept { return aligned_sequences_; }
    [[nodiscard]] const std::string& getAlignedSequence(size_t index) const { return aligned_sequences_.at(index); }
    [[nodiscard]] const std::string& getSequenceId(size_t index) const { return sequence_ids_.at(index); }

    // Column Frequency Access (indexed by Blosum62 0..23)
    [[nodiscard]] const std::array<double, ALPHABET_SIZE>& columnFrequencies(size_t col) const {
        return column_frequencies_.at(col);
    }
    [[nodiscard]] double gapFrequency(size_t col) const {
        return column_gap_frequencies_.at(col);
    }
    [[nodiscard]] double aminoAcidFrequency(size_t col, char aa) const;

    // Column Counts Access
    [[nodiscard]] const std::array<int, ALPHABET_SIZE>& columnCounts(size_t col) const {
        return column_counts_.at(col);
    }
    [[nodiscard]] int gapCount(size_t col) const {
        return column_gap_counts_.at(col);
    }

    // Scoring
    [[nodiscard]] static double scoreColumns(
        const Profile& p1, size_t col1,
        const Profile& p2, size_t col2,
        const Blosum62& blosum
    ) noexcept;

    // Progressive Merging: combines two profiles according to aligned traces
    [[nodiscard]] static Profile mergeProfiles(
        const Profile& p1,
        const Profile& p2,
        const std::string& aligned_trace1,
        const std::string& aligned_trace2
    );

    // Analysis helpers
    [[nodiscard]] std::string consensusSequence() const;
    [[nodiscard]] double conservationScore(size_t col) const;

    // Compatibility adapter (26-element A-Z array)
    [[nodiscard]] std::array<double, 26> getLetterFrequencies(size_t col) const;

private:
    size_t length_{0};
    size_t num_sequences_{0};
    std::vector<std::string> sequence_ids_;
    std::vector<std::string> aligned_sequences_;

    // Per-column statistics
    std::vector<std::array<double, ALPHABET_SIZE>> column_frequencies_;
    std::vector<double> column_gap_frequencies_;
    std::vector<std::array<int, ALPHABET_SIZE>> column_counts_;
    std::vector<int> column_gap_counts_;

    void buildMatrix();
};

} // namespace msa::core

#endif // MSA_CORE_PROFILE_HPP
