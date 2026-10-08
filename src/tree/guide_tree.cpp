#include "msa/tree/guide_tree.hpp"
#include "msa/align/profile_aligner.hpp"

#include <stdexcept>
#include <sstream>
#include <fstream>
#include <iomanip>
#include <algorithm>

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

std::string GuideTree::toNewick() const {
    if (!root_) return ";";

    std::function<std::string(const GuideTreeNode*, double)> build = [&](const GuideTreeNode* node, double parent_height) -> std::string {
        if (!node) return "";
        double branch_len = std::max(0.0, parent_height - node->height);
        std::ostringstream ss;
        ss << std::fixed << std::setprecision(4);
        if (node->is_leaf) {
            ss << node->name << ":" << branch_len;
        } else {
            ss << "(";
            if (node->left) ss << build(node->left.get(), node->height);
            if (node->left && node->right) ss << ",";
            if (node->right) ss << build(node->right.get(), node->height);
            ss << ")";
            if (node == root_.get()) {
                // Root node has no branch length
            } else {
                ss << ":" << branch_len;
            }
        }
        return ss.str();
    };

    return build(root_.get(), root_->height) + ";";
}

namespace {

std::string escapeJsonString(const std::string& input) {
    std::string out;
    out.reserve(input.size() + 8);
    for (char c : input) {
        switch (c) {
            case '"': out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\b': out += "\\b"; break;
            case '\f': out += "\\f"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:
                if (static_cast<unsigned char>(c) < 0x20) {
                    char buf[8];
                    std::snprintf(buf, sizeof(buf), "\\u%04x", static_cast<unsigned char>(c));
                    out += buf;
                } else {
                    out += c;
                }
                break;
        }
    }
    return out;
}

} // anonymous namespace

std::string GuideTree::toJson() const {
    if (!root_) return "{}";

    std::function<std::string(const GuideTreeNode*, double, int)> build = [&](const GuideTreeNode* node, double parent_height, int indent) -> std::string {
        if (!node) return "null";
        double branch_len = std::max(0.0, parent_height - node->height);
        std::string ind(indent * 2, ' ');
        std::string ind2((indent + 1) * 2, ' ');
        std::ostringstream ss;
        ss << "{\n";
        ss << ind2 << "\"id\": " << node->id << ",\n";
        ss << ind2 << "\"name\": \"" << escapeJsonString(node->name) << "\",\n";
        ss << ind2 << "\"height\": " << std::fixed << std::setprecision(6) << node->height << ",\n";
        ss << ind2 << "\"branch_length\": " << std::fixed << std::setprecision(6) << branch_len << ",\n";
        ss << ind2 << "\"clade_size\": " << node->clade_size << ",\n";
        ss << ind2 << "\"is_leaf\": " << (node->is_leaf ? "true" : "false");
        if (!node->is_leaf && (node->left || node->right)) {
            ss << ",\n" << ind2 << "\"children\": [\n";
            bool first = true;
            if (node->left) {
                ss << ind2 << "  " << build(node->left.get(), node->height, indent + 2);
                first = false;
            }
            if (node->right) {
                if (!first) ss << ",\n";
                ss << ind2 << "  " << build(node->right.get(), node->height, indent + 2);
            }
            ss << "\n" << ind2 << "]";
        }
        ss << "\n" << ind << "}";
        return ss.str();
    };

    return build(root_.get(), root_->height, 0);
}

void GuideTree::writeNewick(const std::filesystem::path& path) const {
    std::ofstream ofs(path);
    if (!ofs.is_open()) {
        throw std::runtime_error("Failed to open file for Newick export: " + path.string());
    }
    ofs << toNewick() << "\n";
}

void GuideTree::writeJson(const std::filesystem::path& path) const {
    std::ofstream ofs(path);
    if (!ofs.is_open()) {
        throw std::runtime_error("Failed to open file for JSON tree export: " + path.string());
    }
    ofs << toJson() << "\n";
}

} // namespace msa::tree
