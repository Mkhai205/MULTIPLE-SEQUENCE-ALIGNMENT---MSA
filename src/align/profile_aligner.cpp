#include "msa/align/profile_aligner.hpp"

namespace msa::align {

ProfileAligner::ProfileAligner(
    const core::ScoreModel& model,
    const core::Blosum62& matrix
) noexcept
    : model_(model), matrix_(matrix), hirschberg_(model, matrix) {}

core::Profile ProfileAligner::align(
    const core::Profile& p1,
    const core::Profile& p2
) const {
    AlignmentResult res = hirschberg_.align(p1, p2);
    return core::Profile::mergeProfiles(p1, p2, res.aligned_seq1, res.aligned_seq2);
}

AlignmentResult ProfileAligner::alignTraces(
    const core::Profile& p1,
    const core::Profile& p2
) const {
    return hirschberg_.align(p1, p2);
}

AlignmentResult align_profiles(
    const core::Profile& p1,
    const core::Profile& p2,
    const core::Blosum62& matrix,
    const core::ScoreModel& model,
    bool /*parallel*/
) {
    ProfileAligner aligner(model, matrix);
    return aligner.alignTraces(p1, p2);
}

core::Profile merge_profiles_aligned(
    const core::Profile& p1,
    const core::Profile& p2,
    const core::Blosum62& matrix,
    const core::ScoreModel& model
) {
    ProfileAligner aligner(model, matrix);
    return aligner.align(p1, p2);
}

} // namespace msa::align
