#include "msa/parallel/mpi_distance_matrix.hpp"
#include "msa/io/cli_parser.hpp"
#include "msa/io/fasta_io.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/tree/upgma.hpp"
#include "msa/tree/guide_tree.hpp"
#include "msa/parallel/tree_scheduler.hpp"
#include "msa/eval/balibase_parser.hpp"
#include "msa/eval/sp_score.hpp"
#include "msa/eval/tc_score.hpp"

#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <iomanip>

#if defined(USE_MPI)
#include <mpi.h>
#endif

#if defined(_OPENMP)
#include <omp.h>
#endif

int main(int argc, char* argv[]) {
#if !defined(USE_MPI)
    std::cerr << "[ERROR] msa_align_mpi was compiled without MPI support (-DUSE_MPI).\n";
    std::cerr << "Please build with MPI enabled: cmake -DENABLE_MPI=ON .. or use mpicxx.\n";
    return 1;
#else
    int provided = 0;
    MPI_Init_thread(&argc, &argv, MPI_THREAD_FUNNELED, &provided);

    int rank = 0;
    int num_procs = 1;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &num_procs);

    try {
        msa::io::CliParser parser("msa_align_mpi", "Hybrid MPI + OpenMP Distributed Multiple Sequence Alignment");
        auto config = parser.parse(argc, argv, rank == 0);

        if (config.show_help) {
            if (rank == 0) {
                std::cout << parser.format_help() << "\n";
            }
            MPI_Finalize();
            return 0;
        }

        if (config.show_version) {
            if (rank == 0) {
                std::cout << parser.format_version() << " (Hybrid MPI+OpenMP Build)\n";
            }
            MPI_Finalize();
            return 0;
        }

        if (config.input_file.empty()) {
            if (rank == 0) {
                std::cerr << "[ERROR] No input file specified. Run 'msa_align_mpi --help' for usage.\n";
            }
            MPI_Finalize();
            return 1;
        }

        if (rank == 0) {
            std::cout << "============================================================\n";
            std::cout << "  Hybrid MPI + OpenMP Distributed MSA Pipeline (Group 5)\n";
            std::cout << "  Distributed All-Pairs Distance Matrix on " << num_procs << " MPI node(s)\n";
#if defined(_OPENMP)
            std::cout << "  Internal Node Concurrency: " << config.num_threads << " OpenMP thread(s)/node\n";
#endif
            std::cout << "============================================================\n";
        }

        // Set OpenMP thread count
#if defined(_OPENMP)
        omp_set_num_threads(config.num_threads);
#endif

        // Load Sequences (all ranks load or master broadcasts)
        std::vector<msa::core::Sequence> sequences;
        std::string ext = config.input_file.extension().string();
        for (char& c : ext) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));

        if (ext == ".msf") {
            auto ref = msa::eval::BalibaseParser::parseMSF(config.input_file);
            sequences = ref.extractRawSequences();
        } else {
            msa::io::FastaParser::Options fasta_opt;
            fasta_opt.mode = msa::io::ValidationMode::PERMISSIVE;
            sequences = msa::io::FastaParser::read_file(config.input_file, fasta_opt);
        }

        if (sequences.empty()) {
            if (rank == 0) {
                std::cerr << "[ERROR] Input file contains no sequences.\n";
            }
            MPI_Finalize();
            return 1;
        }

        if (rank == 0) {
            std::cout << "[INFO] Loaded " << sequences.size() << " sequences. Starting distributed alignment...\n";
        }

        msa::core::ScoreModel score_model(config.gap_open, config.gap_extend);
        const auto& matrix = msa::core::Blosum62::instance();

        // 1. Synchronize and benchmark distributed distance matrix computation
        MPI_Barrier(MPI_COMM_WORLD);
        auto t_start = std::chrono::high_resolution_clock::now();

        auto dist = msa::parallel::MpiDistanceMatrix::computeDistributed(
            sequences, score_model, matrix, rank, num_procs
        );

        MPI_Barrier(MPI_COMM_WORLD);
        auto t_dist = std::chrono::high_resolution_clock::now();
        double dist_ms = std::chrono::duration<double, std::milli>(t_dist - t_start).count();

        if (rank == 0) {
            std::cout << "[SUCCESS] Distributed Distance Matrix completed in "
                      << std::fixed << std::setprecision(2) << dist_ms << " ms\n";

            // 2. Build UPGMA Guide Tree on Master
            std::vector<std::string> names;
            names.reserve(sequences.size());
            for (const auto& s : sequences) names.push_back(s.id());
            auto guide_tree = msa::tree::UPGMA::buildTree(dist, names);

            // 3. Progressive Alignment on Master
            msa::core::Profile msa_profile;
            if (config.num_threads > 1) {
                msa_profile = msa::parallel::parallel_progressive_align(
                    guide_tree, sequences, score_model, matrix, 4
                );
            } else {
                msa_profile = guide_tree.progressiveAlign(sequences, score_model, matrix);
            }

            auto t_end = std::chrono::high_resolution_clock::now();
            double total_ms = std::chrono::duration<double, std::milli>(t_end - t_start).count();

            std::cout << "[SUCCESS] Full MSA Completed!\n";
            std::cout << "  - Number of sequences: " << msa_profile.numSequences() << "\n";
            std::cout << "  - Alignment length:    " << msa_profile.length() << " cols\n";
            std::cout << "  - Total runtime:       " << std::fixed << std::setprecision(2) << total_ms << " ms\n";

            // 4. Output results
            std::vector<msa::core::Sequence> aligned_seqs;
            aligned_seqs.reserve(msa_profile.numSequences());
            for (size_t i = 0; i < msa_profile.numSequences(); ++i) {
                aligned_seqs.emplace_back(msa_profile.getSequenceId(i), msa_profile.getAlignedSequence(i));
            }

            if (!config.output_file.empty()) {
                msa::io::FastaWriter::write_file(config.output_file, aligned_seqs);
                std::cout << "[INFO] Aligned FASTA written to: " << config.output_file << "\n";
            }
        }

        MPI_Finalize();
        return 0;
    } catch (const std::exception& e) {
        if (rank == 0) {
            std::cerr << "[MPI Fatal Error] " << e.what() << "\n";
        }
        MPI_Finalize();
        return 1;
    }
#endif
}
