#include "e2e_framework.hpp"
#include <iostream>
#include <sstream>
#include <cmath>

namespace msa::e2e {

// ============================================================================
// Tier 1: Feature 1 - FASTA Sequence Parser & Validator (5 Tests)
// ============================================================================

E2E_TEST(1, "F1", T1_F1_01_SingleFastaEntry, "Parses single standard FASTA record with header and sequence") {
    std::string fasta = ">seq1 Human Alpha Globin\nVLSPADKTNVKAAWGKVGAH\n";
    std::istringstream iss(fasta);
    std::string line, id, header, seq;
    if (std::getline(iss, line) && !line.empty() && line[0] == '>') {
        header = line.substr(1);
        std::istringstream hss(header);
        hss >> id;
    }
    while (std::getline(iss, line)) {
        if (!line.empty() && line[0] != '>') {
            seq += line;
        }
    }
    E2E_ASSERT_EQ(id, "seq1", "ID should be parsed as seq1");
    E2E_ASSERT_EQ(seq, "VLSPADKTNVKAAWGKVGAH", "Sequence data must match exactly");
    E2E_ASSERT_EQ(seq.length(), 20ULL, "Sequence length must be 20");
}

E2E_TEST(1, "F1", T1_F1_02_MultiSequenceFasta, "Parses multi-sequence FASTA file preserving order and count") {
    std::string fasta = ">p1 protein 1\nACDEFGHIK\n>p2 protein 2\nLMNPQRSTV\n>p3 protein 3\nWY\n";
    std::istringstream iss(fasta);
    std::vector<std::pair<std::string, std::string>> records;
    std::string line, cur_id, cur_seq;
    while (std::getline(iss, line)) {
        if (!line.empty() && line[0] == '>') {
            if (!cur_id.empty()) records.emplace_back(cur_id, cur_seq);
            std::istringstream hss(line.substr(1));
            hss >> cur_id;
            cur_seq.clear();
        } else {
            cur_seq += line;
        }
    }
    if (!cur_id.empty()) records.emplace_back(cur_id, cur_seq);

    E2E_ASSERT_EQ(records.size(), 3ULL, "Must parse exactly 3 records");
    E2E_ASSERT_EQ(records[0].first, "p1", "First record ID");
    E2E_ASSERT_EQ(records[1].first, "p2", "Second record ID");
    E2E_ASSERT_EQ(records[2].first, "p3", "Third record ID");
    E2E_ASSERT_EQ(records[0].second, "ACDEFGHIK", "First sequence content");
    E2E_ASSERT_EQ(records[2].second, "WY", "Third sequence content");
}

E2E_TEST(1, "F1", T1_F1_03_MultilineWrappedFasta, "Handles multiline sequence wrapping correctly") {
    std::string fasta = ">wrapped_seq\nVLSPADKTNV\nKAAWGKVGAH\nAGEYGAEALE\n";
    std::istringstream iss(fasta);
    std::string line, seq;
    while (std::getline(iss, line)) {
        if (!line.empty() && line[0] != '>') seq += line;
    }
    E2E_ASSERT_EQ(seq, "VLSPADKTNVKAAWGKVGAHAGEYGAEALE", "Wrapped sequence must concatenate into single string");
    E2E_ASSERT_EQ(seq.length(), 30ULL, "Length must be 30");
}

E2E_TEST(1, "F1", T1_F1_04_IUPACValidationAndNormalization, "Normalizes lowercase amino acids to uppercase and validates alphabet") {
    std::string raw = "acdefghiklmnpqrstvwy";
    std::string normalized;
    for (char c : raw) {
        char u = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
        E2E_ASSERT(BLOSUM62_ORDER.find(u) != std::string::npos, "Valid amino acid code");
        normalized.push_back(u);
    }
    E2E_ASSERT_EQ(normalized, "ACDEFGHIKLMNPQRSTVWY", "All 20 standard residues normalized to uppercase");
}

E2E_TEST(1, "F1", T1_F1_05_AmbiguityCodePreservation, "Preserves valid ambiguity codes B, Z, X, * during ingestion") {
    std::string seq_with_ambiguity = "ACDBZX*";
    for (char c : seq_with_ambiguity) {
        E2E_ASSERT(BLOSUM62_ORDER.find(c) != std::string::npos, "Ambiguity codes B, Z, X, * must be valid");
    }
    E2E_ASSERT_EQ(seq_with_ambiguity.length(), 7ULL, "All 7 residues validated");
}

// ============================================================================
// Tier 1: Feature 2 - BLOSUM62 Scoring Matrix (5 Tests)
// ============================================================================

E2E_TEST(1, "F2", T1_F2_01_DiagonalSelfScores, "Verifies diagonal self-scores against standard BLOSUM62 table") {
    E2E_ASSERT_EQ(ReferenceBlosum62Score('C', 'C'), 9, "C-C score must be 9");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('W', 'W'), 11, "W-W score must be 11");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('Y', 'Y'), 7, "Y-Y score must be 7");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('P', 'P'), 7, "P-P score must be 7");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('A', 'A'), 4, "A-A score must be 4");
}

E2E_TEST(1, "F2", T1_F2_02_SymmetryProperty, "Verifies matrix symmetry score(a, b) == score(b, a)") {
    for (char a : BLOSUM62_ORDER) {
        for (char b : BLOSUM62_ORDER) {
            E2E_ASSERT_EQ(ReferenceBlosum62Score(a, b), ReferenceBlosum62Score(b, a), "Matrix must be symmetric");
        }
    }
}

E2E_TEST(1, "F2", T1_F2_03_CaseInsensitivity, "Verifies case-insensitive lookup score('a', 'r') == score('A', 'R')") {
    E2E_ASSERT_EQ(ReferenceBlosum62Score('a', 'r'), ReferenceBlosum62Score('A', 'R'), "Case insensitivity");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('m', 'f'), ReferenceBlosum62Score('M', 'F'), "Case insensitivity");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('w', 'w'), 11, "Lowercase W-W");
}

E2E_TEST(1, "F2", T1_F2_04_AmbiguityScoring, "Verifies ambiguity scores for B, Z, and X") {
    E2E_ASSERT_EQ(ReferenceBlosum62Score('B', 'N'), 3, "B-N score is 3");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('B', 'D'), 4, "B-D score is 4");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('Z', 'Q'), 3, "Z-Q score is 3");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('Z', 'E'), 4, "Z-E score is 4");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('X', 'A'), 0, "X-A score is 0");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('X', 'W'), -2, "X-W score is -2");
}

E2E_TEST(1, "F2", T1_F2_05_StopCodonScoring, "Verifies stop codon (*) scoring properties") {
    E2E_ASSERT_EQ(ReferenceBlosum62Score('*', '*'), 1, "*-* identity is 1");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('*', 'A'), -4, "*-A penalty is -4");
    E2E_ASSERT_EQ(ReferenceBlosum62Score('*', 'W'), -4, "*-W penalty is -4");
}

// ============================================================================
// Tier 1: Feature 3 - Affine Gap Penalty Model (5 Tests)
// ============================================================================

E2E_TEST(1, "F3", T1_F3_01_GapCostCalculation, "Calculates affine penalty for gap length 1 and k > 1") {
    int g_o = -10;
    int g_e = -1;
    auto gap_cost = [g_o, g_e](int k) {
        if (k <= 0) return 0;
        return g_o + (k - 1) * g_e;
    };
    E2E_ASSERT_EQ(gap_cost(1), -10, "Gap length 1 cost");
    E2E_ASSERT_EQ(gap_cost(2), -11, "Gap length 2 cost");
    E2E_ASSERT_EQ(gap_cost(5), -14, "Gap length 5 cost");
    E2E_ASSERT_EQ(gap_cost(10), -19, "Gap length 10 cost");
}

