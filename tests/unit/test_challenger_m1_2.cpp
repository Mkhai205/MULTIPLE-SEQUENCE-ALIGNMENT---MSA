#include "test_framework.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/profile.hpp"
#include "msa/io/fasta_io.hpp"

#include <vector>
#include <string>
#include <sstream>
#include <limits>
#include <cmath>
#include <chrono>
#include <iostream>

using namespace msa::core;
using namespace msa::io;

// =============================================================================
// Authoritative NCBI Reference BLOSUM62 Matrix (24x24)
// Order: A, R, N, D, C, Q, E, G, H, I, L, K, M, F, P, S, T, W, Y, V, B, Z, X, *
// =============================================================================
static const char NCBI_AA_ORDER[24] = {
    'A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I',
    'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V',
    'B', 'Z', 'X', '*'
};

static const int NCBI_BLOSUM62_REFERENCE[24][24] = {
    /* A */ {  4, -1, -2, -2,  0, -1, -1,  0, -2, -1, -1, -1, -1, -2, -1,  1,  0, -3, -2,  0, -2, -1,  0, -4 },
    /* R */ { -1,  5,  0, -2, -3,  1,  0, -2,  0, -3, -2,  2, -1, -3, -2, -1, -1, -3, -2, -3, -1,  0, -1, -4 },
    /* N */ { -2,  0,  6,  1, -3,  0,  0,  0,  1, -3, -3,  0, -2, -3, -2,  1,  0, -4, -2, -3,  3,  0, -1, -4 },
    /* D */ { -2, -2,  1,  6, -3,  0,  2, -1, -1, -3, -4, -1, -3, -3, -1,  0, -1, -4, -3, -3,  4,  1, -1, -4 },
    /* C */ {  0, -3, -3, -3,  9, -3, -4, -3, -3, -1, -1, -3, -1, -2, -3, -1, -1, -2, -2, -1, -3, -3, -2, -4 },
    /* Q */ { -1,  1,  0,  0, -3,  5,  2, -2,  0, -3, -2,  1,  0, -3, -1,  0, -1, -2, -1, -2,  0,  3, -1, -4 },
    /* E */ { -1,  0,  0,  2, -4,  2,  5, -2,  0, -3, -3,  1, -2, -3, -1,  0, -1, -3, -2, -2,  1,  4, -1, -4 },
    /* G */ {  0, -2,  0, -1, -3, -2, -2,  6, -2, -4, -4, -2, -3, -3, -2,  0, -2, -2, -3, -3, -1, -2, -1, -4 },
    /* H */ { -2,  0,  1, -1, -3,  0,  0, -2,  8, -3, -3, -1, -2, -1, -2, -1, -2, -2,  2, -3,  0,  0, -1, -4 },
    /* I */ { -1, -3, -3, -3, -1, -3, -3, -4, -3,  4,  2, -3,  1,  0, -3, -2, -1, -3, -1,  3, -3, -3, -1, -4 },
    /* L */ { -1, -2, -3, -4, -1, -2, -3, -4, -3,  2,  4, -2,  2,  0, -3, -2, -1, -2, -1,  1, -4, -3, -1, -4 },
    /* K */ { -1,  2,  0, -1, -3,  1,  1, -2, -1, -3, -2,  5, -1, -3, -1,  0, -1, -3, -2, -2,  0,  1, -1, -4 },
    /* M */ { -1, -1, -2, -3, -1,  0, -2, -3, -2,  1,  2, -1,  5,  0, -2, -1, -1, -1, -1,  1, -3, -1, -1, -4 },
    /* F */ { -2, -3, -3, -3, -2, -3, -3, -3, -1,  0,  0, -3,  0,  6, -4, -2, -2,  1,  3, -1, -3, -3, -1, -4 },
    /* P */ { -1, -2, -2, -1, -3, -1, -1, -2, -2, -3, -3, -1, -2, -4,  7, -1, -1, -4, -3, -2, -1, -1, -2, -4 },
    /* S */ {  1, -1,  1,  0, -1,  0,  0,  0, -1, -2, -2,  0, -1, -2, -1,  4,  1, -3, -2, -2,  0,  0,  0, -4 },
    /* T */ {  0, -1,  0, -1, -1, -1, -1, -2, -2, -1, -1, -1, -1, -2, -1,  1,  5, -2, -2,  0, -1, -1,  0, -4 },
    /* W */ { -3, -3, -4, -4, -2, -2, -3, -2, -2, -3, -2, -3, -1,  1, -4, -3, -2, 11,  2, -3, -4, -3, -2, -4 },
    /* Y */ { -2, -2, -2, -3, -2, -1, -2, -3,  2, -1, -1, -2, -1,  3, -3, -2, -2,  2,  7, -1, -3, -2, -1, -4 },
    /* V */ {  0, -3, -3, -3, -1, -2, -2, -3, -3,  3,  1, -2,  1, -1, -2, -2,  0, -3, -1,  4, -3, -2, -1, -4 },
    /* B */ { -2, -1,  3,  4, -3,  0,  1, -1,  0, -3, -4,  0, -3, -3, -1,  0, -1, -4, -3, -3,  4,  1, -1, -4 },
    /* Z */ { -1,  0,  0,  1, -3,  3,  4, -2,  0, -3, -3,  1, -1, -3, -1,  0, -1, -3, -2, -2,  1,  4, -1, -4 },
    /* X */ {  0, -1, -1, -1, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2,  0,  0, -2, -1, -1, -1, -1, -1, -4 },
    /* * */ { -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4,  1 }
};

