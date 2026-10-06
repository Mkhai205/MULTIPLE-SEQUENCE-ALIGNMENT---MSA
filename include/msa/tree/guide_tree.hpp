#ifndef MSA_TREE_GUIDE_TREE_HPP
#define MSA_TREE_GUIDE_TREE_HPP

#include "msa/core/sequence.hpp"
#include "msa/core/profile.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/tree/distance_matrix.hpp"

#include <memory>
#include <string>
#include <vector>
#include <functional>

namespace msa::tree {

struct GuideTreeNode {
    int id{-1};                  // Unique node ID
    int sequence_index{-1};      // >= 0 if leaf, -1 if internal
    std::string name;            // Sequence ID if leaf, or cluster name
    double height{0.0};          // Node height in ultrametric tree
    size_t clade_size{1};        // Number of leaves in this subtree
    bool is_leaf{true};

    std::unique_ptr<GuideTreeNode> left;
    std::unique_ptr<GuideTreeNode> right;

    GuideTreeNode() = default;
};

class GuideTree {
public:
    GuideTree() = default;
    explicit GuideTree(std::unique_ptr<GuideTreeNode> root, size_t num_leaves);

    [[nodiscard]] const GuideTreeNode* root() const noexcept { return root_.get(); }
    [[nodiscard]] size_t numLeaves() const noexcept { return num_leaves_; }
    [[nodiscard]] bool empty() const noexcept { return root_ == nullptr; }

    // Traversal helpers
    void postOrderTraversal(const std::function<void(const GuideTreeNode&)>& visitor) const;

    // Progressive Multiple Sequence Alignment using bottom-up ProfileAligner
    [[nodiscard]] core::Profile progressiveAlign(
        const std::vector<core::Sequence>& sequences,
        const core::ScoreModel& model = core::ScoreModel(),
        const core::Blosum62& matrix = core::Blosum62::instance()
    ) const;

private:
    std::unique_ptr<GuideTreeNode> root_;
    size_t num_leaves_{0};
};

} // namespace msa::tree

#endif // MSA_TREE_GUIDE_TREE_HPP