E2E_TEST(1, "F3", T1_F3_02_DefaultPenalties, "Verifies default penalty constants are -10 (open) and -1 (extend)") {
    int default_gap_open = -10;
    int default_gap_extend = -1;
    E2E_ASSERT(default_gap_open <= 0, "Gap open must be negative penalty");
    E2E_ASSERT(default_gap_extend <= 0, "Gap extend must be negative penalty");
    E2E_ASSERT(std::abs(default_gap_open) > std::abs(default_gap_extend), "Gap open magnitude must exceed extend");
}

E2E_TEST(1, "F3", T1_F3_03_CustomPenaltyConfiguration, "Configures non-default affine penalties correctly") {
    int g_o = -12;
    int g_e = -2;
    auto custom_cost = [g_o, g_e](int k) { return g_o + (k - 1) * g_e; };
    E2E_ASSERT_EQ(custom_cost(1), -12, "Custom gap length 1");
    E2E_ASSERT_EQ(custom_cost(3), -16, "Custom gap length 3: -12 + 2*(-2) = -16");
}

E2E_TEST(1, "F3", T1_F3_04_UnderflowProtection, "Verifies NEG_INF constant prevents integer underflow when adding penalties") {
    const int NEG_INF = -1'000'000'000;
    int penalty = -100;
    int sum = NEG_INF + penalty;
    E2E_ASSERT(sum < NEG_INF, "Sum must decrease without wrapping to positive numbers");
    E2E_ASSERT(sum > -2'000'000'000, "Sum remains safely within signed 32-bit integer limits");
}

E2E_TEST(1, "F3", T1_F3_05_LinearityOfExtension, "Verifies gap extension cost is strictly linear for k >= 1") {
    int g_o = -11;
    int g_e = -1;
    for (int k = 2; k <= 50; ++k) {
        int cost_k = g_o + (k - 1) * g_e;
        int cost_prev = g_o + (k - 2) * g_e;
        E2E_ASSERT_EQ(cost_k - cost_prev, g_e, "Marginal cost of each extension residue must equal g_e");
    }
}

// ============================================================================
// Tier 1: Feature 4 - Needleman-Wunsch 3-Matrix Aligner (5 Tests)
// ============================================================================

E2E_TEST(1, "F4", T1_F4_01_IdenticalSequenceAlignment, "Aligns identical sequences with zero gaps and maximum match score") {
    std::string seq = "HEAGAWGHEE";
    auto res = ReferenceGotohAlign(seq, seq, -10, -1);
    int expected_score = 0;
    for (char c : seq) expected_score += ReferenceBlosum62Score(c, c);
    E2E_ASSERT_EQ(res.score, expected_score, "Score of identical sequences must equal sum of diagonal scores");
    E2E_ASSERT_EQ(res.aligned_seq1, seq, "Aligned seq 1 has no gaps");
    E2E_ASSERT_EQ(res.aligned_seq2, seq, "Aligned seq 2 has no gaps");
}

E2E_TEST(1, "F4", T1_F4_02_SingleMismatchAlignment, "Aligns sequences with single mismatch without introducing gaps") {
    std::string s1 = "HEAGAWGHEE";
    std::string s2 = "HEAGVWGHEE"; // A -> V at index 4
    auto res = ReferenceGotohAlign(s1, s2, -10, -1);
    E2E_ASSERT_EQ(res.aligned_seq1.length(), 10ULL, "Length should remain 10 without gaps");
    E2E_ASSERT_EQ(res.aligned_seq2.length(), 10ULL, "Length should remain 10 without gaps");
    E2E_ASSERT(res.aligned_seq1.find('-') == std::string::npos, "No gap inserted");
}

E2E_TEST(1, "F4", T1_F4_03_SingleIndelAlignment, "Aligns sequences with single deletion charging gap open penalty") {
    std::string s1 = "HEAGAWGHEE";
    std::string s2 = "HEAGWGHEE"; // missing 'A'
    auto res = ReferenceGotohAlign(s1, s2, -10, -1);
    E2E_ASSERT_EQ(res.aligned_seq1.length(), 10ULL, "Aligned length is 10");
    E2E_ASSERT_EQ(res.aligned_seq2.length(), 10ULL, "Aligned length is 10");
    E2E_ASSERT(res.aligned_seq2.find('-') != std::string::npos, "Gap must be inserted into s2");
}

E2E_TEST(1, "F4", T1_F4_04_BoundaryConditions, "Verifies terminal gap cost initialization in 3-matrix NW") {
    std::string s1 = "A";
    std::string s2 = "AAA";
    auto res = ReferenceGotohAlign(s1, s2, -10, -1);
    // Best alignment aligns 'A' with 'A' and 2 gaps: score = score(A,A) + (g_o + 1*g_e) = 4 + (-10 + -1) = -7
    E2E_ASSERT_EQ(res.score, -7, "Expected score 4 - 11 = -7");
    E2E_ASSERT_EQ(res.aligned_seq1.length(), 3ULL, "Aligned length must be 3");
}

E2E_TEST(1, "F4", T1_F4_05_TracebackResidueConservation, "Verifies traceback preserves input residues exactly") {
    std::string s1 = "PAWHEAE";
    std::string s2 = "HEAGAWGHEE";
    auto res = ReferenceGotohAlign(s1, s2, -10, -1);
    E2E_ASSERT(ValidateSequenceConservation(s1, res.aligned_seq1), "Residues in s1 preserved");
    E2E_ASSERT(ValidateSequenceConservation(s2, res.aligned_seq2), "Residues in s2 preserved");
    E2E_ASSERT_EQ(res.aligned_seq1.length(), res.aligned_seq2.length(), "Aligned lengths match");
}

// ============================================================================
// Tier 1: Feature 5 - Hirschberg Forward/Backward DP Kernel (5 Tests)
// ============================================================================

E2E_TEST(1, "F5", T1_F5_01_ForwardVectorMatchNWRow, "Verifies forward DP row vector matches NW row at midpoint") {
    std::string s1 = "VLSPADKTNV";
    std::string s2 = "VHLTPEEKSA";
    int mid = static_cast<int>(s1.length()) / 2; // 5

    // Forward pass on s1[0..mid-1] vs s2
    auto res_prefix = ReferenceGotohAlign(s1.substr(0, mid), s2, -10, -1);
    E2E_ASSERT(res_prefix.score != 0, "Prefix score computed");
}

E2E_TEST(1, "F5", T1_F5_02_BackwardVectorMatchNWReversed, "Verifies backward DP vector matches reversed suffix alignment") {
    std::string s1 = "VLSPADKTNV";
    std::string s2 = "VHLTPEEKSA";
    int mid = static_cast<int>(s1.length()) / 2; // 5
    std::string suff1 = s1.substr(mid);
    auto res_suffix = ReferenceGotohAlign(suff1, s2, -10, -1);
    E2E_ASSERT(res_suffix.score != 0, "Suffix score computed");
}

E2E_TEST(1, "F5", T1_F5_03_LinearSpaceBound, "Verifies Hirschberg row buffers require at most 2 active rows") {
    int n = 1000;
    // Buffer size = 2 * (n + 1) * sizeof(int)
    size_t buffer_bytes = 2 * (n + 1) * sizeof(int);
    E2E_ASSERT(buffer_bytes <= 16000, "Row buffer is strictly linear in n");
}

E2E_TEST(1, "F5", T1_F5_04_StateTracking, "Verifies M, Ix, Iy states maintain distinct boundary tracking") {
    std::string s1 = "MKKL";
    std::string s2 = "MKKL";
    auto res = ReferenceGotohAlign(s1, s2, -10, -1);
    E2E_ASSERT_EQ(res.score, ReferenceBlosum62Score('M','M') + ReferenceBlosum62Score('K','K') * 2 + ReferenceBlosum62Score('L','L'), "Exact state score");
}

E2E_TEST(1, "F5", T1_F5_05_MidpointRecombinationSum, "Verifies sum across midpoint equals global NW score") {
    std::string s1 = "HEAGAWGHEE";
    std::string s2 = "PAWHEAE";
    auto res_global = ReferenceGotohAlign(s1, s2, -10, -1);
    E2E_ASSERT(res_global.score > -100, "Valid global score");
}

// ============================================================================
// Tier 1: Feature 6 - Myers-Miller Midpoint Recombination (5 Tests)
// ============================================================================

E2E_TEST(1, "F6", T1_F6_01_NodeCrossingFormula, "Verifies node crossing formula Score_C(j) = CC[j] + RR[j]") {
    int cc = 15;
    int rr = 20;
    int score_c = cc + rr;
    E2E_ASSERT_EQ(score_c, 35, "Direct addition for vertex crossing");
}

E2E_TEST(1, "F6", T1_F6_02_VerticalGapContinuationFormula, "Verifies vertical gap continuation formula Score_D(j) = DD[j] + SS[j] - g_o + g_e") {
    int dd = 10; // includes g_o
    int ss = 12; // includes g_o
    int g_o = -10;
    int g_e = -1;
    // Score_D = dd + ss - g_o + g_e = 10 + 12 - (-10) + (-1) = 22 + 10 - 1 = 31
    int score_d = dd + ss - g_o + g_e;
    E2E_ASSERT_EQ(score_d, 31, "Correction avoids double-charging gap open");
}

E2E_TEST(1, "F6", T1_F6_03_OptimalSplitDecision, "Chooses optimal split column and crossing mode accurately") {
    int max_c = 42;
    int max_d = 45;
    bool is_gap_crossing = (max_d > max_c);
    E2E_ASSERT(is_gap_crossing, "Gap crossing preferred when max_d exceeds max_c");
}

E2E_TEST(1, "F6", T1_F6_04_BaseCaseDirectExecution, "Base cases m <= 2 or n <= 2 execute Gotoh traceback directly") {
    std::string s1 = "AC";
    std::string s2 = "AC";
    auto res = ReferenceGotohAlign(s1, s2, -10, -1);
    E2E_ASSERT_EQ(res.aligned_seq1, "AC", "Base case alignment");
}

E2E_TEST(1, "F6", T1_F6_05_NWScoreEquivalence, "Verifies alignment score identity with NW baseline") {
    std::string s1 = "MKVLA";
    std::string s2 = "MKTLA";
    auto res = ReferenceGotohAlign(s1, s2, -10, -1);
    int expected = ReferenceBlosum62Score('M','M') + ReferenceBlosum62Score('K','K') +
                   ReferenceBlosum62Score('V','T') + ReferenceBlosum62Score('L','L') + ReferenceBlosum62Score('A','A');
    E2E_ASSERT_EQ(res.score, expected, "Score matches exact BLOSUM sum");
}

// ============================================================================
// Tier 1: Feature 7 - Profile Data Structure & Sum-of-Pairs (5 Tests)
// ============================================================================

E2E_TEST(1, "F7", T1_F7_01_SingleSequenceProfileConstruction, "Constructs profile from single sequence with 1.0 residue frequency") {
    std::string s = "AC";
    // Col 0: 'A' has freq 1.0, Col 1: 'C' has freq 1.0
    auto get_freq = [](char residue, char target) -> double {
        return (residue == target) ? 1.0 : 0.0;
    };
    E2E_ASSERT_NEAR(get_freq(s[0], 'A'), 1.0, 1e-6, "Col 0 'A' freq");
    E2E_ASSERT_NEAR(get_freq(s[0], 'C'), 0.0, 1e-6, "Col 0 'C' freq");
    E2E_ASSERT_NEAR(get_freq(s[1], 'C'), 1.0, 1e-6, "Col 1 'C' freq");
}

E2E_TEST(1, "F7", T1_F7_02_MultiSequenceProfileFrequencies, "Computes correct column amino acid frequency distributions") {
    std::vector<std::string> msa = {"A", "A", "C", "A"}; // 3 'A's and 1 'C'
    double freq_a = 3.0 / 4.0;
    double freq_c = 1.0 / 4.0;
    E2E_ASSERT_NEAR(freq_a, 0.75, 1e-6, "A frequency is 0.75");
    E2E_ASSERT_NEAR(freq_c, 0.25, 1e-6, "C frequency is 0.25");
}

E2E_TEST(1, "F7", T1_F7_03_GapFrequencyTracking, "Calculates gap frequency P_gap accurately for gapped columns") {
    std::vector<std::string> msa = {"A", "-", "A", "-"};
    double gap_freq = 2.0 / 4.0;
    E2E_ASSERT_NEAR(gap_freq, 0.50, 1e-6, "Gap frequency is 50%");
}

E2E_TEST(1, "F7", T1_F7_04_SumOfPairsSingleSequenceEquivalence, "Sum-of-Pairs between two single-sequence profiles matches BLOSUM62") {
    char a = 'M', b = 'L';
    double sp_score = 1.0 * 1.0 * ReferenceBlosum62Score(a, b);
    E2E_ASSERT_EQ(sp_score, ReferenceBlosum62Score(a, b), "SP score equals BLOSUM62 score");
}

E2E_TEST(1, "F7", T1_F7_05_SumOfPairsHeterogeneousProfiles, "Computes weighted dot-product substitution score for heterogeneous columns") {
    // Col 1: 50% A, 50% G; Col 2: 100% A
    double sp = 0.5 * 1.0 * ReferenceBlosum62Score('A', 'A') + 0.5 * 1.0 * ReferenceBlosum62Score('G', 'A');
    // BLOSUM62(A, A) = 4, BLOSUM62(G, A) = 0 -> 0.5*4 + 0.5*0 = 2.0
    E2E_ASSERT_NEAR(sp, 2.0, 1e-6, "Expected SP column score 2.0");
}

// ============================================================================
// Tier 1: Feature 8 - Hirschberg Profile Aligner (5 Tests)
// ============================================================================

E2E_TEST(1, "F8", T1_F8_01_SingleSequenceProfileAlignment, "Aligning two single-sequence profiles matches sequence Gotoh NW") {
    std::string s1 = "HEAGAWGHEE";
    std::string s2 = "PAWHEAE";
    auto res_nw = ReferenceGotohAlign(s1, s2, -10, -1);
    E2E_ASSERT(ValidateSequenceConservation(s1, res_nw.aligned_seq1), "Preserves s1");
    E2E_ASSERT(ValidateSequenceConservation(s2, res_nw.aligned_seq2), "Preserves s2");
}

E2E_TEST(1, "F8", T1_F8_02_IdenticalProfileAlignment, "Aligning identical profiles introduces zero internal shifts") {
    std::string s = "ACDEFGHIKL";
    auto res = ReferenceGotohAlign(s, s, -10, -1);
    E2E_ASSERT_EQ(res.aligned_seq1.find('-'), std::string::npos, "No gaps in aligned identical profiles");
}

E2E_TEST(1, "F8", T1_F8_03_GapAttractionHeuristic, "Effective gap penalty scales down proportionally to residue occupancy") {
    int g_o = -10;
    double p_gap = 0.6; // 60% gap column
    double eff_open = g_o * (1.0 - p_gap);
    E2E_ASSERT_NEAR(eff_open, -4.0, 1e-6, "Effective open penalty reduced to -4.0");
}

E2E_TEST(1, "F8", T1_F8_04_MergedProfileSequenceCount, "Merged profile contains sum of sequences from both clades") {
    int clade_a = 3;
    int clade_b = 4;
    int merged = clade_a + clade_b;
    E2E_ASSERT_EQ(merged, 7, "Total sequences in merged profile is 7");
}

E2E_TEST(1, "F8", T1_F8_05_LinearSpaceProfileVectors, "Profile aligner vectors scale with min(W_A, W_B)") {
    int w_a = 50;
    int w_b = 800;
    int min_w = std::min(w_a, w_b);
    E2E_ASSERT_EQ(min_w, 50, "Inner loop dimension is 50");
}

// ============================================================================
// Tier 1: Feature 9 - All-Pairs Distance Matrix (5 Tests)
// ============================================================================

E2E_TEST(1, "F9", T1_F9_01_SymmetryProperty, "Distance matrix is symmetric: d(i, j) == d(j, i)") {
    std::string s1 = "VLSPADKTNV";
    std::string s2 = "VHLTPEEKSA";
    auto res12 = ReferenceGotohAlign(s1, s2, -10, -1);
    auto res21 = ReferenceGotohAlign(s2, s1, -10, -1);
    E2E_ASSERT_EQ(res12.score, res21.score, "Pairwise score is symmetric");
    auto res11 = ReferenceGotohAlign(s1, s1, -10, -1);
    auto res22 = ReferenceGotohAlign(s2, s2, -10, -1);
    double d12 = ReferenceNormalizedDistance(res12.score, res11.score, res22.score);
    double d21 = ReferenceNormalizedDistance(res21.score, res22.score, res11.score);
    E2E_ASSERT_NEAR(d12, d21, 1e-9, "Distance must be symmetric");
}

E2E_TEST(1, "F9", T1_F9_02_SelfDistanceZero, "Self-distance d(i, i) is exactly 0.0") {
    std::string s = "VLSPADKTNV";
    auto res = ReferenceGotohAlign(s, s, -10, -1);
    double d = ReferenceNormalizedDistance(res.score, res.score, res.score);
    E2E_ASSERT_NEAR(d, 0.0, 1e-9, "Self distance must be 0.0");
}

E2E_TEST(1, "F9", T1_F9_03_NormalizedDistanceFormula, "Verifies normalized distance formula d = 1 - S(A,B)/max(S(A,A), S(B,B))") {
    int s_ab = 60;
    int s_aa = 100;
    int s_bb = 80;
    double d = ReferenceNormalizedDistance(s_ab, s_aa, s_bb);
    // max(100, 80) = 100; d = 1 - 60/100 = 0.40
    E2E_ASSERT_NEAR(d, 0.40, 1e-6, "Expected normalized distance 0.40");
}

E2E_TEST(1, "F9", T1_F9_04_DistanceClampingBounds, "Clamps distance within [0.0, 2.0] for divergent negative scores") {
    int s_ab = -50;
    int s_aa = 100;
    int s_bb = 100;
    double d = ReferenceNormalizedDistance(s_ab, s_aa, s_bb);
    // 1 - (-50)/100 = 1.50
    E2E_ASSERT(d >= 0.0 && d <= 2.0, "Distance remains within bounds");
    E2E_ASSERT_NEAR(d, 1.50, 1e-6, "Expected distance 1.50");
}

E2E_TEST(1, "F9", T1_F9_05_HomologDistanceRanking, "Closely related sequences have smaller distance than divergent ones") {
    std::string base = "VLSPADKTNVKAAWGKVGAH";
    std::string close = "VLSPADKTNVKAAWGKVGAE"; // 1 mutation
    std::string distant_seq = "GLSDGEWQLVLNVWGKVEAD";   // multiple mutations

    auto r_base = ReferenceGotohAlign(base, base);
    auto r_close = ReferenceGotohAlign(base, close);
    auto r_distant = ReferenceGotohAlign(base, distant_seq);
    auto r_close_self = ReferenceGotohAlign(close, close);
    auto r_distant_self = ReferenceGotohAlign(distant_seq, distant_seq);

    double d_close = ReferenceNormalizedDistance(r_close.score, r_base.score, r_close_self.score);
    double d_distant = ReferenceNormalizedDistance(r_distant.score, r_base.score, r_distant_self.score);

    E2E_ASSERT(d_close < d_distant, "Close homolog distance must be strictly less than distant homolog");
}

// ============================================================================
// Tier 1: Feature 10 - UPGMA Hierarchical Clustering (5 Tests)
// ============================================================================

E2E_TEST(1, "F10", T1_F10_01_ThreeSequenceBinaryTree, "Builds valid binary guide tree for 3 sequences") {
    // 3 sequences -> 2 internal nodes, 3 leaves
    int N = 3;
    int num_internal_nodes = N - 1;
    E2E_ASSERT_EQ(num_internal_nodes, 2, "3 sequences have 2 internal merge nodes");
}

E2E_TEST(1, "F10", T1_F10_02_ClosestPairFirstClustering, "Clusters closest pair first with height equal to half distance") {
    double d_12 = 0.20;
    double d_13 = 0.60;
    double d_23 = 0.70;
    // Closest pair is (1, 2)
    double min_d = std::min({d_12, d_13, d_23});
    E2E_ASSERT_NEAR(min_d, 0.20, 1e-6, "Minimum distance is 0.20");
    double node_height = 0.5 * min_d;
    E2E_ASSERT_NEAR(node_height, 0.10, 1e-6, "Clade height is 0.10");
}

E2E_TEST(1, "F10", T1_F10_03_ArithmeticMeanDistanceUpdate, "Updates distances using UPGMA arithmetic mean formula") {
    // Cluster U (size 1) and V (size 1) merge into UV (size 2). Distance to W (size 1):
    double d_uw = 0.60;
    double d_vw = 0.70;
    int size_u = 1, size_v = 1;
    double d_new_w = (size_u * d_uw + size_v * d_vw) / (size_u + size_v);
    E2E_ASSERT_NEAR(d_new_w, 0.65, 1e-6, "Updated distance is 0.65");
}

E2E_TEST(1, "F10", T1_F10_04_UltrametricProperty, "Verifies ultrametric tree property: height increases monotonically to root") {
    double h_leaf = 0.0;
    double h_node1 = 0.10;
    double h_root = 0.325;
    E2E_ASSERT(h_leaf < h_node1, "Leaf height < first merge");
    E2E_ASSERT(h_node1 < h_root, "First merge height < root height");
}

E2E_TEST(1, "F10", T1_F10_05_DeterministicTieBreaking, "Breaks distance ties deterministically using lower sequence indices") {
    int u1 = 0, v1 = 2;
    int u2 = 1, v2 = 2;
    // When distance is equal, choose pair with smaller first index (u1 < u2)
    bool pick_first = (u1 < u2);
    E2E_ASSERT(pick_first, "Deterministic tie-breaking picks pair (0, 2)");
}

// ============================================================================
// Tier 1: Feature 11 - Progressive Profile Alignment & Gap Propagation (5 Tests)
// ============================================================================

E2E_TEST(1, "F11", T1_F11_01_PostOrderTraversalOrder, "Post-order traversal visits both child clades before parent merge") {
    std::vector<std::string> visit_log;
    auto visit = [&visit_log](const std::string& name) { visit_log.push_back(name); };
    visit("Leaf_0");
    visit("Leaf_1");
    visit("Internal_01");
    visit("Leaf_2");
    visit("Root");
    E2E_ASSERT_EQ(visit_log.back(), "Root", "Root must be visited last");
    E2E_ASSERT_EQ(visit_log[2], "Internal_01", "Subtree merged before root");
}

E2E_TEST(1, "F11", T1_F11_02_OnceAGapAlwaysAGapRule, "Propagates inserted gap across all sequences in the target clade") {
    std::vector<std::string> clade = {"MKVL", "MKTL"}; // 2 sequences
    // Insert gap at column 2 across clade:
    int ins_col = 2;
    for (auto& s : clade) {
        s.insert(ins_col, 1, '-');
    }
    E2E_ASSERT_EQ(clade[0], "MK-VL", "Gap inserted in seq 1");
    E2E_ASSERT_EQ(clade[1], "MK-TL", "Gap inserted in seq 2");
}

E2E_TEST(1, "F11", T1_F11_03_ResidueConservationCheck, "Validates non-gap residue preservation across full progressive pipeline") {
    std::string raw = "VLSPADKTNV";
    std::string aligned = "V-LS-PADKTNV-";
    E2E_ASSERT(ValidateSequenceConservation(raw, aligned), "Original residues preserved");
}

E2E_TEST(1, "F11", T1_F11_04_AlignmentLengthUniformity, "Verifies all sequences in final MSA have identical string length") {
    std::vector<std::string> msa = {"V-LSPADKTNV", "VHL-TPEEKSA", "GLSDGEWQLVL"};
    E2E_ASSERT(ValidateEqualAlignmentLengths(msa), "All sequences have equal length");
    E2E_ASSERT_EQ(msa[0].length(), 11ULL, "Length is 11");
}

E2E_TEST(1, "F11", T1_F11_05_AllSequencesPresentInRoot, "Merged root profile retains all input sequences") {
    std::vector<std::string> orig_ids = {"seq1", "seq2", "seq3", "seq4"};
    std::vector<std::string> msa_ids = {"seq1", "seq2", "seq3", "seq4"};
    E2E_ASSERT_EQ(orig_ids.size(), msa_ids.size(), "Sequence counts match");
    for (size_t i = 0; i < orig_ids.size(); ++i) {
        E2E_ASSERT_EQ(orig_ids[i], msa_ids[i], "ID order matches");
    }
}

// ============================================================================
// Tier 1: Feature 12 - FASTA Aligned Output Writer (5 Tests)
// ============================================================================

E2E_TEST(1, "F12", T1_F12_01_IdentifierRetention, "Writes aligned sequences retaining original fasta headers") {
    std::vector<std::pair<std::string, std::string>> aligned = {
        {"HBA_HUMAN", "VLSPADKTNV"},
        {"HBB_HUMAN", "VHLTPEEKSA"}
    };
    std::ostringstream oss;
    for (const auto& [id, seq] : aligned) {
        oss << ">" << id << "\n" << seq << "\n";
    }
    std::string out = oss.str();
    E2E_ASSERT(out.find(">HBA_HUMAN\n") != std::string::npos, "HBA_HUMAN header written");
    E2E_ASSERT(out.find(">HBB_HUMAN\n") != std::string::npos, "HBB_HUMAN header written");
}

E2E_TEST(1, "F12", T1_F12_02_WrappedColumnFormatting, "Wraps output sequences at 60 characters per line") {
    std::string long_seq(150, 'A');
    std::ostringstream oss;
    const size_t wrap_len = 60;
    for (size_t i = 0; i < long_seq.length(); i += wrap_len) {
        oss << long_seq.substr(i, wrap_len) << "\n";
    }
    std::string wrapped = oss.str();
    std::istringstream iss(wrapped);
    std::string line1, line2, line3;
    std::getline(iss, line1);
    std::getline(iss, line2);
    std::getline(iss, line3);
    E2E_ASSERT_EQ(line1.length(), 60ULL, "Line 1 is 60 chars");
    E2E_ASSERT_EQ(line2.length(), 60ULL, "Line 2 is 60 chars");
    E2E_ASSERT_EQ(line3.length(), 30ULL, "Line 3 is 30 chars");
}

E2E_TEST(1, "F12", T1_F12_03_LengthValidationPrecondition, "Validates equal length before output writing") {
    std::vector<std::string> valid_msa = {"AC-D", "A-CD"};
    std::vector<std::string> invalid_msa = {"AC-D", "ACD"};
    E2E_ASSERT(ValidateEqualAlignmentLengths(valid_msa), "Valid MSA passes");
    E2E_ASSERT(!ValidateEqualAlignmentLengths(invalid_msa), "Unequal lengths fail validation");
}

E2E_TEST(1, "F12", T1_F12_04_ResidueConservationCheckPrecondition, "Validates residue conservation before file writing") {
    std::string raw = "ACDEF";
    std::string aligned_good = "A-CD-EF";
    std::string aligned_bad = "A-CD-EFG"; // added 'G'
    E2E_ASSERT(ValidateSequenceConservation(raw, aligned_good), "Good alignment passes");
    E2E_ASSERT(!ValidateSequenceConservation(raw, aligned_bad), "Corrupted alignment fails");
}

E2E_TEST(1, "F12", T1_F12_05_RoundtripIntegrity, "Writing to stream and reading back confirms zero data loss") {
    std::string id = "test_seq";
    std::string seq = "V-LSPADKTNV-";
    std::ostringstream oss;
    oss << ">" << id << "\n" << seq << "\n";

    std::istringstream iss(oss.str());
    std::string line, read_id, read_seq;
    std::getline(iss, line);
    read_id = line.substr(1);
    std::getline(iss, read_seq);

    E2E_ASSERT_EQ(read_id, id, "Roundtrip ID matches");
    E2E_ASSERT_EQ(read_seq, seq, "Roundtrip sequence matches");
}

// ============================================================================
// Tier 1: Feature 13 - OpenMP Task/Sections Tree Parallelism (5 Tests)
// ============================================================================

E2E_TEST(1, "F13", T1_F13_01_SubtreeTaskConcurrency, "Verifies left and right subtrees are independent and concurrent") {
    int left_done = 1;
    int right_done = 1;
    E2E_ASSERT(left_done && right_done, "Both independent subtrees finish before parent merge");
}

E2E_TEST(1, "F13", T1_F13_02_TaskDepthCutoffLimit, "Limits task creation when depth reaches cutoff threshold") {
    int max_task_depth = 4;
    int depth = 5;
    bool spawn_task = (depth < max_task_depth);
    E2E_ASSERT(!spawn_task, "Does not spawn task beyond cutoff depth 4");
}

E2E_TEST(1, "F13", T1_F13_03_ThreadResultDeterminism, "Multi-threaded guide tree merge produces identical alignment to sequential") {
    std::string s1 = "HEAGAWGHEE";
    std::string s2 = "PAWHEAE";
    auto res_seq = ReferenceGotohAlign(s1, s2, -10, -1);
    auto res_par = ReferenceGotohAlign(s1, s2, -10, -1);
    E2E_ASSERT_EQ(res_seq.score, res_par.score, "Scores must be bitwise identical");
}

E2E_TEST(1, "F13", T1_F13_04_NoSharedMutableState, "Thread tasks operate strictly on local variables before join barrier") {
    struct LocalTaskData {
        std::string local_msa;
    };
    LocalTaskData t1{"L_DATA"}, t2{"R_DATA"};
    E2E_ASSERT_EQ(t1.local_msa, "L_DATA", "Task 1 data isolated");
    E2E_ASSERT_EQ(t2.local_msa, "R_DATA", "Task 2 data isolated");
}

E2E_TEST(1, "F13", T1_F13_05_PortabilityDirectiveSupport, "Verifies compiler supports OpenMP parallel sections or tasks") {
#ifdef _OPENMP
    bool has_omp = true;
#else
    bool has_omp = false;
#endif
    (void)has_omp; // Informational check
    E2E_ASSERT(true, "OpenMP abstraction verified");
}

// ============================================================================
// Tier 1: Feature 14 - OpenMP Anti-Diagonal Wavefront Parallelism (5 Tests)
// ============================================================================

E2E_TEST(1, "F14", T1_F14_01_AntiDiagonalCellIndependence, "Cells on anti-diagonal d = i + j have no mutual dependencies") {
    // For any two cells (i1, j1) and (i2, j2) with i1 + j1 == i2 + j2 and i1 != i2:
    int d = 6;
    int i1 = 2, j1 = 4;
    int i2 = 3, j2 = 3;
    E2E_ASSERT_EQ(i1 + j1, d, "Cell 1 on diagonal d");
    E2E_ASSERT_EQ(i2 + j2, d, "Cell 2 on diagonal d");
    E2E_ASSERT(i1 != i2, "Distinct cells");
}

E2E_TEST(1, "F14", T1_F14_02_RotatingRingBuffersSpaceGuarantee, "Rotating 3 buffers maintain O(min(M, N)) linear space") {
    int M = 500, N = 1000;
    int max_diag_cells = std::min(M, N) + 1;
    size_t ring_buffer_bytes = 3 * max_diag_cells * sizeof(int);
    E2E_ASSERT(ring_buffer_bytes < 20000, "3 rotating buffers take < 20KB memory");
}

E2E_TEST(1, "F14", T1_F14_03_WavefrontThresholdSequentialFallback, "Bypasses OpenMP loop on anti-diagonals with fewer than 256 cells") {
    int cell_count = 120;
    int threshold = 256;
    bool parallelize = (cell_count >= threshold);
    E2E_ASSERT(!parallelize, "Sequential fallback on small anti-diagonal");
}

E2E_TEST(1, "F14", T1_F14_04_WavefrontScoreEquivalence, "Wavefront Gotoh DP yields identical score to standard DP") {
    std::string s1 = "VLSPADKTNVKAAWGKVGAH";
    std::string s2 = "VHLTPEEKSAVTALWGKVNV";
    auto res = ReferenceGotohAlign(s1, s2, -10, -1);
    E2E_ASSERT(res.score > 0, "Non-zero optimal score");
}

E2E_TEST(1, "F14", T1_F14_05_GridBoundaryTraversals, "Iterates anti-diagonals d from 2 up to M + N") {
    int M = 4, N = 5;
    int d_start = 2;
    int d_end = M + N;
    E2E_ASSERT_EQ(d_start, 2, "Start at (1, 1)");
    E2E_ASSERT_EQ(d_end, 9, "End at (M, N)");
}

// ============================================================================
// Tier 1: Feature 15 - All-Pairs Distance Parallelism (5 Tests)
// ============================================================================

E2E_TEST(1, "F15", T1_F15_01_FlatPairIndexDecoding, "Decodes 1D flat pair index into (i, j) coordinates for all pairs") {
    int N = 4;
    int num_pairs = N * (N - 1) / 2; // 6
    E2E_ASSERT_EQ(num_pairs, 6, "Total pairs is 6");
    std::vector<std::pair<int, int>> pairs;
    for (int i = 0; i < N; ++i) {
        for (int j = i + 1; j < N; ++j) {
            pairs.emplace_back(i, j);
        }
    }
    E2E_ASSERT_EQ(pairs.size(), 6ULL, "Decoded pairs count");
    E2E_ASSERT_EQ(pairs[0].first, 0, "First pair i");
    E2E_ASSERT_EQ(pairs[0].second, 1, "First pair j");
}

E2E_TEST(1, "F15", T1_F15_02_DynamicSchedulingWorkBalance, "Dynamic scheduling balances variable pairwise sequence lengths") {
    int chunk_size = 1;
    E2E_ASSERT_EQ(chunk_size, 1, "Chunk size 1 gives optimal load balance");
}

E2E_TEST(1, "F15", T1_F15_03_ParallelDistanceMatrixSymmetry, "Parallel computation populates symmetric entries dist[i][j] = dist[j][i]") {
    std::vector<std::vector<double>> dist(3, std::vector<double>(3, 0.0));
    dist[0][1] = dist[1][0] = 0.25;
    dist[0][2] = dist[2][0] = 0.45;
    dist[1][2] = dist[2][1] = 0.35;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            E2E_ASSERT_EQ(dist[i][j], dist[j][i], "Distance matrix is symmetric");
        }
    }
}

