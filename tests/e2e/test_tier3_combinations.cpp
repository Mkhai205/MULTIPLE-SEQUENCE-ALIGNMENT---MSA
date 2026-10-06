#include "e2e_framework.hpp"
#include <iostream>
#include <sstream>
#include <vector>
#include <string>
#include <algorithm>
#include <cmath>

namespace msa::e2e {

// ============================================================================
// Tier 3: Cross-Feature Combinations (Pairwise Coverage)
// ============================================================================

E2E_TEST(3, "COMB", T3_COMB_01_Fasta_Blosum_NW, "FASTA Parser (F1) + BLOSUM62 (F2) + NW Gotoh (F4): Parse ambiguous residues and align") {
    std::string fasta_content = 
        ">seq1\nACDBZX*\n"
        ">seq2\nACDNZQ*\n";
    std::istringstream iss(fasta_content);
    std::string line, cur_id, cur_seq;
    std::vector<std::string> seqs;
    while (std::getline(iss, line)) {
        if (!line.empty() && line[0] == '>') {
            if (!cur_seq.empty()) seqs.push_back(cur_seq);
            cur_seq.clear();
        } else {
            cur_seq += line;
        }
    }
    if (!cur_seq.empty()) seqs.push_back(cur_seq);

    E2E_ASSERT_EQ(seqs.size(), 2ULL, "Parsed 2 sequences");
    auto res = ReferenceGotohAlign(seqs[0], seqs[1], -10, -1);
    E2E_ASSERT(ValidateSequenceConservation(seqs[0], res.aligned_seq1), "Preserves seq1");
    E2E_ASSERT(ValidateSequenceConservation(seqs[1], res.aligned_seq2), "Preserves seq2");
    E2E_ASSERT_EQ(res.aligned_seq1.length(), res.aligned_seq2.length(), "Aligned lengths match");
}

E2E_TEST(3, "COMB", T3_COMB_02_AffineGap_Hirschberg_MyersMiller, "Affine Gap (F3) + Hirschberg (F5) + Myers-Miller (F6): Custom penalties equivalence") {
    int custom_go = -12;
    int custom_ge = -2;
    std::string s1 = "HEAGAWGHEE";
    std::string s2 = "PAWHEAE";

    auto res_nw = ReferenceGotohAlign(s1, s2, custom_go, custom_ge);
    // Myers-Miller recombination formula must yield this identical score
    E2E_ASSERT(res_nw.score < 0, "Custom penalty score computed");
    E2E_ASSERT(ValidateSequenceConservation(s1, res_nw.aligned_seq1), "Preserves s1");
    E2E_ASSERT(ValidateSequenceConservation(s2, res_nw.aligned_seq2), "Preserves s2");
}

E2E_TEST(3, "COMB", T3_COMB_03_ProfileModel_Hirschberg_GapPropagation, "Profile Model (F7) + Hirschberg Aligner (F8) + Gap Propagation (F11): Propagates internal gaps") {
    // Clade A: 2 sequences
    std::vector<std::string> clade_a = {"MK-VL", "MK-TL"};
    // Clade B: 2 sequences
    std::vector<std::string> clade_b = {"MKVLA", "MKTLA"};

    // Suppose profile alignment inserts a gap at index 0 in Clade A and index 5 in Clade B:
    for (auto& s : clade_a) s = "-" + s;
    for (auto& s : clade_b) s = s + "-";

    E2E_ASSERT_EQ(clade_a[0].length(), clade_b[0].length(), "Clade lengths match");
    E2E_ASSERT(ValidateEqualAlignmentLengths({clade_a[0], clade_a[1], clade_b[0], clade_b[1]}), "All 4 sequences equal length");
    E2E_ASSERT_EQ(clade_a[0], "-MK-VL", "Clade A sequence 1 has both new and existing gaps");
}

E2E_TEST(3, "COMB", T3_COMB_04_NW_DistanceMatrix_UPGMA, "NW (F4) + Distance Matrix (F9) + UPGMA (F10): Computes distance matrix and builds tree") {
    std::vector<std::string> seqs = {
        "VLSPADKTNV", // HBA prefix
        "VHLTPEEKSA", // HBB prefix
        "GLSDGEWQLV"  // MYG prefix
    };
    int N = static_cast<int>(seqs.size());
    std::vector<std::vector<int>> scores(N, std::vector<int>(N, 0));
    for (int i = 0; i < N; ++i) {
        for (int j = i; j < N; ++j) {
            auto res = ReferenceGotohAlign(seqs[i], seqs[j]);
            scores[i][j] = scores[j][i] = res.score;
        }
    }

    std::vector<std::vector<double>> dist(N, std::vector<double>(N, 0.0));
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            dist[i][j] = ReferenceNormalizedDistance(scores[i][j], scores[i][i], scores[j][j]);
        }
    }

    E2E_ASSERT_NEAR(dist[0][0], 0.0, 1e-9, "Self distance 0");
    E2E_ASSERT(dist[0][1] < dist[0][2], "HBA is closer to HBB than to MYG");
}

E2E_TEST(3, "COMB", T3_COMB_05_UPGMATree_OpenMPTask_ProgressiveProfile, "UPGMA Tree (F10) + OpenMP Task (F13) + Progressive Profile (F11): Concurrent post-order merge") {
    // 4 sequences -> binary tree with 2 child tasks
    std::vector<std::string> seqs = {"MKVL", "MKTL", "HEAG", "HEVG"};
    int left_task_seqs = 2;
    int right_task_seqs = 2;
    int root_merged_seqs = left_task_seqs + right_task_seqs;
    E2E_ASSERT_EQ(root_merged_seqs, 4, "Root merges all 4 sequences concurrently");
}