// =============================================================================
// Test 1: Exhaustive BLOSUM62 Verification against NCBI Reference (All 576 Pairs)
// =============================================================================
TEST_CASE("Challenger M1-2: BLOSUM62 Exhaustive NCBI 576-Cell Verification") {
    const auto& matrix = Blosum62::instance();

    for (int i = 0; i < 24; ++i) {
        char aa1 = NCBI_AA_ORDER[i];
        char aa1_lower = static_cast<char>(std::tolower(static_cast<unsigned char>(aa1)));

        for (int j = 0; j < 24; ++j) {
            char aa2 = NCBI_AA_ORDER[j];
            char aa2_lower = static_cast<char>(std::tolower(static_cast<unsigned char>(aa2)));

            int expected = NCBI_BLOSUM62_REFERENCE[i][j];

            // 1. Direct index check
            CHECK_EQ(matrix.scoreByIndex(i, j), expected);

            // 2. Character lookup check
            CHECK_EQ(matrix.score(aa1, aa2), expected);

            // 3. Case insensitivity check
            CHECK_EQ(matrix.score(aa1_lower, aa2_lower), expected);
            CHECK_EQ(matrix.score(aa1_lower, aa2), expected);
            CHECK_EQ(matrix.score(aa1, aa2_lower), expected);

            // 4. Mathematical symmetry check
            CHECK_EQ(matrix.score(aa1, aa2), matrix.score(aa2, aa1));
            CHECK_EQ(expected, NCBI_BLOSUM62_REFERENCE[j][i]);
        }
    }
}

// =============================================================================
// Test 2: Extended Amino Acids and Robust Fallback
// =============================================================================
TEST_CASE("Challenger M1-2: Extended Amino Acids and Fallback Equivalence") {
    const auto& matrix = Blosum62::instance();

    // Selenocysteine (U/u) -> Cysteine (C)
    for (int i = 0; i < 24; ++i) {
        char aa = NCBI_AA_ORDER[i];
        CHECK_EQ(matrix.score('U', aa), matrix.score('C', aa));
        CHECK_EQ(matrix.score('u', aa), matrix.score('C', aa));
    }

    // Pyrrolysine (O/o) -> Lysine (K)
    for (int i = 0; i < 24; ++i) {
        char aa = NCBI_AA_ORDER[i];
        CHECK_EQ(matrix.score('O', aa), matrix.score('K', aa));
        CHECK_EQ(matrix.score('o', aa), matrix.score('K', aa));
    }

    // Xle (J/j) -> Unknown (X)
    for (int i = 0; i < 24; ++i) {
        char aa = NCBI_AA_ORDER[i];
        CHECK_EQ(matrix.score('J', aa), matrix.score('X', aa));
        CHECK_EQ(matrix.score('j', aa), matrix.score('X', aa));
    }

    // Out-of-alphabet characters safely default to 'X' without throwing or UB
    const char invalid_chars[] = {'1', '9', '?', '!', '@', '#', '$', '%', '^', '&', '~', '\0', -1, -50, -128};
    for (char bad_c : invalid_chars) {
        CHECK_EQ(matrix.score(bad_c, 'A'), matrix.score('X', 'A'));
        CHECK_EQ(matrix.score('W', bad_c), matrix.score('W', 'X'));
        CHECK_EQ(matrix.score(bad_c, bad_c), matrix.score('X', 'X'));
    }
}