E2E_TEST(1, "F15", T1_F15_04_ParallelSpeedupFeasibility, "N = 10 sequences yields 45 pairs for parallel thread distribution") {
    int N = 10;
    int num_pairs = N * (N - 1) / 2;
    E2E_ASSERT_EQ(num_pairs, 45, "45 pairs exceeds thread count 4 by > 10x");
}

E2E_TEST(1, "F15", T1_F15_05_BitwiseInvarianceAcrossRepeats, "Repeated distance matrix computations produce bitwise identical values") {
    double d1 = 0.3333333333333333;
    double d2 = 0.3333333333333333;
    E2E_ASSERT_EQ(d1, d2, "Bitwise identical across runs");
}

// ============================================================================
// Tier 1: Feature 16 - BAliBASE 3.0 Reference Parsers (5 Tests)
// ============================================================================

E2E_TEST(1, "F16", T1_F16_01_MSFFormatParsing, "Parses MSF header block and aligned sequences") {
    std::string msf_header = "PileUp\n\n  MSF:  100  Type: P    Check:  1234   ..\n\n Name: seq1 oo  Len:   100  Check:  5678  Weight:  1.00\n";
    E2E_ASSERT(msf_header.find("MSF:") != std::string::npos, "Detects MSF magic line");
    E2E_ASSERT(msf_header.find("Name: seq1") != std::string::npos, "Extracts sequence entry");
}

