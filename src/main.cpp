#include "msa/io/cli_parser.hpp"
#include "msa/io/fasta_io.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/profile.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/align/needleman_wunsch.hpp"
#include "msa/align/hirschberg.hpp"
#include "msa/tree/distance_matrix.hpp"
#include "msa/tree/upgma.hpp"
#include "msa/tree/guide_tree.hpp"
#include "msa/parallel/tree_scheduler.hpp"
#include "msa/eval/memory_tracker.hpp"
#include "msa/eval/balibase_parser.hpp"
#include "msa/eval/sp_score.hpp"
#include "msa/eval/tc_score.hpp"
#include "msa/eval/benchmark.hpp"

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <iomanip>
#include <memory>

#if defined(_OPENMP)
#include <omp.h>
#endif

int main(int argc, char* argv[]) {
    try {
        msa::io::CliParser parser;
        auto config = parser.parse(argc, argv, true);

        if (config.show_help) {
            std::cout << parser.format_help() << "\n";
            return 0;
        }

        if (config.show_version) {
            std::cout << parser.format_version() << "\n";
            return 0;
        }

        if (config.input_file.empty()) {
            std::cerr << "Error: No input file specified.\n";
            std::cerr << "Run 'msa_align --help' for usage options.\n";
            return 1;
        }

        std::cout << "============================================================\n";
        std::cout << "  Multiple Sequence Alignment (MSA) C++17 Pipeline\n";
        std::cout << "  Divide-and-Conquer Linear-Space with OpenMP Concurrency\n";
        std::cout << "============================================================\n";

        // 1. Load Sequences (auto-detect MSF or FASTA)
        std::vector<msa::core::Sequence> sequences;
        std::unique_ptr<msa::eval::BalibaseReference> balibase_ref;

        std::string ext = config.input_file.extension().string();
        for (char& c : ext) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));

        if (ext == ".msf") {
            auto ref = msa::eval::BalibaseParser::parseMSF(config.input_file);
            sequences = ref.extractRawSequences();
            balibase_ref = std::make_unique<msa::eval::BalibaseReference>(std::move(ref));
        } else {
            // Default to FASTA parser
            msa::io::FastaParser::Options fasta_opt;
            fasta_opt.mode = msa::io::ValidationMode::PERMISSIVE;
            sequences = msa::io::FastaParser::read_file(config.input_file, fasta_opt);
        }

        if (sequences.empty()) {
            std::cerr << "Error: Input file contains no sequences: " << config.input_file << "\n";
            return 1;
        }

        std::cout << "[INFO] Loaded " << sequences.size() << " sequences from "
                  << config.input_file.filename().string() << "\n";

        msa::core::ScoreModel score_model(config.gap_open, config.gap_extend);
        const auto& matrix = msa::core::Blosum62::instance();

        // 2. Baseline Comparison Mode
        if (config.baseline_compare) {
            std::cout << "\n--- Baseline Comparison: Gotoh NW (O(mn)) vs Myers-Miller Linear (O(min(m,n))) ---\n";
            if (sequences.size() < 2) {
                std::cout << "[WARN] At least 2 sequences required for pairwise baseline comparison.\n";
            } else {
                const auto& s1 = sequences[0];
                const auto& s2 = sequences[1];

                msa::align::NeedlemanWunsch nw(score_model, matrix);
                msa::align::HirschbergAligner hb(score_model, matrix);

                auto t0_nw = std::chrono::high_resolution_clock::now();
                auto res_nw = nw.align(s1, s2);
                auto t1_nw = std::chrono::high_resolution_clock::now();

                auto t0_hb = std::chrono::high_resolution_clock::now();
                auto res_hb = hb.align(s1, s2);
                auto t1_hb = std::chrono::high_resolution_clock::now();

                double ms_nw = std::chrono::duration<double, std::milli>(t1_nw - t0_nw).count();
                double ms_hb = std::chrono::duration<double, std::milli>(t1_hb - t0_hb).count();

                std::cout << "Pair: " << s1.id() << " (" << s1.length() << " aa) vs "
                          << s2.id() << " (" << s2.length() << " aa)\n";
                std::cout << "  Gotoh NW Score:       " << res_nw.score << " (Time: " << ms_nw
                          << " ms, Peak Mem: " << res_nw.peak_memory_bytes << " B)\n";
                std::cout << "  Myers-Miller Score:   " << res_hb.score << " (Time: " << ms_hb
                          << " ms, Peak Mem: " << res_hb.peak_memory_bytes << " B)\n";
                std::cout << "  Score Identity:       " << (res_nw.score == res_hb.score ? "MATCH (100% IDENTICAL)" : "MISMATCH") << "\n";
                if (res_hb.peak_memory_bytes > 0) {
                    double mem_ratio = static_cast<double>(res_nw.peak_memory_bytes) / static_cast<double>(res_hb.peak_memory_bytes);
                    std::cout << "  Memory Reduction:     " << std::fixed << std::setprecision(1) << mem_ratio << "x less memory\n";
                }
            }
        }

        // 3. Benchmark Mode
        if (config.benchmark) {
            std::cout << "\n--- Multi-Threaded Scalability & Accuracy Benchmark ---\n";
            msa::eval::BenchmarkConfig bench_config;
            bench_config.thread_counts = {1, 2, 4, 8};
            bench_config.model = score_model;
            bench_config.repetitions = 2;

            msa::eval::BenchmarkReport report;
            if (balibase_ref) {
                report = msa::eval::BenchmarkRunner::runBalibase(*balibase_ref, bench_config);
            } else {
                report = msa::eval::BenchmarkRunner::run(config.input_file.stem().string(), sequences, bench_config);
            }

            std::cout << "\n" << report.toMarkdownTable() << "\n";

            if (!config.output_file.empty()) {
                std::filesystem::path json_out = config.output_file;
                json_out.replace_extension(".json");
                std::ofstream ofs(json_out);
                if (ofs.is_open()) {
                    ofs << report.toJson();
                    std::cout << "[INFO] Benchmark JSON report saved to: " << json_out << "\n";
                }
            }
            return 0;
        }

        // 4. Standard Progressive Multiple Sequence Alignment Execution
        std::cout << "\n[INFO] Running Progressive Alignment with " << config.num_threads << " thread(s)...\n";
