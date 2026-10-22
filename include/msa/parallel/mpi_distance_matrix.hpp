#ifndef MSA_PARALLEL_MPI_DISTANCE_MATRIX_HPP
#define MSA_PARALLEL_MPI_DISTANCE_MATRIX_HPP

#include "msa/core/sequence.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/tree/distance_matrix.hpp"

#include <vector>
#include <utility>
#include <cstddef>

namespace msa::parallel {

/**
 * @brief Distributed All-Pairs Distance Matrix computation using MPI.
 *
 * Implements block-cyclic pair distribution across P processes:
 * For K sequences, there are M = K(K - 1) / 2 unique pairs.
 * Each MPI rank r evaluates pairs p where p % P == r.
 * Inside each rank, OpenMP threads can further parallelize computation (Hybrid MPI + OpenMP).
 * The full matrix is assembled via MPI_Allreduce or MPI_Reduce on Rank 0.
 */
class MpiDistanceMatrix {
public:
    /**
     * @brief Partition pairwise indices (i, j) with i < j deterministically among ranks.
     * @param num_sequences Total number of sequences K
     * @param rank MPI Rank of current process (0 <= rank < num_procs)
     * @param num_procs Total number of MPI ranks
     * @return List of (i, j) pairs assigned to this rank
     */
    [[nodiscard]] static std::vector<std::pair<size_t, size_t>> getAssignedPairs(
        size_t num_sequences,
        int rank,
        int num_procs
    ) noexcept;

    /**
     * @brief Compute the distributed distance matrix across all MPI processes.
     * @param sequences Vector of sequences
     * @param model Scoring parameters (gap open / extend)
     * @param matrix Substitution matrix (BLOSUM62)
     * @param rank MPI rank of current process
     * @param num_procs Total MPI processes
     * @return DistanceMatrix (assembled on all ranks if Allreduce, or on Rank 0 if Reduce)
     */
    [[nodiscard]] static tree::DistanceMatrix computeDistributed(
        const std::vector<core::Sequence>& sequences,
        const core::ScoreModel& model = core::ScoreModel(),
        const core::Blosum62& matrix = core::Blosum62::instance(),
        int rank = 0,
        int num_procs = 1
    );
};

} // namespace msa::parallel

#endif // MSA_PARALLEL_MPI_DISTANCE_MATRIX_HPP
