#include "test_framework.hpp"
#include "msa/eval/memory_tracker.hpp"
#include "msa/eval/balibase_parser.hpp"
#include "msa/eval/sp_score.hpp"
#include "msa/eval/tc_score.hpp"
#include "msa/eval/benchmark.hpp"

#include <sstream>
#include <vector>
#include <string>

using namespace msa;

TEST_CASE("Eval - Memory Tracker Returns Valid System Metrics") {
    size_t current_mem = eval::MemoryTracker::getCurrentMemoryUsageBytes();
    size_t peak_mem = eval::MemoryTracker::getPeakMemoryUsageBytes();

    CHECK(current_mem > 0);
    CHECK(peak_mem > 0);
    CHECK(peak_mem >= current_mem);

    eval::MemoryTracker::Scope scope;
    CHECK(scope.initialBytes() > 0);
    CHECK(scope.peakBytes() >= scope.initialBytes());
}

TEST_CASE("Eval - Balibase MSF Parser and Core Block Detection") {
    std::string sample_msf =
        "PileUp\n\n"
        "  MSF: 30  Type: P    Check: 1000   ..\n\n"
        " Name: seq1  Len: 30  Check: 100  Weight: 1.00\n"
        " Name: seq2  Len: 30  Check: 200  Weight: 1.00\n"
        " Name: seq3  Len: 30  Check: 300  Weight: 1.00\n\n"
        "//\n\n"
        "seq1      aaHEAGAWGH EE--aaAAAA\n"
        "seq2      aaHEAGAWGH EE--aaAAAA\n"
        "seq3      aaHEAW..GH EE--aaAAAA\n";

    std::istringstream iss(sample_msf);
    auto ref = eval::BalibaseParser::parseMSF(iss, "test_dataset");

    CHECK_EQ(ref.id, "test_dataset");
    CHECK_EQ(ref.numSequences(), 3ULL);
    CHECK_EQ(ref.length(), 20ULL);
    CHECK_EQ(ref.sequence_ids[0], "seq1");
    CHECK_EQ(ref.sequence_ids[1], "seq2");
    CHECK_EQ(ref.sequence_ids[2], "seq3");

    // Standardized gaps: dots should be converted to '-'
    CHECK_EQ(ref.aligned_sequences[2], "aaHEAW--GHEE--aaAAAA");

    // Check core blocks: uppercase non-gap columns are detected as core
    CHECK(ref.numCoreColumns() > 0);

    auto raw = ref.extractRawSequences();
    CHECK_EQ(raw.size(), 3ULL);
    CHECK_EQ(raw[0].seq(), "AAHEAGAWGHEEAAAAAA");
    CHECK_EQ(raw[2].seq(), "AAHEAWGHEEAAAAAA");
}

TEST_CASE("Eval - Balibase FASTA Parser") {
    std::string sample_fasta =
        ">s1\n"
        "MKWVTFISLL--LFSS\n"
        ">s2\n"
        "MK-VTFISLL--LFSS\n";

    std::istringstream iss(sample_fasta);
    auto ref = eval::BalibaseParser::parseFASTA(iss, "fasta_dataset");

    CHECK_EQ(ref.numSequences(), 2ULL);
    CHECK_EQ(ref.length(), 16ULL);
    CHECK_EQ(ref.sequence_ids[0], "s1");
    CHECK_EQ(ref.sequence_ids[1], "s2");

    auto raw = ref.extractRawSequences();
    CHECK_EQ(raw[0].seq(), "MKWVTFISLLLFSS");
    CHECK_EQ(raw[1].seq(), "MKVTFISLLLFSS");
}

TEST_CASE("Eval - SP Score Identity and Degradation") {
    std::vector<std::string> ids = {"s1", "s2", "s3"};
    std::vector<std::string> ref_aligned = {
        "MKWVTFISLL",
        "MK-VTFISLL",
        "MKWVTF-SLL"
    };

    // Test with identical alignment -> SP = 1.0
    auto res_perfect = eval::SPScore::compute(ids, ref_aligned, ids, ref_aligned, {}, false);
    CHECK_NEAR(res_perfect.score, 1.0, 1e-9);
    CHECK_EQ(res_perfect.correct_pairs, res_perfect.total_ref_pairs);
    CHECK(res_perfect.total_ref_pairs > 0);

    // Test with completely shifted/perturbed alignment -> SP < 1.0
    std::vector<std::string> bad_aligned = {
        "--MKWVTFISLL",
        "MKVTFISLL---",
        "MK-W-V-T-FISLL"
    };
    auto res_bad = eval::SPScore::compute(ids, ref_aligned, ids, bad_aligned, {}, false);
    CHECK(res_bad.score < 1.0);
}

TEST_CASE("Eval - TC Score Identity and Misalignment Detection") {
    std::vector<std::string> ids = {"s1", "s2", "s3"};
    std::vector<std::string> ref_aligned = {
        "MKWVTFISLL",
        "MKWVTFISLL",
        "MKWVTFISLL"
    };

    // 100% concordance across all columns
    auto res_perfect = eval::TCScore::compute(ids, ref_aligned, ids, ref_aligned, {}, false);
    CHECK_NEAR(res_perfect.score, 1.0, 1e-9);
    CHECK_EQ(res_perfect.correct_columns, 10ULL);
    CHECK_EQ(res_perfect.total_ref_columns, 10ULL);

    // Shift one sequence by a gap in the middle -> TC decreases
    std::vector<std::string> test_shifted = {
        "MK-WVTFISLL",
        "MKWVTFISLL-",
        "MK-WVTFISLL"
    };
    auto res_shifted = eval::TCScore::compute(ids, ref_aligned, ids, test_shifted, {}, false);
    CHECK(res_shifted.score < 1.0);
}

TEST_CASE("Eval - Benchmark Runner End-to-End Execution") {
    std::vector<core::Sequence> seqs = {
        core::Sequence("p1", "HEAGAWGHEE"),
        core::Sequence("p2", "PAWHEAE"),
        core::Sequence("p3", "HEAWGHEE"),
        core::Sequence("p4", "PAWHE")
    };

    eval::BenchmarkConfig config;
    config.thread_counts = {1, 2};
    config.repetitions = 1;

    auto report = eval::BenchmarkRunner::run("SmallBenchmark", seqs, config);

    CHECK_EQ(report.num_sequences, 4ULL);
    CHECK_EQ(report.results.size(), 2ULL);
    CHECK_EQ(report.results[0].num_threads, 1);
    CHECK_EQ(report.results[1].num_threads, 2);
    CHECK(report.results[0].runtime_ms > 0.0);
    CHECK(report.results[1].runtime_ms > 0.0);
    CHECK_NEAR(report.results[0].speedup, 1.0, 1e-9);

    std::string md_table = report.toMarkdownTable();
    CHECK(md_table.find("SmallBenchmark") != std::string::npos);
    CHECK(md_table.find("Speedup") != std::string::npos);

    std::string json_str = report.toJson();
    CHECK(json_str.find("\"dataset_name\": \"SmallBenchmark\"") != std::string::npos);
}