#if defined(_OPENMP)
        omp_set_num_threads(config.num_threads);
#endif

        msa::eval::MemoryTracker::Scope mem_scope;
        auto start_time = std::chrono::high_resolution_clock::now();

        // Step 4.1: Pairwise Distance Matrix
        bool parallel = (config.num_threads > 1);
        auto dist = msa::tree::DistanceMatrix::compute(sequences, score_model, matrix, parallel);

        // Step 4.2: UPGMA Guide Tree
        std::vector<std::string> names;
        names.reserve(sequences.size());
        for (const auto& s : sequences) names.push_back(s.id());
        auto guide_tree = msa::tree::UPGMA::buildTree(dist, names);

        if (!config.export_tree_file.empty()) {
            std::filesystem::path json_path = config.export_tree_file;
            json_path.replace_extension(".json");
            std::filesystem::path nwk_path = config.export_tree_file;
            nwk_path.replace_extension(".nwk");

            guide_tree.writeJson(json_path);
            guide_tree.writeNewick(nwk_path);

            std::cout << "[INFO] Guide tree exported to: " << json_path << " and " << nwk_path << "\n";
        }

        // Step 4.3: Bottom-up Progressive Alignment
        msa::core::Profile msa_profile;
        if (parallel) {
            msa_profile = msa::parallel::parallel_progressive_align(guide_tree, sequences, score_model, matrix, 4);
        } else {
            msa_profile = guide_tree.progressiveAlign(sequences, score_model, matrix);
        }

        auto end_time = std::chrono::high_resolution_clock::now();
        double elapsed_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();
        size_t peak_mem_bytes = mem_scope.peakBytes();
        double peak_mem_mb = static_cast<double>(peak_mem_bytes) / (1024.0 * 1024.0);

        std::cout << "[SUCCESS] Multiple Alignment Completed!\n";
        std::cout << "  - Number of sequences: " << msa_profile.numSequences() << "\n";
        std::cout << "  - Alignment length:    " << msa_profile.length() << " columns\n";
        std::cout << "  - Execution time:      " << std::fixed << std::setprecision(2) << elapsed_ms << " ms\n";
        std::cout << "  - Peak Working Set:    " << std::fixed << std::setprecision(2) << peak_mem_mb << " MB\n";

        // Step 4.4: Evaluate biological accuracy against reference if available
        if (balibase_ref) {
            auto sp_res = msa::eval::SPScore::compute(*balibase_ref, msa_profile, true);
            auto tc_res = msa::eval::TCScore::compute(*balibase_ref, msa_profile, true);
            std::cout << "  - BAliBASE SP Score:   " << std::fixed << std::setprecision(4) << sp_res.score
                      << " (" << sp_res.correct_pairs << " / " << sp_res.total_ref_pairs << " pairs)\n";
            std::cout << "  - BAliBASE TC Score:   " << std::fixed << std::setprecision(4) << tc_res.score
                      << " (" << tc_res.correct_columns << " / " << tc_res.total_ref_columns << " columns)\n";
        }

        // 5. Output Results
        std::vector<msa::core::Sequence> aligned_seqs;
        aligned_seqs.reserve(msa_profile.numSequences());
        for (size_t i = 0; i < msa_profile.numSequences(); ++i) {
            aligned_seqs.emplace_back(msa_profile.getSequenceId(i), msa_profile.getAlignedSequence(i));
        }

        if (!config.output_file.empty()) {
            msa::io::FastaWriter::write_file(config.output_file, aligned_seqs);
            std::cout << "[INFO] Aligned FASTA written to: " << config.output_file << "\n";
        } else {
            std::cout << "\n--- Aligned Sequences (FASTA) ---\n";
            for (const auto& s : aligned_seqs) {
                std::cout << ">" << s.id() << "\n" << s.seq() << "\n";
            }
        }

        return 0;
    } catch (const msa::io::CliParseException& e) {
        std::cerr << e.what() << "\n";
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "[Fatal Error] " << e.what() << "\n";
        return 1;
    }
}