// =============================================================================
// Test 3: ScoreModel Affine Cost Range and Boundary Analysis (k in [1, 100000])
// =============================================================================
TEST_CASE("Challenger M1-2: ScoreModel Affine Cost Range and Boundary Analysis") {
    const ScoreModel default_model;
    CHECK_EQ(default_model.gapOpen(), -10);
    CHECK_EQ(default_model.gapExtend(), -1);

    // Boundary conditions: k <= 0 returns 0
    CHECK_EQ(default_model.gapCost(0), 0);
    CHECK_EQ(default_model.gapCost(-1), 0);
    CHECK_EQ(default_model.gapCost(-1000), 0);

    // Test across range k in [1, 100000]
    const std::vector<int> test_lengths = {
        1, 2, 3, 5, 10, 20, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000
    };

    for (int k : test_lengths) {
        int expected = -10 + k * (-1);
        CHECK_EQ(default_model.gapCost(k), expected);
    }

    // Test with non-default parameters
    const ScoreModel custom_model(12, 2);
    CHECK_EQ(custom_model.gapOpen(), -12);
    CHECK_EQ(custom_model.gapExtend(), -2);

    for (int k : test_lengths) {
        int expected = -12 + k * (-2);
        CHECK_EQ(custom_model.gapCost(k), expected);
    }

    // Test negative parameter constructor normalization
    const ScoreModel neg_param_model(-15, -3);
    CHECK_EQ(neg_param_model.gapOpen(), -15);
    CHECK_EQ(neg_param_model.gapExtend(), -3);
    for (int k : test_lengths) {
        int expected = -15 + k * (-3);
        CHECK_EQ(neg_param_model.gapCost(k), expected);
    }
}

