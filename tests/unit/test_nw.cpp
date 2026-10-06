#include "test_framework.hpp"
#include "msa/align/needleman_wunsch.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/blosum62.hpp"

#include <string>
#include <vector>
#include <random>
#include <algorithm>
#include <stdexcept>

namespace {

// Helper to strip gap characters and verify residue conservation
bool verifyResidueConservation(std::string_view raw, std::string_view aligned) {
    std::string stripped;
    stripped.reserve(aligned.size());
    for (char c : aligned) {
        if (c != '-') stripped.push_back(c);
    }
    return stripped == raw;
}

// Helper to ensure no column contains dual gaps ('-' in both)
bool verifyNoDualGaps(std::string_view s1, std::string_view s2) {
    if (s1.length() != s2.length()) return false;
    for (size_t k = 0; k < s1.length(); ++k) {
        if (s1[k] == '-' && s2[k] == '-') return false;
    }
    return true;
}

} // anonymous namespace

// =============================================================================
// Needleman-Wunsch Unit Tests
// =============================================================================

TEST_CASE("NeedlemanWunsch - Identical Sequences") {
    using namespace msa::align;
    using namespace msa::core;

    std::string seq = "HEAGAWGHEE";
    auto res = needleman_wunsch_align(seq, seq);

    const auto& matrix = Blosum62::instance();
    int expected_score = 0;
    for (char c : seq) expected_score += matrix.score(c, c);

    CHECK_EQ(res.score, expected_score);
    CHECK_EQ(res.aligned_seq1, seq);
    CHECK_EQ(res.aligned_seq2, seq);
    CHECK(verifyResidueConservation(seq, res.aligned_seq1));
    CHECK(verifyResidueConservation(seq, res.aligned_seq2));
    CHECK(verifyNoDualGaps(res.aligned_seq1, res.aligned_seq2));
}

TEST_CASE("NeedlemanWunsch - Single Mismatch") {
    using namespace msa::align;

    std::string s1 = "HEAGAWGHEE";
    std::string s2 = "HEAGVWGHEE"; // A -> V at index 4
    auto res = needleman_wunsch_align(s1, s2);

    CHECK_EQ(res.aligned_seq1.length(), 10ULL);
    CHECK_EQ(res.aligned_seq2.length(), 10ULL);
    CHECK_EQ(res.aligned_seq1.find('-'), std::string::npos);
    CHECK_EQ(res.aligned_seq2.find('-'), std::string::npos);
    CHECK(verifyResidueConservation(s1, res.aligned_seq1));
    CHECK(verifyResidueConservation(s2, res.aligned_seq2));
}

TEST_CASE("NeedlemanWunsch - Single Indel") {
    using namespace msa::align;

    std::string s1 = "HEAGAWGHEE";
    std::string s2 = "HEAGWGHEE"; // Missing 'A'
    auto res = needleman_wunsch_align(s1, s2);

    CHECK_EQ(res.aligned_seq1.length(), 10ULL);
    CHECK_EQ(res.aligned_seq2.length(), 10ULL);
    CHECK_NE(res.aligned_seq2.find('-'), std::string::npos);
    CHECK(verifyResidueConservation(s1, res.aligned_seq1));
    CHECK(verifyResidueConservation(s2, res.aligned_seq2));
    CHECK(verifyNoDualGaps(res.aligned_seq1, res.aligned_seq2));
}

TEST_CASE("NeedlemanWunsch - Boundary Conditions (A vs AAA)") {
    using namespace msa::align;

    std::string s1 = "A";
    std::string s2 = "AAA";
    auto res = needleman_wunsch_align(s1, s2);

    // Matches 'A' with 'A' (score 4) and 2 gaps in seq1 (-10 + 1 * (-1) = -11)
    // Total score = 4 + (-11) = -7
    CHECK_EQ(res.score, -7);
    CHECK_EQ(res.aligned_seq1.length(), 3ULL);
    CHECK_EQ(res.aligned_seq2.length(), 3ULL);
    CHECK(verifyResidueConservation(s1, res.aligned_seq1));
    CHECK(verifyResidueConservation(s2, res.aligned_seq2));
    CHECK(verifyNoDualGaps(res.aligned_seq1, res.aligned_seq2));
}

TEST_CASE("NeedlemanWunsch - 1x1 Match and Mismatch") {
    using namespace msa::align;

    auto res_match = needleman_wunsch_align("W", "W");
    CHECK_EQ(res_match.score, 11);
    CHECK_EQ(res_match.aligned_seq1, "W");
    CHECK_EQ(res_match.aligned_seq2, "W");

    auto res_mismatch = needleman_wunsch_align("W", "D");
    CHECK_EQ(res_mismatch.score, -4);
    CHECK_EQ(res_mismatch.aligned_seq1, "W");
    CHECK_EQ(res_mismatch.aligned_seq2, "D");
}

TEST_CASE("NeedlemanWunsch - Drastic Length Asymmetry (1 vs 100)") {
    using namespace msa::align;

    std::string s1 = "W";
    std::string s2(100, 'W');
    auto res = needleman_wunsch_align(s1, s2);

    CHECK_EQ(res.aligned_seq1.length(), 100ULL);
    CHECK_EQ(res.aligned_seq2.length(), 100ULL);
    CHECK(verifyResidueConservation(s1, res.aligned_seq1));
    CHECK(verifyResidueConservation(s2, res.aligned_seq2));
    CHECK(verifyNoDualGaps(res.aligned_seq1, res.aligned_seq2));
}

