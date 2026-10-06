#include "msa/tree/distance_matrix.hpp"
#include "msa/align/needleman_wunsch.hpp"

#include <stdexcept>
#include <algorithm>

namespace msa::tree {

DistanceMatrix::DistanceMatrix(size_t n)
    : size_(n), data_(n * n, 0.0) {}

double DistanceMatrix::get(size_t i, size_t j) const {
    if (i >= size_ || j >= size_) {
        throw std::out_of_range("DistanceMatrix indices out of range");
    }
    return data_[i * size_ + j];
}

void DistanceMatrix::set(size_t i, size_t j, double val) {
    if (i >= size_ || j >= size_) {
        throw std::out_of_range("DistanceMatrix indices out of range");
    }
    data_[i * size_ + j] = val;
    data_[j * size_ + i] = val;
}

double DistanceMatrix::computeNormalizedDistance(int s_ab, int s_aa, int s_bb) noexcept {
    int max_self = std::max(s_aa, s_bb);
    if (max_self <= 0) return 1.0;
    double d = 1.0 - (static_cast<double>(s_ab) / static_cast<double>(max_self));
    if (d < 0.0) d = 0.0;
    if (d > 2.0) d = 2.0;
    return d;
}

DistanceMatrix DistanceMatrix::compute(
    const std::vector<core::Sequence>& sequences,
    const core::ScoreModel& model,
    const core::Blosum62& matrix,
    bool /*parallel*/
) {
    size_t n = sequences.size();
    DistanceMatrix dist(n);

    if (n == 0) return dist;

    align::NeedlemanWunsch aligner(model, matrix);

    // 1. Calculate self-alignment scores S(i, i)
    std::vector<int> self_scores(n);
    for (size_t i = 0; i < n; ++i) {
        self_scores[i] = aligner.align(sequences[i], sequences[i]).score;
        dist.set(i, i, 0.0);
    }

    // 2. Calculate pairwise alignment scores S(i, j) for all i < j
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = i + 1; j < n; ++j) {
            auto res = aligner.align(sequences[i], sequences[j]);
            double d = computeNormalizedDistance(res.score, self_scores[i], self_scores[j]);
            dist.set(i, j, d);
        }
    }

    return dist;
}

} // namespace msa::tree