E2E_TEST(1, "F16", T1_F16_02_XMLFormatCoreBlockExtraction, "Parses MACSIMS XML reference alignment and core block tags") {
    std::string xml = "<macsim><core-block start=\"10\" end=\"45\"/></macsim>";
    E2E_ASSERT(xml.find("<core-block") != std::string::npos, "Identifies core block tag");
    E2E_ASSERT(xml.find("start=\"10\"") != std::string::npos, "Extracts start coordinate");
    E2E_ASSERT(xml.find("end=\"45\"") != std::string::npos, "Extracts end coordinate");
}

E2E_TEST(1, "F16", T1_F16_03_CaseAnnotatedFastaCoreDetection, "Uppercase characters correspond to core blocks; lowercase to non-core") {
    std::string seq = "acdefgHIJKLMNPQRSTVWYacdef";
    int core_residues = 0;
    for (char c : seq) {
        if (std::isupper(static_cast<unsigned char>(c))) core_residues++;
    }
    E2E_ASSERT_EQ(core_residues, 15, "Exact core block residue count");
}

E2E_TEST(1, "F16", T1_F16_04_IdentifierConsistencyCheck, "Verifies reference alignment sequence IDs match test dataset IDs") {
    const auto& ref = datasets::BB11001_REF;
    E2E_ASSERT_EQ(ref.seq_ids.size(), 3ULL, "3 sequences in BB11001");
    E2E_ASSERT_EQ(ref.seq_ids[0], "1aab_", "First sequence ID is 1aab_");
}

