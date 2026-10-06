#ifndef MSA_EVAL_BENCHMARK_HPP
#define MSA_EVAL_BENCHMARK_HPP

#include "msa/eval/balibase_parser.hpp"
#include "msa/eval/sp_score.hpp"
#include "msa/eval/tc_score.hpp"
#include "msa/eval/memory_tracker.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/blosum62.hpp"

#include <vector>
#include <string>

namespace msa::eval {

struct ThreadBenchmarkResult {
    int num_threads{1};
    double runtime_ms{0.0};
    double speedup{1.0};
    double efficiency{1.0};
    size_t peak_memory_bytes{0};
    SPResult sp_result;
    TCResult tc_result;
};

struct BenchmarkConfig {
    std::vector<int> thread_counts{1, 2, 4};
    int repetitions{1};
    core::ScoreModel model{-10, -1};
    bool evaluate_accuracy{true};
};

struct BenchmarkReport {
    std::string dataset_name;
    size_t num_sequences{0};
    size_t avg_sequence_length{0};
    std::vector<ThreadBenchmarkResult> results;

    [[nodiscard]] std::string toMarkdownTable() const;
    [[nodiscard]] std::string toJson() const;
};

class BenchmarkRunner {
public:
    [[nodiscard]] static BenchmarkReport run(
        const std::string& dataset_name,
        const std::vector<core::Sequence>& sequences,
        const BenchmarkConfig& config = BenchmarkConfig(),
        const BalibaseReference* reference = nullptr
    );

    [[nodiscard]] static BenchmarkReport runBalibase(
        const BalibaseReference& reference,
        const BenchmarkConfig& config = BenchmarkConfig()
    );
};

} // namespace msa::eval

#endif // MSA_EVAL_BENCHMARK_HPP
