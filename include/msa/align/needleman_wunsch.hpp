#ifndef MSA_ALIGN_NEEDLEMAN_WUNSCH_HPP
#define MSA_ALIGN_NEEDLEMAN_WUNSCH_HPP

#include "msa/core/sequence.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/core/score_model.hpp"

#include <string>
#include <string_view>
#include <functional>
#include <cstddef>

namespace msa::align {

/// Result of a pairwise sequence alignment
struct AlignmentResult {
    std::string aligned_seq1;
    std::string aligned_seq2;
    int score{0};
    size_t peak_memory_bytes{0};

    bool operator==(const AlignmentResult& other) const noexcept {
        return score == other.score &&
               aligned_seq1 == other.aligned_seq1 &&
               aligned_seq2 == other.aligned_seq2;
    }
    bool operator!=(const AlignmentResult& other) const noexcept {
        return !(*this == other);
    }
};

/// Sequential pairwise Needleman-Wunsch aligner using Gotoh (1982) 3-matrix DP
class NeedlemanWunsch {
public:
    explicit NeedlemanWunsch(
        const core::ScoreModel& model = core::ScoreModel(),
        const core::Blosum62& matrix = core::Blosum62::instance()
    ) noexcept;

    /// Align two Sequence objects
    [[nodiscard]] AlignmentResult align(
        const core::Sequence& seq1,
        const core::Sequence& seq2
    ) const;

    /// Align two raw sequence string views
    [[nodiscard]] AlignmentResult align(
        std::string_view seq1,
        std::string_view seq2
    ) const;

    /// Score model accessor and mutator
    [[nodiscard]] const core::ScoreModel& scoreModel() const noexcept { return model_; }
    void setScoreModel(const core::ScoreModel& model) noexcept { model_ = model; }

    /// Matrix accessor and mutator
    [[nodiscard]] const core::Blosum62& matrix() const noexcept { return matrix_.get(); }
    void setMatrix(const core::Blosum62& matrix) noexcept { matrix_ = matrix; }

private:
    core::ScoreModel model_;
    std::reference_wrapper<const core::Blosum62> matrix_;
};

/// Convenience free function for Needleman-Wunsch alignment
[[nodiscard]] AlignmentResult needleman_wunsch_align(
    const core::Sequence& seq1,
    const core::Sequence& seq2,
    const core::ScoreModel& model = core::ScoreModel(),
    const core::Blosum62& matrix = core::Blosum62::instance()
);

[[nodiscard]] AlignmentResult needleman_wunsch_align(
    std::string_view seq1,
    std::string_view seq2,
    const core::ScoreModel& model = core::ScoreModel(),
    const core::Blosum62& matrix = core::Blosum62::instance()
);

} // namespace msa::align

#endif // MSA_ALIGN_NEEDLEMAN_WUNSCH_HPP
