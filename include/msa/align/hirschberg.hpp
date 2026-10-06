#ifndef MSA_ALIGN_HIRSCHBERG_HPP
#define MSA_ALIGN_HIRSCHBERG_HPP

#include "msa/align/needleman_wunsch.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/profile.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/core/score_model.hpp"

#include <string>
#include <string_view>
#include <functional>
#include <cstddef>

namespace msa::align {

/// Hirschberg linear-space aligner using Myers-Miller (1988) divide-and-conquer
class HirschbergAligner {
public:
    explicit HirschbergAligner(
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

    /// Align two Profile objects using Sum-of-Pairs scoring
    [[nodiscard]] AlignmentResult align(
        const core::Profile& p1,
        const core::Profile& p2
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

/// Convenience free functions for Hirschberg alignment
[[nodiscard]] AlignmentResult hirschberg_align(
    const core::Sequence& seq1,
    const core::Sequence& seq2,
    const core::ScoreModel& model = core::ScoreModel(),
    const core::Blosum62& matrix = core::Blosum62::instance()
);

[[nodiscard]] AlignmentResult hirschberg_align(
    std::string_view seq1,
    std::string_view seq2,
    const core::ScoreModel& model = core::ScoreModel(),
    const core::Blosum62& matrix = core::Blosum62::instance()
);

[[nodiscard]] AlignmentResult hirschberg_align(
    const core::Profile& p1,
    const core::Profile& p2,
    const core::ScoreModel& model = core::ScoreModel(),
    const core::Blosum62& matrix = core::Blosum62::instance()
);

} // namespace msa::align

#endif // MSA_ALIGN_HIRSCHBERG_HPP