// =============================================================================
// Test 4: ScoreModel NEG_INF Underflow Immunity and Addition Safety
// =============================================================================
TEST_CASE("Challenger M1-2: ScoreModel NEG_INF Underflow Immunity and Addition Safety") {
    const ScoreModel model(-10, -1);

    // 1. Verify constant value
    CHECK_EQ(ScoreModel::NEG_INF, -1'000'000'000);

    // 2. Verify headroom against INT_MIN
    int min_int = std::numeric_limits<int>::min(); // -2,147,483,648
    int headroom = ScoreModel::NEG_INF - min_int;
    CHECK(headroom >= 1'147'483'648);

    // 3. Safe accumulation of 100,000 gap extend steps
    int accumulated = ScoreModel::NEG_INF;
    for (int step = 0; step < 100000; ++step) {
        accumulated += model.gapExtend(); // -1 each step
    }
    CHECK_EQ(accumulated, -1'000'100'000);
    CHECK(accumulated > min_int);
    CHECK(ScoreModel::isNegInf(accumulated));

    // 4. Safe addition of two NEG_INF (e.g. forward + reverse Myers-Miller split)
    int two_inf = ScoreModel::NEG_INF + ScoreModel::NEG_INF; // -2,000,000,000
    CHECK_EQ(two_inf, -2'000'000'000);
    CHECK(two_inf > min_int);
    CHECK(ScoreModel::isNegInf(two_inf));

    // 5. Unreachable sentinel classification
    CHECK(ScoreModel::isNegInf(ScoreModel::NEG_INF));
    CHECK(ScoreModel::isNegInf(ScoreModel::NEG_INF / 2));
    CHECK(ScoreModel::isNegInf(ScoreModel::NEG_INF / 2 - 1));
    CHECK(!ScoreModel::isNegInf(ScoreModel::NEG_INF / 2 + 1));
    CHECK(!ScoreModel::isNegInf(0));
    CHECK(!ScoreModel::isNegInf(-1000000));
}

// =============================================================================
// Test 5: Profile Sum-of-Pairs Clade Size 1 Exact BLOSUM62 Equivalence
// =============================================================================
TEST_CASE("Challenger M1-2: Profile Sum-of-Pairs Clade Size 1 Exact BLOSUM62 Equivalence") {
    const auto& blosum = Blosum62::instance();

    // Test all 24 x 24 character combinations
    for (int i = 0; i < 24; ++i) {
        char aa1 = NCBI_AA_ORDER[i];
        Sequence seq1("s1", std::string(1, aa1));
        Profile p1(seq1);

        for (int j = 0; j < 24; ++j) {
            char aa2 = NCBI_AA_ORDER[j];
            Sequence seq2("s2", std::string(1, aa2));
            Profile p2(seq2);

            double prof_score = Profile::scoreColumns(p1, 0, p2, 0, blosum);
            int expected_score = blosum.score(aa1, aa2);

            CHECK_NEAR(prof_score, static_cast<double>(expected_score), 1e-9);
        }
    }

    // Test on realistic 50-residue sequence
    std::string s1_str = "MKVILLFVLAVAYAGPVDDEAAQLKEEIENMKVKLEELQAELEELAKNKK";
    std::string s2_str = "MRVILLFLLSVAFAGPVDDEADQLREEIDNMKVKLEELQAELQELAQNKR";

    Sequence seq1("seq1", s1_str);
    Sequence seq2("seq2", s2_str);
    Profile prof1(seq1);
    Profile prof2(seq2);

    REQUIRE_EQ(prof1.length(), static_cast<size_t>(50));
    REQUIRE_EQ(prof2.length(), static_cast<size_t>(50));

    for (size_t col = 0; col < 50; ++col) {
        double p_score = Profile::scoreColumns(prof1, col, prof2, col, blosum);
        int b_score = blosum.score(s1_str[col], s2_str[col]);
        CHECK_NEAR(p_score, static_cast<double>(b_score), 1e-9);
    }
}

// =============================================================================
// Test 6: Profile Multi-Sequence Sum-of-Pairs Exact Average Oracle
// =============================================================================
TEST_CASE("Challenger M1-2: Profile Multi-Sequence Sum-of-Pairs Exact Average Oracle") {
    const auto& blosum = Blosum62::instance();

    std::vector<std::string> ids1 = {"A1", "A2", "A3", "A4"};
    std::vector<std::string> seqs1 = {
        "MKVI",
        "LKVI",
        "MRVI",
        "ARVI"
    };

    std::vector<std::string> ids2 = {"B1", "B2", "B3"};
    std::vector<std::string> seqs2 = {
        "MKLI",
        "MRLL",
        "WRLV"
    };

    Profile p1(ids1, seqs1);
    Profile p2(ids2, seqs2);

    REQUIRE_EQ(p1.length(), static_cast<size_t>(4));
    REQUIRE_EQ(p2.length(), static_cast<size_t>(4));
    REQUIRE_EQ(p1.numSequences(), static_cast<size_t>(4));
    REQUIRE_EQ(p2.numSequences(), static_cast<size_t>(3));

    for (size_t col1 = 0; col1 < 4; ++col1) {
        for (size_t col2 = 0; col2 < 4; ++col2) {
            double actual_score = Profile::scoreColumns(p1, col1, p2, col2, blosum);

            // Compute exact mathematical Sum-of-Pairs average oracle
            double expected_sum = 0.0;
            for (size_t i = 0; i < ids1.size(); ++i) {
                for (size_t j = 0; j < ids2.size(); ++j) {
                    expected_sum += blosum.score(seqs1[i][col1], seqs2[j][col2]);
                }
            }
            double expected_avg = expected_sum / (ids1.size() * ids2.size());

            CHECK_NEAR(actual_score, expected_avg, 1e-9);
        }
    }
}

// =============================================================================
// Test 7: Sequence Stress & Memory Scaling (100,000 Residues)
// =============================================================================
TEST_CASE("Challenger M1-2: Sequence Stress & Memory Scaling (100,000 Residues)") {
    const size_t STRESS_LEN = 100000;
    std::string large_seq_data;
    large_seq_data.reserve(STRESS_LEN);

    const char aa_alphabet[] = "ACDEFGHIKLMNPQRSTVWY";
    for (size_t i = 0; i < STRESS_LEN; ++i) {
        large_seq_data.push_back(aa_alphabet[i % 20]);
    }

    auto start_time = std::chrono::high_resolution_clock::now();

    Sequence seq("giant_protein", large_seq_data, "100k Residue Synthetic Protein", true);

    auto construct_time = std::chrono::high_resolution_clock::now();
    double ms_construct = std::chrono::duration<double, std::milli>(construct_time - start_time).count();

    REQUIRE_EQ(seq.length(), STRESS_LEN);
    CHECK_EQ(seq.id(), "giant_protein");
    CHECK_EQ(seq.front(), 'A');
    CHECK_EQ(seq.back(), aa_alphabet[(STRESS_LEN - 1) % 20]);
    CHECK(seq.isValid());
    CHECK(!seq.findFirstInvalidChar().has_value());

    // Test append performance on large sequence (10,000 additional residues)
    std::string extra(10000, 'M');
    seq.append(extra);
    CHECK_EQ(seq.length(), STRESS_LEN + 10000);
    CHECK_EQ(seq.back(), 'M');

    // Test invalid residue detection on 110k sequence
    std::string bad_str = seq.raw_seq();
    bad_str[77777] = '!'; // Inject illegal character
    Sequence bad_seq;
    bad_seq.setId("bad");
    bad_seq.setSeq(bad_str);
    CHECK(!bad_seq.isValid());
    auto bad_pos = bad_seq.findFirstInvalidChar();
    REQUIRE(bad_pos.has_value());
    CHECK_EQ(*bad_pos, static_cast<size_t>(77777));

    std::cout << "\n    [STRESS STATS] 100k Residue Sequence Constructed in " << ms_construct << " ms";
}

// =============================================================================
// Test 8: Profile Stress & Memory Scaling (1,000 Sequences x 500 Residues)
// =============================================================================
TEST_CASE("Challenger M1-2: Profile Stress & Memory Scaling (1,000 Sequences x 500 Residues)") {
    const size_t NUM_SEQS = 1000;
    const size_t ALIGN_LEN = 500;

    std::vector<std::string> ids;
    ids.reserve(NUM_SEQS);
    std::vector<std::string> seqs;
    seqs.reserve(NUM_SEQS);

    const char aa_alphabet[] = "ACDEFGHIKLMNPQRSTVWY-"; // 20 AA + gap
    for (size_t k = 0; k < NUM_SEQS; ++k) {
        ids.push_back("seq_" + std::to_string(k));
        std::string s;
        s.reserve(ALIGN_LEN);
        for (size_t c = 0; c < ALIGN_LEN; ++c) {
            // Introduce deterministic pattern
            s.push_back(aa_alphabet[(k + c) % 21]);
        }
        seqs.push_back(std::move(s));
    }

    auto start_time = std::chrono::high_resolution_clock::now();

    Profile prof(std::move(ids), std::move(seqs));

    auto build_time = std::chrono::high_resolution_clock::now();
    double ms_build = std::chrono::duration<double, std::milli>(build_time - start_time).count();

    REQUIRE_EQ(prof.length(), ALIGN_LEN);
    REQUIRE_EQ(prof.numSequences(), NUM_SEQS);

    // Verify mathematical frequency partition for all 500 columns:
    // sum of AA frequencies + gap frequency must equal exactly 1.0
    for (size_t col = 0; col < ALIGN_LEN; ++col) {
        double sum_freq = prof.gapFrequency(col);
        const auto& col_f = prof.columnFrequencies(col);
        for (size_t a = 0; a < Profile::ALPHABET_SIZE; ++a) {
            sum_freq += col_f[a];
        }
        CHECK_NEAR(sum_freq, 1.0, 1e-6);

        int sum_counts = prof.gapCount(col);
        const auto& col_c = prof.columnCounts(col);
        for (size_t a = 0; a < Profile::ALPHABET_SIZE; ++a) {
            sum_counts += col_c[a];
        }
        CHECK_EQ(sum_counts, static_cast<int>(NUM_SEQS));
    }

    // Benchmark consensus generation
    auto c_start = std::chrono::high_resolution_clock::now();
    std::string consensus = prof.consensusSequence();
    auto c_end = std::chrono::high_resolution_clock::now();
    double ms_consensus = std::chrono::duration<double, std::milli>(c_end - c_start).count();

    CHECK_EQ(consensus.length(), ALIGN_LEN);

    std::cout << "\n    [STRESS STATS] 1000 Seqs x 500 Cols Profile Matrix Built in " << ms_build 
              << " ms, Consensus Generated in " << ms_consensus << " ms";
}

// =============================================================================
// Test 9: FASTA High-Volume Round-Trip Stress
// =============================================================================
TEST_CASE("Challenger M1-2: FASTA High-Volume Round-Trip Stress") {
    const size_t NUM_SEQS = 100;
    const size_t SEQ_LEN = 1000; // Total 100,000 residues

    std::vector<Sequence> original_seqs;
    original_seqs.reserve(NUM_SEQS);

    for (size_t i = 0; i < NUM_SEQS; ++i) {
        std::string raw(SEQ_LEN, "ACDEFGHIKLMNPQRSTVWY"[i % 20]);
        original_seqs.emplace_back("fasta_seq_" + std::to_string(i), raw, "description_" + std::to_string(i));
    }

    std::stringstream ss;
    FastaWriter::write_stream(ss, original_seqs, 60);

    auto parsed_seqs = FastaParser::read_stream(ss);
    REQUIRE_EQ(parsed_seqs.size(), NUM_SEQS);

    for (size_t i = 0; i < NUM_SEQS; ++i) {
        CHECK_EQ(parsed_seqs[i].id(), original_seqs[i].id());
        CHECK_EQ(parsed_seqs[i].seq(), original_seqs[i].seq());
        CHECK_EQ(parsed_seqs[i].length(), SEQ_LEN);
    }
}

// =============================================================================
// Test 10: Sequence Massive Stress & Memory Scaling (1,000,000 Residues)
// =============================================================================
TEST_CASE("Challenger M1-2: Sequence Massive Stress & Memory Scaling (1,000,000 Residues)") {
    const size_t MEGA_LEN = 1000000;
    std::string mega_str;
    mega_str.reserve(MEGA_LEN);
    const char aa_alphabet[] = "ACDEFGHIKLMNPQRSTVWY";
    for (size_t i = 0; i < MEGA_LEN; ++i) {
        mega_str.push_back(aa_alphabet[i % 20]);
    }

    auto t0 = std::chrono::high_resolution_clock::now();
    Sequence mega_seq("mega_protein", mega_str, "1 Million Residues", true);
    auto t1 = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

    REQUIRE_EQ(mega_seq.length(), MEGA_LEN);
    CHECK(mega_seq.isValid());
    CHECK_EQ(mega_seq[0], 'A');
    CHECK_EQ(mega_seq[MEGA_LEN - 1], aa_alphabet[(MEGA_LEN - 1) % 20]);

    std::cout << "\n    [STRESS STATS] 1,000,000 Residue Sequence Created & Validated in " << ms << " ms";
}

// =============================================================================
// Test 11: Profile Massive Scaling (5,000 Sequences x 300 Residues = 1.5M Cells)
// =============================================================================
TEST_CASE("Challenger M1-2: Profile Massive Scaling (5,000 Sequences x 300 Residues)") {
    const size_t NUM_SEQS = 5000;
    const size_t ALIGN_LEN = 300;

    std::vector<std::string> ids;
    ids.reserve(NUM_SEQS);
    std::vector<std::string> seqs;
    seqs.reserve(NUM_SEQS);

    const char aa_alphabet[] = "ACDEFGHIKLMNPQRSTVWY-";
    for (size_t k = 0; k < NUM_SEQS; ++k) {
        ids.push_back("s_" + std::to_string(k));
        std::string s;
        s.reserve(ALIGN_LEN);
        for (size_t c = 0; c < ALIGN_LEN; ++c) {
            s.push_back(aa_alphabet[(k + c) % 21]);
        }
        seqs.push_back(std::move(s));
    }

    auto t0 = std::chrono::high_resolution_clock::now();
    Profile prof(std::move(ids), std::move(seqs));
    auto t1 = std::chrono::high_resolution_clock::now();
    double ms_build = std::chrono::duration<double, std::milli>(t1 - t0).count();

    REQUIRE_EQ(prof.length(), ALIGN_LEN);
    REQUIRE_EQ(prof.numSequences(), NUM_SEQS);

    auto t2 = std::chrono::high_resolution_clock::now();
    std::string consensus = prof.consensusSequence();
    auto t3 = std::chrono::high_resolution_clock::now();
    double ms_cons = std::chrono::duration<double, std::milli>(t3 - t2).count();

    CHECK_EQ(consensus.length(), ALIGN_LEN);

    std::cout << "\n    [STRESS STATS] 5,000 Seqs x 300 Cols Profile Matrix Built in " << ms_build 
              << " ms, Consensus Generated in " << ms_cons << " ms";
}
