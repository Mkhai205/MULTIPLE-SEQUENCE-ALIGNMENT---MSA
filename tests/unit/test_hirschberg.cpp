#include "test_framework.hpp"
#include "msa/align/hirschberg.hpp"
#include "msa/align/needleman_wunsch.hpp"
#include "msa/align/profile_aligner.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/profile.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/blosum62.hpp"

#include <string>
#include <vector>
#include <random>
#include <algorithm>

namespace {

bool verifyResidueConservation(std::string_view raw, std::string_view aligned) {
    std::string stripped;
    stripped.reserve(aligned.size());
    for (char c : aligned) {
        if (c != '-') stripped.push_back(c);
    }
    return stripped == raw;
}

bool verifyNoDualGaps(std::string_view s1, std::string_view s2) {
    if (s1.length() != s2.length()) return false;
    for (size_t k = 0; k < s1.length(); ++k) {
        if (s1[k] == '-' && s2[k] == '-') return false;
    }
    return true;
}

} // anonymous namespace

// =============================================================================
// Hirschberg Linear-Space Aligner Tests
// =============================================================================

TEST_CASE("Hirschberg - Identical Sequences Match NW") {
    using namespace msa::align;

    std::string seq = "HEAGAWGHEE";
    auto nw_res = needleman_wunsch_align(seq, seq);
    auto h_res = hirschberg_align(seq, seq);

    CHECK_EQ(h_res.score, nw_res.score);
    CHECK_EQ(h_res.aligned_seq1, seq);
    CHECK_EQ(h_res.aligned_seq2, seq);
    CHECK(verifyResidueConservation(seq, h_res.aligned_seq1));
    CHECK(verifyResidueConservation(seq, h_res.aligned_seq2));
}

TEST_CASE("Hirschberg - Single Mismatch Match NW") {
    using namespace msa::align;

    std::string s1 = "HEAGAWGHEE";
    std::string s2 = "HEAGVWGHEE";
    auto nw_res = needleman_wunsch_align(s1, s2);
    auto h_res = hirschberg_align(s1, s2);

    CHECK_EQ(h_res.score, nw_res.score);
    CHECK_EQ(h_res.aligned_seq1.length(), 10ULL);
    CHECK_EQ(h_res.aligned_seq2.length(), 10ULL);
    CHECK(verifyResidueConservation(s1, h_res.aligned_seq1));
    CHECK(verifyResidueConservation(s2, h_res.aligned_seq2));
}

TEST_CASE("Hirschberg - Single Indel Match NW") {
    using namespace msa::align;

    std::string s1 = "HEAGAWGHEE";
    std::string s2 = "HEAGWGHEE";
    auto nw_res = needleman_wunsch_align(s1, s2);
    auto h_res = hirschberg_align(s1, s2);

    CHECK_EQ(h_res.score, nw_res.score);
    CHECK_EQ(h_res.aligned_seq1.length(), 10ULL);
    CHECK_EQ(h_res.aligned_seq2.length(), 10ULL);
    CHECK(verifyResidueConservation(s1, h_res.aligned_seq1));
    CHECK(verifyResidueConservation(s2, h_res.aligned_seq2));
    CHECK(verifyNoDualGaps(h_res.aligned_seq1, h_res.aligned_seq2));
}

TEST_CASE("Hirschberg - Boundary Conditions (A vs AAA)") {
    using namespace msa::align;

    std::string s1 = "A";
    std::string s2 = "AAA";
    auto nw_res = needleman_wunsch_align(s1, s2);
    auto h_res = hirschberg_align(s1, s2);

    CHECK_EQ(h_res.score, nw_res.score);
    CHECK_EQ(h_res.score, -7);
    CHECK_EQ(h_res.aligned_seq1.length(), 3ULL);
    CHECK_EQ(h_res.aligned_seq2.length(), 3ULL);
}

