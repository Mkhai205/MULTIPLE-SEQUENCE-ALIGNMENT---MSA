#ifndef MSA_ALIGN_PROFILE_ALIGNER_HPP
#define MSA_ALIGN_PROFILE_ALIGNER_HPP

#include "msa/align/needleman_wunsch.hpp"
#include "msa/align/hirschberg.hpp"
#include "msa/core/profile.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/core/score_model.hpp"

namespace msa::align {

/// Profile-to-Profile aligner that aligns two profiles and produces a merged profile
class ProfileAligner {
public:
    explicit ProfileAligner(
        const core::ScoreModel& model = core::ScoreModel(),
        const core::Blosum62& matrix = core::Blosum62::instance()
    ) noexcept;

    /// Align two Profile objects and return the newly merged Profile
    [[nodiscard]] core::Profile align(
        const core::Profile& p1,
        const core::Profile& p2
    ) const;

    /// Align two Profile objects and return detailed AlignmentResult (traces + score)
    [[nodiscard]] AlignmentResult alignTraces(
        const core::Profile& p1,
        const core::Profile& p2
    ) const;

    [[nodiscard]] const core::ScoreModel& scoreModel() const noexcept { return model_; }
    void setScoreModel(const core::ScoreModel& model) noexcept { model_ = model; }

    [[nodiscard]] const core::Blosum62& matrix() const noexcept { return matrix_.get(); }
    void setMatrix(const core::Blosum62& matrix) noexcept { matrix_ = matrix; }

private:
    core::ScoreModel model_;
    std::reference_wrapper<const core::Blosum62> matrix_;
    HirschbergAligner hirschberg_;
};

/// Convenience free functions
[[nodiscard]] AlignmentResult align_profiles(
    const core::Profile& p1,
    const core::Profile& p2,
    const core::Blosum62& matrix = core::Blosum62::instance(),
    const core::ScoreModel& model = core::ScoreModel(),
    bool parallel = false
);

[[nodiscard]] core::Profile merge_profiles_aligned(
    const core::Profile& p1,
    const core::Profile& p2,
    const core::Blosum62& matrix = core::Blosum62::instance(),
    const core::ScoreModel& model = core::ScoreModel()
);

} // namespace msa::align

#endif // MSA_ALIGN_PROFILE_ALIGNER_HPP
