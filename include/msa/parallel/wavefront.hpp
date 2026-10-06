#ifndef MSA_PARALLEL_WAVEFRONT_HPP
#define MSA_PARALLEL_WAVEFRONT_HPP

#include "msa/align/needleman_wunsch.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/core/score_model.hpp"

#include <string_view>

namespace msa::parallel {

/// Computes Gotoh Needleman-Wunsch optimal score using anti-diagonal wavefront parallelism.
/// Uses 3 rotating linear buffers along diagonals to achieve O(min(m, n)) space.
[[nodiscard]] int wavefront_gotoh_score(
    std::string_view seq1,
    std::string_view seq2,
    const core::ScoreModel& model = core::ScoreModel(),
    const core::Blosum62& matrix = core::Blosum62::instance(),
    int threshold = 256
);

/// Wavefront Gotoh alignment returning AlignmentResult
[[nodiscard]] align::AlignmentResult wavefront_gotoh_align(
    std::string_view seq1,
    std::string_view seq2,
    const core::ScoreModel& model = core::ScoreModel(),
    const core::Blosum62& matrix = core::Blosum62::instance(),
    int threshold = 256
);

} // namespace msa::parallel

#endif // MSA_PARALLEL_WAVEFRONT_HPP