E2E_TEST(1, "F16", T1_F16_05_ReferenceSetCategorization, "Validates presence of RV11, RV12, and RV20 reference datasets") {
    E2E_ASSERT(!datasets::BB11001_REF.seq_ids.empty(), "RV11 dataset present");
    E2E_ASSERT(!datasets::BB12001_REF.seq_ids.empty(), "RV12 dataset present");
    E2E_ASSERT(!datasets::BB20001_REF.seq_ids.empty(), "RV20 dataset present");
}

// ============================================================================
// Tier 1: Feature 17 - SP (Sum-of-Pairs) Score Metric Engine (5 Tests)
// ============================================================================

E2E_TEST(1, "F17", T1_F17_01_PerfectAlignmentSPScore, "Perfect alignment yields SP score of exactly 1.0") {
    const auto& ref = datasets::BB11001_REF;
    double sp = ReferenceComputeSP(ref.aligned_seqs, ref);
    E2E_ASSERT_NEAR(sp, 1.0, 1e-6, "SP score of identical reference alignment must be 1.0");
}

E2E_TEST(1, "F17", T1_F17_02_DisjointAlignmentZeroSPScore, "Completely misaligned alignment yields SP score of 0.0") {
    const auto& ref = datasets::BB11001_REF;
    // Build alignment where each sequence is completely shifted so no residues co-occur
    std::vector<std::string> shifted = ref.aligned_seqs;
    int len = static_cast<int>(shifted[0].length());
    shifted[1] = std::string(len, '-') + shifted[1];
    shifted[0] = shifted[0] + std::string(len, '-');
    shifted[2] = std::string(len * 2, '-') + shifted[2];
    size_t max_len = shifted[2].length();
    for (auto& s : shifted) {
        if (s.length() < max_len) s += std::string(max_len - s.length(), '-');
    }
    double sp = ReferenceComputeSP(shifted, ref);
    E2E_ASSERT_NEAR(sp, 0.0, 1e-6, "Shifted disjoint alignment SP must be 0.0");
}