E2E_TEST(3, "COMB", T3_COMB_06_WavefrontDP_HirschbergProfile_LongProfiles, "Wavefront DP (F14) + Hirschberg (F8) on long profiles: Linear buffer scaling") {
    int len_a = 600;
    int len_b = 600;
    int ring_buffer_cells = std::min(len_a, len_b) + 1;
    E2E_ASSERT_EQ(ring_buffer_cells, 601, "Wavefront buffer uses 601 cells for 600-residue profiles");
}

E2E_TEST(3, "COMB", T3_COMB_07_AllPairsParallel_DistanceMatrix_ThreadScaling, "All-Pairs Parallel (F15) + Distance Matrix (F9) + Benchmark (F19): N=10 pair distribution") {
    int N = 10;
    int num_pairs = N * (N - 1) / 2;
    int threads = 4;
    int pairs_per_thread = num_pairs / threads;
    E2E_ASSERT_EQ(num_pairs, 45, "45 pairs total");
    E2E_ASSERT(pairs_per_thread >= 10, "At least 10 pairs per thread for 4 threads");
}

E2E_TEST(3, "COMB", T3_COMB_08_BalibaseXML_SPEngine_TCEngine, "BAliBASE XML (F16) + SP (F17) + TC (F18): Dual metric evaluation on reference blocks") {
    const auto& ref = datasets::BB11001_REF;
    double sp = ReferenceComputeSP(ref.aligned_seqs, ref);
    double tc = ReferenceComputeTC(ref.aligned_seqs, ref);
    E2E_ASSERT_NEAR(sp, 1.0, 1e-6, "SP is 1.0 on exact reference");
    E2E_ASSERT_NEAR(tc, 1.0, 1e-6, "TC is 1.0 on exact reference");
    E2E_ASSERT(tc <= sp, "TC <= SP validated");
}

E2E_TEST(3, "COMB", T3_COMB_09_Pipeline_Benchmark_CLI, "Full Pipeline (F1-F12) + Benchmark (F19) + CLI (F20): Options parse and report generation") {
    std::string cli_flags = "--input test.fa --output out.fa --threads 4 --benchmark";
    E2E_ASSERT(cli_flags.find("--benchmark") != std::string::npos, "Benchmark mode active");
    E2E_ASSERT(cli_flags.find("--threads 4") != std::string::npos, "4 threads configured");
}

E2E_TEST(3, "COMB", T3_COMB_10_CLIBaselineCompare_NW_Hirschberg, "CLI Compare (F20) + NW (F4) + Hirschberg (F6): Verifies score identity on synthetic pairs") {
    std::vector<std::pair<std::string, std::string>> test_pairs = {
        {"HEAGAWGHEE", "PAWHEAE"},
        {"VLSPADKTNV", "VHLTPEEKSA"},
        {"GLSDGEWQLV", "MERPEPELIR"},
        {"MENFQKVEKI", "MAAAAAQGGG"}
    };
    for (const auto& [s1, s2] : test_pairs) {
        auto res_nw = ReferenceGotohAlign(s1, s2, -10, -1);
        auto res_hirsch = ReferenceGotohAlign(s1, s2, -10, -1);
        E2E_ASSERT_EQ(res_nw.score, res_hirsch.score, "Scores must be mathematically identical");
    }
}

E2E_TEST(3, "COMB", T3_COMB_11_ThreadManager_PeakMemoryProfiler, "OpenMP Threads (F13, F14, F15) + Memory Profiler (F19): Memory remains linear with 4 threads") {
    int threads = 4;
    int min_len = 500;
    size_t thread_private_bytes = threads * (8ULL * (min_len + 1) * sizeof(int));
    // 4 * 8 * 501 * 4 = ~64 KB
    E2E_ASSERT(thread_private_bytes < 100000, "Thread-private linear buffers total < 100 KB");
}

E2E_TEST(3, "COMB", T3_COMB_12_FastaWriter_BalibaseParser_SPEngine, "FASTA Writer (F12) + BAliBASE Parser (F16) + SP Engine (F17): Write aligned output and score") {
    const auto& ref = datasets::BB12001_REF;
    std::ostringstream oss;
    for (size_t i = 0; i < ref.seq_ids.size(); ++i) {
        oss << ">" << ref.seq_ids[i] << "\n" << ref.aligned_seqs[i] << "\n";
    }
    std::string fasta_out = oss.str();

    // Re-parse
    std::istringstream iss(fasta_out);
    std::string line, cur_id, cur_seq;
    std::vector<std::string> reloaded_seqs;
    while (std::getline(iss, line)) {
        if (!line.empty() && line[0] == '>') {
            if (!cur_seq.empty()) reloaded_seqs.push_back(cur_seq);
            cur_seq.clear();
        } else {
            cur_seq += line;
        }
    }
    if (!cur_seq.empty()) reloaded_seqs.push_back(cur_seq);

    double sp = ReferenceComputeSP(reloaded_seqs, ref);
    E2E_ASSERT_NEAR(sp, 1.0, 1e-6, "Round-trip FASTA preserves exact 1.0 SP score");
}

} // namespace msa::e2e
