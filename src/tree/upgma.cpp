#include "msa/tree/upgma.hpp"

#include <vector>
#include <memory>
#include <cmath>
#include <algorithm>
#include <stdexcept>

namespace msa::tree {

GuideTree UPGMA::buildTree(
    const DistanceMatrix& dist_matrix,
    const std::vector<std::string>& sequence_names
) {
    size_t n = sequence_names.size();
    if (n == 0) {
        return GuideTree(nullptr, 0);
    }
    if (n == 1) {
        auto leaf = std::make_unique<GuideTreeNode>();
        leaf->id = 0;
        leaf->sequence_index = 0;
        leaf->name = sequence_names[0];
        leaf->height = 0.0;
        leaf->clade_size = 1;
        leaf->is_leaf = true;
        return GuideTree(std::move(leaf), 1);
    }

    // Active nodes representing clusters
    std::vector<std::unique_ptr<GuideTreeNode>> active_nodes;
    active_nodes.reserve(n);

    for (size_t i = 0; i < n; ++i) {
        auto leaf = std::make_unique<GuideTreeNode>();
        leaf->id = static_cast<int>(i);
        leaf->sequence_index = static_cast<int>(i);
        leaf->name = sequence_names[i];
        leaf->height = 0.0;
        leaf->clade_size = 1;
        leaf->is_leaf = true;
        active_nodes.push_back(std::move(leaf));
    }

    // Working distance table (K x K)
    std::vector<std::vector<double>> dist_table(n, std::vector<double>(n, 0.0));
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = 0; j < n; ++j) {
            dist_table[i][j] = dist_matrix.get(i, j);
        }
    }

    int next_id = static_cast<int>(n);

    // Agglomerative clustering: N - 1 merge steps
    for (size_t step = 0; step < n - 1; ++step) {
        size_t k = active_nodes.size();
        double min_d = 1e18;
        size_t best_u = 0;
        size_t best_v = 1;

        // Find closest pair (u, v) with deterministic tie-breaking (lowest indices)
        for (size_t i = 0; i < k; ++i) {
            for (size_t j = i + 1; j < k; ++j) {
                double d = dist_table[i][j];
                if (d < min_d - 1e-12) {
                    min_d = d;
                    best_u = i;
                    best_v = j;
                } else if (std::abs(d - min_d) <= 1e-12) {
                    if (i < best_u || (i == best_u && j < best_v)) {
                        best_u = i;
                        best_v = j;
                    }
                }
            }
        }

        double size_u = static_cast<double>(active_nodes[best_u]->clade_size);
        double size_v = static_cast<double>(active_nodes[best_v]->clade_size);
        double total_size = size_u + size_v;

        // Create new merged internal node
        auto parent = std::make_unique<GuideTreeNode>();
        parent->id = next_id++;
        parent->height = 0.5 * min_d;
        parent->clade_size = active_nodes[best_u]->clade_size + active_nodes[best_v]->clade_size;
        parent->is_leaf = false;
        parent->name = "Clade_" + std::to_string(parent->id);
        parent->left = std::move(active_nodes[best_u]);
        parent->right = std::move(active_nodes[best_v]);

        // Calculate updated arithmetic mean distances to other active clusters
        std::vector<double> updated_dist(k, 0.0);
        for (size_t w = 0; w < k; ++w) {
            if (w != best_u && w != best_v) {
                updated_dist[w] = (size_u * dist_table[best_u][w] + size_v * dist_table[best_v][w]) / total_size;
            }
        }

        // Update row and column best_u with new cluster distances
        for (size_t w = 0; w < k; ++w) {
            if (w != best_u && w != best_v) {
                dist_table[best_u][w] = updated_dist[w];
                dist_table[w][best_u] = updated_dist[w];
            }
        }
        dist_table[best_u][best_u] = 0.0;

        // Replace best_u with parent node
        active_nodes[best_u] = std::move(parent);

        // Erase cluster best_v from active_nodes and distance table
        active_nodes.erase(active_nodes.begin() + static_cast<ptrdiff_t>(best_v));
        dist_table.erase(dist_table.begin() + static_cast<ptrdiff_t>(best_v));
        for (auto& row : dist_table) {
            row.erase(row.begin() + static_cast<ptrdiff_t>(best_v));
        }
    }

    return GuideTree(std::move(active_nodes[0]), n);
}

GuideTree UPGMA::buildTree(
    const std::vector<core::Sequence>& sequences,
    const core::ScoreModel& model,
    const core::Blosum62& matrix,
    bool parallel
) {
    auto dist_matrix = DistanceMatrix::compute(sequences, model, matrix, parallel);
    std::vector<std::string> names;
    names.reserve(sequences.size());
    for (const auto& s : sequences) {
        names.push_back(s.id());
    }
    return buildTree(dist_matrix, names);
}

} // namespace msa::tree