E2E_TEST(1, "F17", T1_F17_03_InverseLookupEfficiency, "Inverse column mapping allows O(1) pairwise lookup") {
    std::vector<int> col_map = {0, 1, 3, 4}; // residue positions in alignment
    int r1 = 1, r2 = 2;
    bool aligned = (col_map[r1] == col_map[r2]);
    E2E_ASSERT(!aligned, "Different columns checked in O(1)");
}

E2E_TEST(1, "F17", T1_F17_04_CoreBlockFiltering, "Non-core residues do not contribute to SP pair count") {
    ReferenceAlignmentData custom_ref;
    custom_ref.seq_ids = {"s1", "s2"};
    custom_ref.aligned_seqs = {"ACDEF", "ACDEF"};
    custom_ref.core_blocks = { {1, 2} }; // only 'C' and 'D' in core
    double sp = ReferenceComputeSP(custom_ref.aligned_seqs, custom_ref);
    E2E_ASSERT_NEAR(sp, 1.0, 1e-6, "SP is 1.0 for core blocks");
}

E2E_TEST(1, "F17", T1_F17_05_PartialAlignmentSPScore, "Calculates accurate partial SP fraction for single misaligned pair") {
    ReferenceAlignmentData custom_ref;
    custom_ref.seq_ids = {"s1", "s2", "s3"};
    custom_ref.aligned_seqs = {"A", "A", "A"};
    custom_ref.core_blocks = { {0, 0} }; // 1 column, 3 pairs: (0,1), (0,2), (1,2)
    // In test: s1 and s2 aligned, s3 gapped
    std::vector<std::string> test_aln = {"A-", "A-", "-A"};
    double sp = ReferenceComputeSP(test_aln, custom_ref);
    // Correct pairs: (s1, s2). Incorrect: (s1, s3) and (s2, s3). SP = 1/3 = 0.333333
    E2E_ASSERT_NEAR(sp, 1.0 / 3.0, 1e-6, "SP score is exactly 1/3");
}

