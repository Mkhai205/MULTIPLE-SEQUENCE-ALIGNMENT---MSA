#ifndef MSA_TREE_UPGMA_HPP
#define MSA_TREE_UPGMA_HPP

#include "msa/tree/guide_tree.hpp"
#include "msa/tree/distance_matrix.hpp"
#include "msa/core/sequence.hpp"
#include <vector>
#include <string>

namespace msa::tree {

class UPGMA {
public:
    // Build a binary GuideTree from a distance matrix and sequence names
    [[nodiscard]] static GuideTree buildTree(
        const DistanceMatrix& dist_matrix,
        const std::vector<std::string>& sequence_names
    );

    // Convenience method: build directly from sequences
    [[nodiscard]] static GuideTree buildTree(
        const std::vector<core::Sequence>& sequences,
        const core::ScoreModel& model = core::ScoreModel(),
        const core::Blosum62& matrix = core::Blosum62::instance(),
        bool parallel = false
    );
};

} // namespace msa::tree

#endif // MSA_TREE_UPGMA_HPP
