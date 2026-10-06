#include "msa/tree/distance_matrix.hpp"
#include "msa/align/needleman_wunsch.hpp"

#include <stdexcept>
#include <algorithm>
#include <vector>

#if defined(_OPENMP)
#include <omp.h>
#endif

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
    bool parallel
) {
    size_t n = sequences.size();
    DistanceMatrix dist(n);

    if (n == 0) return dist;

    std::vector<int> self_scores(n, 0);

#if defined(_OPENMP)
    if (parallel) {
        // Parallel self-alignment scores S(i, i)
        #pragma omp parallel for schedule(dynamic, 1)
        for (int i = 0; i < static_cast<int>(n); ++i) {
            align::NeedlemanWunsch aligner(model, matrix);
            self_scores[static_cast<size_t>(i)] = aligner.align(sequences[static_cast<size_t>(i)], sequences[static_cast<size_t>(i)]).score;
            dist.set(static_cast<size_t>(i), static_cast<size_t>(i), 0.0);
        }

        // Generate pairwise indices
        struct PairIdx { size_t i; size_t j; };
        std::vector<PairIdx> pairs;
        pairs.reserve(n * (n - 1) / 2);
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = i + 1; j < n; ++j) {
                pairs.push_back({i, j});
            }
        }

        int total_pairs = static_cast<int>(pairs.size());
        #pragma omp parallel for schedule(dynamic, 1)
        for (int p = 0; p < total_pairs; ++p) {
            size_t i = pairs[static_cast<size_t>(p)].i;
            size_t j = pairs[static_cast<size_t>(p)].j;
            align::NeedlemanWunsch aligner(model, matrix);
            auto res = aligner.align(sequences[i], sequences[j]);
            double d = computeNormalizedDistance(res.score, self_scores[i], self_scores[j]);
            dist.set(i, j, d);
        }

        return dist;
    }
#endif

    // Sequential fallback
    align::NeedlemanWunsch aligner(model, matrix);

    // 1. Calculate self-alignment scores S(i, i)
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
