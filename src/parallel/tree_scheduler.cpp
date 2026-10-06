#include "msa/parallel/tree_scheduler.hpp"
#include "msa/align/profile_aligner.hpp"

#include <stdexcept>

#if defined(_OPENMP)
#include <omp.h>
#endif

namespace msa::parallel {

core::Profile parallel_progressive_align(
    const tree::GuideTree& tree,
    const std::vector<core::Sequence>& sequences,
    const core::ScoreModel& model,
    const core::Blosum62& matrix,
    int max_task_depth
) {
    if (tree.empty()) {
        return core::Profile();
    }

    align::ProfileAligner aligner(model, matrix);

    std::function<core::Profile(const tree::GuideTreeNode*, int)> task_align =
        [&](const tree::GuideTreeNode* node, int depth) -> core::Profile {
            if (!node) return core::Profile();

            if (node->is_leaf) {
                if (node->sequence_index >= 0 && static_cast<size_t>(node->sequence_index) < sequences.size()) {
                    return core::Profile(sequences[static_cast<size_t>(node->sequence_index)]);
                }
                throw std::runtime_error("Invalid leaf sequence index in tree scheduler");
            }

            core::Profile left_prof;
            core::Profile right_prof;

#if defined(_OPENMP)
            if (depth < max_task_depth) {
                #pragma omp parallel sections shared(left_prof, right_prof)
                {
                    #pragma omp section
                    {
                        left_prof = task_align(node->left.get(), depth + 1);
                    }
                    #pragma omp section
                    {
                        right_prof = task_align(node->right.get(), depth + 1);
                    }
                }
            } else
#endif
            {
                left_prof = task_align(node->left.get(), depth + 1);
                right_prof = task_align(node->right.get(), depth + 1);
            }

            return aligner.align(left_prof, right_prof);
        };

#if defined(_OPENMP)
    int old_nested = omp_get_nested();
    omp_set_nested(1);
    core::Profile root_prof = task_align(tree.root(), 0);
    omp_set_nested(old_nested);
#else
    core::Profile root_prof = task_align(tree.root(), 0);
#endif

    return root_prof;
}

} // namespace msa::parallel
