#include "msa/parallel/mpi_distance_matrix.hpp"
#include "msa/align/needleman_wunsch.hpp"

#if defined(USE_MPI)
#include <mpi.h>
#endif

#if defined(_OPENMP)
#include <omp.h>
#endif

#include <vector>
#include <algorithm>

namespace msa::parallel {

std::vector<std::pair<size_t, size_t>> MpiDistanceMatrix::getAssignedPairs(
    size_t num_sequences,
    int rank,
    int num_procs
) noexcept {
    std::vector<std::pair<size_t, size_t>> assigned;
    if (num_sequences < 2 || num_procs <= 0 || rank < 0 || rank >= num_procs) {
        return assigned;
    }

    size_t pair_idx = 0;
    for (size_t i = 0; i < num_sequences; ++i) {
        for (size_t j = i + 1; j < num_sequences; ++j) {
            if (static_cast<int>(pair_idx % static_cast<size_t>(num_procs)) == rank) {
                assigned.emplace_back(i, j);
            }
            ++pair_idx;
        }
    }
    return assigned;
}

tree::DistanceMatrix MpiDistanceMatrix::computeDistributed(
    const std::vector<core::Sequence>& sequences,
    const core::ScoreModel& model,
    const core::Blosum62& matrix,
    int rank,
    int num_procs
) {
    size_t n = sequences.size();
    tree::DistanceMatrix dist(n);

    if (n == 0) {
        return dist;
    }

#if defined(USE_MPI)
    if (num_procs > 1) {
        // 1. Calculate self-scores S(i, i) locally across all ranks
        std::vector<int> self_scores(n, 0);
        align::NeedlemanWunsch self_aligner(model, matrix);
        for (size_t i = 0; i < n; ++i) {
            self_scores[i] = self_aligner.align(sequences[i], sequences[i]).score;
        }

        // 2. Identify assigned pairs for this rank (Block-Cyclic distribution)
        auto assigned_pairs = getAssignedPairs(n, rank, num_procs);
        int num_assigned = static_cast<int>(assigned_pairs.size());

        // 3. Compute assigned pairwise alignments (with OpenMP concurrency inside rank)
        std::vector<double> local_matrix(n * n, 0.0);

#if defined(_OPENMP)
        #pragma omp parallel for schedule(dynamic, 1)
#endif
        for (int p = 0; p < num_assigned; ++p) {
            size_t i = assigned_pairs[static_cast<size_t>(p)].first;
            size_t j = assigned_pairs[static_cast<size_t>(p)].second;

            align::NeedlemanWunsch aligner(model, matrix);
            auto res = aligner.align(sequences[i], sequences[j]);
            double d = tree::DistanceMatrix::computeNormalizedDistance(res.score, self_scores[i], self_scores[j]);

            local_matrix[i * n + j] = d;
            local_matrix[j * n + i] = d;
        }

        // 4. Reduce all pairwise distances across MPI ranks using MPI_Allreduce
        std::vector<double> global_matrix(n * n, 0.0);
        MPI_Allreduce(
            local_matrix.data(),
            global_matrix.data(),
            static_cast<int>(n * n),
            MPI_DOUBLE,
            MPI_SUM,
            MPI_COMM_WORLD
        );

        // 5. Populate resulting DistanceMatrix
        for (size_t i = 0; i < n; ++i) {
            dist.set(i, i, 0.0);
            for (size_t j = i + 1; j < n; ++j) {
                dist.set(i, j, global_matrix[i * n + j]);
            }
        }

        return dist;
    }
#else
    (void)rank;
    (void)num_procs;
#endif

    // Fallback: Use standard OpenMP/Sequential DistanceMatrix computation
    return tree::DistanceMatrix::compute(sequences, model, matrix, true);
}

} // namespace msa::parallel
