#ifndef MSA_TREE_DISTANCE_MATRIX_HPP
#define MSA_TREE_DISTANCE_MATRIX_HPP

#include "msa/core/sequence.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/core/score_model.hpp"

#include <vector>
#include <cstddef>
#include <string>

namespace msa::tree {

class DistanceMatrix {
public:
    DistanceMatrix() = default;
    explicit DistanceMatrix(size_t n);

    [[nodiscard]] size_t size() const noexcept { return size_; }

    [[nodiscard]] double get(size_t i, size_t j) const;
    void set(size_t i, size_t j, double val);

    [[nodiscard]] const std::vector<double>& rawData() const noexcept { return data_; }

    // Normalize distance formula: d = 1.0 - S(A,B) / max(S(A,A), S(B,B)), clamped to [0.0, 2.0]
    [[nodiscard]] static double computeNormalizedDistance(int s_ab, int s_aa, int s_bb) noexcept;

    // Compute full NxN distance matrix from input sequences
    [[nodiscard]] static DistanceMatrix compute(
        const std::vector<core::Sequence>& sequences,
        const core::ScoreModel& model = core::ScoreModel(),
        const core::Blosum62& matrix = core::Blosum62::instance(),
        bool parallel = false
    );

private:
    size_t size_{0};
    std::vector<double> data_; // 1D flat buffer of size N x N
};

} // namespace msa::tree

#endif // MSA_TREE_DISTANCE_MATRIX_HPP