TEST_CASE("NeedlemanWunsch - Completely Disjoint Sequences") {
    using namespace msa::align;

    std::string s1 = "AAAA";
    std::string s2 = "WWWW";
    auto res = needleman_wunsch_align(s1, s2);

    CHECK_EQ(res.aligned_seq1.length(), res.aligned_seq2.length());
    CHECK(verifyResidueConservation(s1, res.aligned_seq1));
    CHECK(verifyResidueConservation(s2, res.aligned_seq2));
    CHECK(verifyNoDualGaps(res.aligned_seq1, res.aligned_seq2));
}

TEST_CASE("NeedlemanWunsch - Homopolymer Gap Consolidation") {
    using namespace msa::align;

    std::string s1 = "AAAAA";
    std::string s2 = "AAA";
    auto res = needleman_wunsch_align(s1, s2);

    CHECK_EQ(res.aligned_seq1.length(), 5ULL);
    CHECK_EQ(res.aligned_seq2.length(), 5ULL);
    int gaps = 0;
    for (char c : res.aligned_seq2) if (c == '-') gaps++;
    CHECK_EQ(gaps, 2);
    CHECK(verifyResidueConservation(s1, res.aligned_seq1));
    CHECK(verifyResidueConservation(s2, res.aligned_seq2));
}

TEST_CASE("NeedlemanWunsch - Ambiguity and Extended Residues") {
    using namespace msa::align;

    std::string s = "BZXUOJ*";
    auto res = needleman_wunsch_align(s, s);

    CHECK_EQ(res.aligned_seq1, s);
    CHECK_EQ(res.aligned_seq2, s);
    CHECK(res.score > 0);
}

TEST_CASE("NeedlemanWunsch - Empty Sequence Exception") {
    using namespace msa::align;

    CHECK_THROWS_AS(needleman_wunsch_align("", "ACD"), std::invalid_argument);
    CHECK_THROWS_AS(needleman_wunsch_align("ACD", ""), std::invalid_argument);
    CHECK_THROWS_AS(needleman_wunsch_align("", ""), std::invalid_argument);
}

TEST_CASE("NeedlemanWunsch - Deterministic Repeatability") {
    using namespace msa::align;

    std::string s1 = "VLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGK";
    std::string s2 = "VHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKV";

    auto base = needleman_wunsch_align(s1, s2);

    for (int rep = 0; rep < 5; ++rep) {
        auto trial = needleman_wunsch_align(s1, s2);
        CHECK_EQ(trial.score, base.score);
        CHECK_EQ(trial.aligned_seq1, base.aligned_seq1);
        CHECK_EQ(trial.aligned_seq2, base.aligned_seq2);
        CHECK_EQ(trial.peak_memory_bytes, base.peak_memory_bytes);
    }
}

TEST_CASE("NeedlemanWunsch - Quadratic Memory Scaling") {
    using namespace msa::align;

    std::string s100(100, 'A');
    std::string s200(200, 'A');
    std::string s500(500, 'A');

    auto r100 = needleman_wunsch_align(s100, s100);
    auto r200 = needleman_wunsch_align(s200, s200);
    auto r500 = needleman_wunsch_align(s500, s500);

    // Cells: 3 * (len + 1)^2 * sizeof(int)
    // Ratio 200 / 100 should be approx (201/101)^2 = ~3.96
    double ratio_200_100 = static_cast<double>(r200.peak_memory_bytes) / static_cast<double>(r100.peak_memory_bytes);
    CHECK(ratio_200_100 > 3.8 && ratio_200_100 < 4.2);

    // Ratio 500 / 100 should be approx (501/101)^2 = ~24.6
    double ratio_500_100 = static_cast<double>(r500.peak_memory_bytes) / static_cast<double>(r100.peak_memory_bytes);
    CHECK(ratio_500_100 > 23.5 && ratio_500_100 < 25.8);
}

TEST_CASE("NeedlemanWunsch - 25 Diverse Random Sequence Pairs Validation") {
    using namespace msa::align;

    const std::string amino_acids = "ACDEFGHIKLMNPQRSTVWY";
    std::mt19937 rng(42);

    for (int test_idx = 0; test_idx < 25; ++test_idx) {
        int len1 = 20 + static_cast<int>(rng() % 80);
        int len2 = 20 + static_cast<int>(rng() % 80);

        std::string s1, s2;
        s1.reserve(len1);
        s2.reserve(len2);

        for (int i = 0; i < len1; ++i) s1.push_back(amino_acids[rng() % amino_acids.size()]);
        for (int j = 0; j < len2; ++j) s2.push_back(amino_acids[rng() % amino_acids.size()]);

        auto res = needleman_wunsch_align(s1, s2);

        // Invariants:
        CHECK_EQ(res.aligned_seq1.length(), res.aligned_seq2.length());
        CHECK(verifyResidueConservation(s1, res.aligned_seq1));
        CHECK(verifyResidueConservation(s2, res.aligned_seq2));
        CHECK(verifyNoDualGaps(res.aligned_seq1, res.aligned_seq2));
    }
}