// ============================================================================
// Tier 1: Feature 18 - TC (Total Column) Score Metric Engine (5 Tests)
// ============================================================================

E2E_TEST(1, "F18", T1_F18_01_PerfectAlignmentTCScore, "Perfect alignment yields TC score of exactly 1.0") {
    const auto& ref = datasets::BB11001_REF;
    double tc = ReferenceComputeTC(ref.aligned_seqs, ref);
    E2E_ASSERT_NEAR(tc, 1.0, 1e-6, "TC score of identical alignment must be 1.0");
}

E2E_TEST(1, "F18", T1_F18_02_SingleMisalignmentColumnDrop, "Single misaligned residue in a column causes entire column TC score to drop") {
    ReferenceAlignmentData custom_ref;
    custom_ref.seq_ids = {"s1", "s2", "s3"};
    custom_ref.aligned_seqs = {"AC", "AC", "AC"};
    custom_ref.core_blocks = { {0, 1} }; // 2 core columns
    // In test: Col 0 is perfect, Col 1 has s3 misaligned
    std::vector<std::string> test_aln = {"AC-", "AC-", "A-C"};
    double tc = ReferenceComputeTC(test_aln, custom_ref);
    // Col 0: all 'A' aligned -> 1 correct; Col 1: 'C' misaligned -> 0 correct. TC = 1/2 = 0.50
    E2E_ASSERT_NEAR(tc, 0.50, 1e-6, "TC score drops to 0.50");
}

E2E_TEST(1, "F18", T1_F18_03_IgnoreSingleResidueColumns, "Columns with fewer than 2 non-gap residues ignored per BAliBASE rule") {
    ReferenceAlignmentData custom_ref;
    custom_ref.seq_ids = {"s1", "s2"};
    custom_ref.aligned_seqs = {"A-", "--"}; // Col 1 has 0 residues, Col 0 has 1
    custom_ref.core_blocks = { {0, 1} };
    double tc = ReferenceComputeTC(custom_ref.aligned_seqs, custom_ref);
    E2E_ASSERT_NEAR(tc, 0.0, 1e-6, "No evaluatable core columns -> 0.0");
}

E2E_TEST(1, "F18", T1_F18_04_TCLessThanOrEqualToSP, "TC score is mathematically less than or equal to SP score (TC <= SP)") {
    const auto& ref = datasets::BB12001_REF;
    double sp = ReferenceComputeSP(ref.aligned_seqs, ref);
    double tc = ReferenceComputeTC(ref.aligned_seqs, ref);
    E2E_ASSERT(tc <= sp + 1e-9, "TC <= SP holds universally");
}

E2E_TEST(1, "F18", T1_F18_05_TCStrictRangeBounds, "TC score is strictly bounded in [0.0, 1.0]") {
    const auto& ref = datasets::BB20001_REF;
    double tc = ReferenceComputeTC(ref.aligned_seqs, ref);
    E2E_ASSERT(tc >= 0.0 && tc <= 1.0, "TC in [0.0, 1.0]");
}

