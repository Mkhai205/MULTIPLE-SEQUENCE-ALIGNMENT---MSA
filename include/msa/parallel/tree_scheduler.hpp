#ifndef MSA_PARALLEL_TREE_SCHEDULER_HPP
#define MSA_PARALLEL_TREE_SCHEDULER_HPP

#include "msa/tree/guide_tree.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/profile.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/blosum62.hpp"

namespace msa::parallel {

/// Progressively aligns sequences across the guide tree using OpenMP tasks on independent subtrees.
/// max_task_depth limits task spawning to avoid thread overhead on small subtrees.
[[nodiscard]] core::Profile parallel_progressive_align(
    const tree::GuideTree& tree,
    const std::vector<core::Sequence>& sequences,
    const core::ScoreModel& model = core::ScoreModel(),
    const core::Blosum62& matrix = core::Blosum62::instance(),
    int max_task_depth = 4
);

} // namespace msa::parallel

#endif // MSA_PARALLEL_TREE_SCHEDULER_HPP
