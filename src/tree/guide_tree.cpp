#include "msa/tree/guide_tree.hpp"
#include "msa/align/profile_aligner.hpp"

#include <stdexcept>

namespace msa::tree {

GuideTree::GuideTree(std::unique_ptr<GuideTreeNode> root, size_t num_leaves)
    : root_(std::move(root)), num_leaves_(num_leaves) {}

void GuideTree::postOrderTraversal(const std::function<void(const GuideTreeNode&)>& visitor) const {
    if (!root_) return;

    std::function<void(const GuideTreeNode*)> traverse = [&](const GuideTreeNode* node) {
        if (!node) return;
        if (node->left) traverse(node->left.get());
        if (node->right) traverse(node->right.get());
        visitor(*node);
    };

    traverse(root_.get());
}

core::Profile GuideTree::progressiveAlign(
    const std::vector<core::Sequence>& sequences,
    const core::ScoreModel& model,
    const core::Blosum62& matrix
) const {
    if (!root_) return core::Profile();

    align::ProfileAligner aligner(model, matrix);

    std::function<core::Profile(const GuideTreeNode*)> recurse = [&](const GuideTreeNode* node) -> core::Profile {
        if (!node) return core::Profile();

        if (node->is_leaf) {
            if (node->sequence_index >= 0 && static_cast<size_t>(node->sequence_index) < sequences.size()) {
                return core::Profile(sequences[static_cast<size_t>(node->sequence_index)]);
            }
            throw std::runtime_error("Invalid leaf sequence index in GuideTree");
        }

        auto left_prof = recurse(node->left.get());
        auto right_prof = recurse(node->right.get());
        return aligner.align(left_prof, right_prof);
    };

    return recurse(root_.get());
}

} // namespace msa::tree