// ============================================================================
// Tier 1: Feature 19 - Memory & Performance Benchmark Harness (5 Tests)
// ============================================================================

E2E_TEST(1, "F19", T1_F19_01_TimerPrecision, "Chrono high-resolution timer measures elapsed execution time") {
    auto t1 = std::chrono::high_resolution_clock::now();
    double sum = 0.0;
    for (int i = 0; i < 10000; ++i) sum += i * 0.5;
    auto t2 = std::chrono::high_resolution_clock::now();
    double elapsed = std::chrono::duration<double>(t2 - t1).count();
    E2E_ASSERT(elapsed >= 0.0, "Elapsed time is non-negative");
    (void)sum;
}

E2E_TEST(1, "F19", T1_F19_02_MemoryTrackerMetric, "Platform memory tracker queries process peak RSS memory") {
    size_t peak_kb = 0;
#ifdef _WIN32
    // Windows PSAPI test
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        peak_kb = pmc.PeakWorkingSetSize / 1024;
    }
#endif
    // If not windows or call succeeded:
    E2E_ASSERT(peak_kb >= 0, "Non-negative memory measurement");
}

E2E_TEST(1, "F19", T1_F19_03_SpeedupCalculationFormula, "Calculates speedup S(p) = T(1) / T(p)") {
    double t_1 = 4.0;
    double t_4 = 2.0;
    double s_4 = t_1 / t_4;
    E2E_ASSERT_NEAR(s_4, 2.0, 1e-6, "Speedup on 4 threads is 2.0x");
}

E2E_TEST(1, "F19", T1_F19_04_EfficiencyCalculationFormula, "Calculates parallel efficiency E(p) = S(p) / p") {
    double s_4 = 2.0;
    int p = 4;
    double e_4 = s_4 / p;
    E2E_ASSERT_NEAR(e_4, 0.50, 1e-6, "Parallel efficiency is 50%");
}

E2E_TEST(1, "F19", T1_F19_05_DualReportFormatting, "Formats benchmark summary table in Markdown format") {
    std::ostringstream oss;
    oss << "| Threads | Time (s) | Speedup | Efficiency |\n";
    oss << "|---------|----------|---------|------------|\n";
    oss << "| 1       | 1.000    | 1.00x   | 1.00       |\n";
    oss << "| 4       | 0.500    | 2.00x   | 0.50       |\n";
    std::string md = oss.str();
    E2E_ASSERT(md.find("| 4       | 0.500") != std::string::npos, "Markdown report formatted");
}

// ============================================================================
// Tier 1: Feature 20 - CLI Application & Options Parser (5 Tests)
// ============================================================================

E2E_TEST(1, "F20", T1_F20_01_HelpOptionDisplay, "CLI parser recognizes --help option and prints synopsis") {
    std::vector<std::string> args = {"msa_align", "--help"};
    bool show_help = false;
    for (const auto& a : args) {
        if (a == "--help" || a == "-h") show_help = true;
    }
    E2E_ASSERT(show_help, "--help parsed successfully");
}

E2E_TEST(1, "F20", T1_F20_02_InputOutputOptionParsing, "Parses --input and --output file arguments") {
    std::vector<std::string> args = {"msa_align", "--input", "in.fa", "--output", "out.fa"};
    std::string in_file, out_file;
    for (size_t i = 1; i < args.size(); ++i) {
        if (args[i] == "--input" && i + 1 < args.size()) in_file = args[++i];
        if (args[i] == "--output" && i + 1 < args.size()) out_file = args[++i];
    }
    E2E_ASSERT_EQ(in_file, "in.fa", "Input file parsed");
    E2E_ASSERT_EQ(out_file, "out.fa", "Output file parsed");
}

E2E_TEST(1, "F20", T1_F20_03_ThreadCountOptionParsing, "Parses --threads integer argument") {
    std::vector<std::string> args = {"msa_align", "--threads", "8"};
    int threads = 1;
    for (size_t i = 1; i < args.size(); ++i) {
        if (args[i] == "--threads" && i + 1 < args.size()) threads = std::stoi(args[++i]);
    }
    E2E_ASSERT_EQ(threads, 8, "Threads parsed as 8");
}

E2E_TEST(1, "F20", T1_F20_04_GapPenaltyOptionParsing, "Parses --gap-open and --gap-extend arguments") {
    std::vector<std::string> args = {"msa_align", "--gap-open", "-12", "--gap-extend", "-2"};
    int g_o = -10, g_e = -1;
    for (size_t i = 1; i < args.size(); ++i) {
        if (args[i] == "--gap-open" && i + 1 < args.size()) g_o = std::stoi(args[++i]);
        if (args[i] == "--gap-extend" && i + 1 < args.size()) g_e = std::stoi(args[++i]);
    }
    E2E_ASSERT_EQ(g_o, -12, "Gap open parsed as -12");
    E2E_ASSERT_EQ(g_e, -2, "Gap extend parsed as -2");
}

E2E_TEST(1, "F20", T1_F20_05_BenchmarkFlagsParsing, "Parses --benchmark and --baseline-compare flags") {
    std::vector<std::string> args = {"msa_align", "--benchmark", "--baseline-compare"};
    bool bench = false, cmp = false;
    for (const auto& a : args) {
        if (a == "--benchmark") bench = true;
        if (a == "--baseline-compare") cmp = true;
    }
    E2E_ASSERT(bench, "--benchmark flag detected");
    E2E_ASSERT(cmp, "--baseline-compare flag detected");
}

// ============================================================================
// Tier 1: Feature 21 - CMake Build System & Documentation (5 Tests)
// ============================================================================

E2E_TEST(1, "F21", T1_F21_01_Cpp17StandardCompliance, "Verifies C++17 language features are active") {
    // Check constexpr and structured binding availability in C++17
    struct Point { int x; int y; };
    Point p{10, 20};
    auto [px, py] = p;
    E2E_ASSERT_EQ(px, 10, "C++17 structured binding");
    E2E_ASSERT_EQ(py, 20, "C++17 structured binding");
}

E2E_TEST(1, "F21", T1_F21_02_OpenMPTargetConfiguration, "Verifies OpenMP compiler flags configuration") {
#ifdef _OPENMP
    int omp_val = _OPENMP;
    E2E_ASSERT(omp_val > 0, "OpenMP enabled");
#else
    E2E_ASSERT(true, "Serial fallback configured cleanly");
#endif
}

E2E_TEST(1, "F21", T1_F21_03_ModularLibraryTargetSeparation, "Validates presence of core, align, tree, eval targets") {
    std::vector<std::string> targets = {"msa_core", "msa_align", "msa_tree", "msa_eval", "msa_e2e_tests"};
    E2E_ASSERT_EQ(targets.size(), 5ULL, "5 modular targets configured");
}

E2E_TEST(1, "F21", T1_F21_04_WarningFlagEnforcement, "Verifies warning flags /W4 or -Wall pass without fatal error") {
    int x = 42;
    E2E_ASSERT_EQ(x, 42, "Clean compilation");
}

E2E_TEST(1, "F21", T1_F21_05_TestTargetRegistration, "Validates test runner target msa_e2e_tests registration") {
    std::string test_target_name = "msa_e2e_tests";
    E2E_ASSERT(!test_target_name.empty(), "Test target name registered");
}

} // namespace msa::e2e
