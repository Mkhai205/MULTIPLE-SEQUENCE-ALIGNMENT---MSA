#include "msa/eval/benchmark.hpp"
#include "msa/tree/distance_matrix.hpp"
#include "msa/tree/upgma.hpp"
#include "msa/tree/guide_tree.hpp"
#include "msa/parallel/tree_scheduler.hpp"

#include <chrono>
#include <sstream>
#include <iomanip>
#include <numeric>
#include <algorithm>

#if defined(_OPENMP)
#include <omp.h>
#endif

namespace msa::eval {

std::string BenchmarkReport::toMarkdownTable() const {
    std::ostringstream oss;
    oss << "### Benchmark Report: " << dataset_name << "\n";
    oss << "- Sequences: " << num_sequences << "\n";
    oss << "- Average Length: " << avg_sequence_length << " aa\n\n";

    oss << "| Threads | Time (ms) | Speedup $S(p)$ | Efficiency $E(p)$ | Peak Mem (MB) | SP Score | TC Score |\n";
    oss << "|:-------:|:---------:|:--------------:|:-----------------:|:-------------:|:--------:|:--------:|\n";

    for (const auto& r : results) {
        double mem_mb = static_cast<double>(r.peak_memory_bytes) / (1024.0 * 1024.0);
        oss << "| " << std::setw(7) << r.num_threads << " | "
            << std::fixed << std::setprecision(2) << std::setw(9) << r.runtime_ms << " | "
            << std::setprecision(2) << std::setw(14) << r.speedup << "x | "
            << std::setprecision(1) << std::setw(15) << (r.efficiency * 100.0) << "% | "
            << std::setprecision(2) << std::setw(13) << mem_mb << " | "
            << std::setprecision(4) << std::setw(8) << r.sp_result.score << " | "
            << std::setprecision(4) << std::setw(8) << r.tc_result.score << " |\n";
    }

    return oss.str();
}

std::string BenchmarkReport::toJson() const {
    std::ostringstream oss;
    oss << "{\n";
    oss << "  \"dataset_name\": \"" << dataset_name << "\",\n";
    oss << "  \"num_sequences\": " << num_sequences << ",\n";
    oss << "  \"avg_sequence_length\": " << avg_sequence_length << ",\n";
    oss << "  \"results\": [\n";

    for (size_t i = 0; i < results.size(); ++i) {
        const auto& r = results[i];
        oss << "    {\n";
        oss << "      \"threads\": " << r.num_threads << ",\n";
        oss << "      \"runtime_ms\": " << r.runtime_ms << ",\n";
        oss << "      \"speedup\": " << r.speedup << ",\n";
        oss << "      \"efficiency\": " << r.efficiency << ",\n";
        oss << "      \"peak_memory_bytes\": " << r.peak_memory_bytes << ",\n";
        oss << "      \"sp_score\": " << r.sp_result.score << ",\n";
        oss << "      \"tc_score\": " << r.tc_result.score << "\n";
        oss << "    }" << (i + 1 < results.size() ? "," : "") << "\n";
    }

    oss << "  ]\n";
    oss << "}\n";
    return oss.str();
}

BenchmarkReport BenchmarkRunner::run(
    const std::string& dataset_name,
    const std::vector<core::Sequence>& sequences,
    const BenchmarkConfig& config,
    const BalibaseReference* reference
) {
    BenchmarkReport report;
    report.dataset_name = dataset_name;
    report.num_sequences = sequences.size();

    if (sequences.empty()) {
        return report;
    }

    size_t total_len = 0;
    for (const auto& s : sequences) total_len += s.length();
    report.avg_sequence_length = total_len / sequences.size();

    std::vector<std::string> names;
    names.reserve(sequences.size());
    for (const auto& s : sequences) names.push_back(s.id());

    const auto& matrix = core::Blosum62::instance();
    double baseline_ms = 0.0;

    for (int threads : config.thread_counts) {
        ThreadBenchmarkResult tr;
        tr.num_threads = threads;

#if defined(_OPENMP)
        omp_set_num_threads(threads);
#endif

        std::vector<double> run_times;
        core::Profile final_profile;
        size_t peak_mem = 0;

        int reps = std::max(1, config.repetitions);
        for (int rep = 0; rep < reps; ++rep) {
            MemoryTracker::Scope mem_scope;
            auto start = std::chrono::high_resolution_clock::now();

            bool parallel = (threads > 1);
            auto dist = tree::DistanceMatrix::compute(sequences, config.model, matrix, parallel);
            auto tree = tree::UPGMA::buildTree(dist, names);

            if (parallel) {
                final_profile = parallel::parallel_progressive_align(tree, sequences, config.model, matrix, 4);
            } else {
                final_profile = tree.progressiveAlign(sequences, config.model, matrix);
            }

            auto end = std::chrono::high_resolution_clock::now();
            double ms = std::chrono::duration<double, std::milli>(end - start).count();
            run_times.push_back(ms);

            peak_mem = std::max(peak_mem, mem_scope.peakBytes());
        }

        double avg_ms = std::accumulate(run_times.begin(), run_times.end(), 0.0) / static_cast<double>(run_times.size());
        tr.runtime_ms = avg_ms;
        tr.peak_memory_bytes = peak_mem;

        if (threads == 1 || baseline_ms == 0.0) {
            baseline_ms = avg_ms;
            tr.speedup = 1.0;
            tr.efficiency = 1.0;
        } else {
            tr.speedup = (avg_ms > 0.0) ? (baseline_ms / avg_ms) : 1.0;
            tr.efficiency = tr.speedup / static_cast<double>(threads);
        }

        if (reference && config.evaluate_accuracy) {
            tr.sp_result = SPScore::compute(*reference, final_profile, true);
            tr.tc_result = TCScore::compute(*reference, final_profile, true);
        }

        report.results.push_back(tr);
    }

    return report;
}

BenchmarkReport BenchmarkRunner::runBalibase(
    const BalibaseReference& reference,
    const BenchmarkConfig& config
) {
    auto raw_seqs = reference.extractRawSequences();
    return run(reference.id.empty() ? "BAliBASE_Benchmark" : reference.id, raw_seqs, config, &reference);
}

} // namespace msa::eval