TEST_CASE("Hirschberg - 1x1 Match and Mismatch") {
    using namespace msa::align;

    auto r_match = hirschberg_align("W", "W");
    CHECK_EQ(r_match.score, 11);
    CHECK_EQ(r_match.aligned_seq1, "W");
    CHECK_EQ(r_match.aligned_seq2, "W");

    auto r_mismatch = hirschberg_align("W", "D");
    CHECK_EQ(r_mismatch.score, -4);
    CHECK_EQ(r_mismatch.aligned_seq1, "W");
    CHECK_EQ(r_mismatch.aligned_seq2, "D");
}

TEST_CASE("Hirschberg - 25 Diverse Random Sequence Pairs Exact Score Parity with NW") {
    using namespace msa::align;

    const std::string amino_acids = "ACDEFGHIKLMNPQRSTVWY";
    std::mt19937 rng(12345);

    for (int t = 0; t < 25; ++t) {
        int len1 = 20 + static_cast<int>(rng() % 60);
        int len2 = 20 + static_cast<int>(rng() % 60);

        std::string s1, s2;
        s1.reserve(len1);
        s2.reserve(len2);

        for (int i = 0; i < len1; ++i) s1.push_back(amino_acids[rng() % amino_acids.size()]);
        for (int j = 0; j < len2; ++j) s2.push_back(amino_acids[rng() % amino_acids.size()]);

        auto nw_res = needleman_wunsch_align(s1, s2);
        auto h_res = hirschberg_align(s1, s2);

        // Score must match Needleman-Wunsch identically!
        CHECK_EQ(h_res.score, nw_res.score);
        CHECK_EQ(h_res.aligned_seq1.length(), h_res.aligned_seq2.length());
        CHECK(verifyResidueConservation(s1, h_res.aligned_seq1));
        CHECK(verifyResidueConservation(s2, h_res.aligned_seq2));
        CHECK(verifyNoDualGaps(h_res.aligned_seq1, h_res.aligned_seq2));
    }
}

TEST_CASE("Hirschberg - Linear Memory Bound <= 5 * min(m, n) * sizeof(int)") {
    using namespace msa::align;

    std::string s500_a(500, 'A');
    std::string s500_b(500, 'W');

    auto nw_res = needleman_wunsch_align(s500_a, s500_b);
    auto h_res = hirschberg_align(s500_a, s500_b);

    size_t allowed_bytes = 5ULL * 500 * sizeof(int); // 10,000 bytes
    CHECK(h_res.peak_memory_bytes <= allowed_bytes);

    // NW quadratic memory should be over 3 MB
    CHECK(nw_res.peak_memory_bytes > 3'000'000ULL);

    // Memory reduction ratio should be > 250x
    double reduction_ratio = static_cast<double>(nw_res.peak_memory_bytes) / static_cast<double>(h_res.peak_memory_bytes);
    CHECK(reduction_ratio > 250.0);
}

TEST_CASE("Hirschberg - Profile-to-Profile Alignment and Merging") {
    using namespace msa::align;
    using namespace msa::core;

    std::vector<std::string> ids1 = {"p1_a", "p1_b"};
    std::vector<std::string> seqs1 = {"HEAGAWGHEE", "HEAGVWGHEE"};
    Profile p1(ids1, seqs1);

    std::vector<std::string> ids2 = {"p2_a", "p2_b"};
    std::vector<std::string> seqs2 = {"HEAG-WGHEE", "PAWHEAE---"};
    Profile p2(ids2, seqs2);

    ProfileAligner aligner;
    Profile merged = aligner.align(p1, p2);

    // Merged profile must contain all 4 sequences
    CHECK_EQ(merged.numSequences(), 4ULL);
    CHECK(merged.length() >= 10ULL);

    // All sequences in merged profile must have equal length
    for (size_t i = 0; i < merged.numSequences(); ++i) {
        CHECK_EQ(merged.getAlignedSequence(i).length(), merged.length());
    }

    // Sequence IDs preserved
    CHECK_EQ(merged.getSequenceId(0), "p1_a");
    CHECK_EQ(merged.getSequenceId(1), "p1_b");
    CHECK_EQ(merged.getSequenceId(2), "p2_a");
    CHECK_EQ(merged.getSequenceId(3), "p2_b");
}
