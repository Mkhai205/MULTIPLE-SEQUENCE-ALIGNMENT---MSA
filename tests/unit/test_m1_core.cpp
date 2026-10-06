#include "test_framework.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/profile.hpp"
#include "msa/io/fasta_io.hpp"
#include "msa/io/cli_parser.hpp"

#include <sstream>
#include <limits>
#include <stdexcept>

using namespace msa::core;
using namespace msa::io;

// =============================================================================
// Sequence Tests
// =============================================================================

TEST_CASE("Sequence - Basic Construction & Properties") {
    Sequence seq("seq1", "MKVILLFVL", "Test kinase protein");

    CHECK_EQ(seq.id(), "seq1");
    CHECK_EQ(seq.seq(), "MKVILLFVL");
    CHECK_EQ(seq.raw_seq(), "MKVILLFVL");
    CHECK_EQ(seq.description(), "Test kinase protein");
    CHECK_EQ(seq.length(), static_cast<size_t>(9));
    CHECK(!seq.empty());
    CHECK_EQ(seq[0], 'M');
    CHECK_EQ(seq[8], 'L');
}

TEST_CASE("Sequence - Automatic Case Normalization") {
    Sequence seq("seq2", "acdefghiklmnpqrstvwy");
    CHECK_EQ(seq.seq(), "ACDEFGHIKLMNPQRSTVWY");
}

TEST_CASE("Sequence - Whitespace and Newline Sanitization") {
    Sequence seq("seq_ws", "  MKVI\nLLFV\r\nL \t ");
    CHECK_EQ(seq.seq(), "MKVILLFVL");
    CHECK_EQ(seq.length(), static_cast<size_t>(9));
}

TEST_CASE("Sequence - Valid IUPAC Ambiguity and Extended Codes") {
    CHECK_NOTHROW(Sequence("ambig", "BZX*"));
    Sequence seq("ambig", "BZX*");
    CHECK_EQ(seq.seq(), "BZX*");

    CHECK_NOTHROW(Sequence("ext", "UOJ"));
    Sequence seq_ext("ext", "UOJ");
    CHECK_EQ(seq_ext.seq(), "UOJ");
}

TEST_CASE("Sequence - Rejection of Invalid Residues") {
    CHECK_THROWS_AS(Sequence("bad1", "MKV1L"), std::invalid_argument);
    CHECK_THROWS_AS(Sequence("bad2", "MKV@LL"), std::invalid_argument);
    CHECK_THROWS_AS(Sequence("bad3", "MKV#LL"), std::invalid_argument);
    CHECK_THROWS_AS(Sequence("bad4", "MKV$LL"), std::invalid_argument);
}

TEST_CASE("Sequence - Boundary Cases: Empty and Single Residue") {
    Sequence empty_seq("empty", "");
    CHECK(empty_seq.empty());
    CHECK_EQ(empty_seq.length(), static_cast<size_t>(0));

    Sequence single_seq("single", "M");
    CHECK_EQ(single_seq.length(), static_cast<size_t>(1));
    CHECK_EQ(single_seq[0], 'M');
}

TEST_CASE("Sequence - Long Sequence Handling (1500 Residues)") {
    std::string long_str(1500, 'A');
    Sequence long_seq("long", long_str);
    CHECK_EQ(long_seq.length(), static_cast<size_t>(1500));
    CHECK_EQ(long_seq[0], 'A');
    CHECK_EQ(long_seq[1499], 'A');
}

// =============================================================================
// BLOSUM62 Tests
// =============================================================================

TEST_CASE("BLOSUM62 - Canonical Diagonal Self-Scores") {
    const auto& matrix = Blosum62::instance();

    CHECK_EQ(matrix.score('C', 'C'), 9);
    CHECK_EQ(matrix.score('W', 'W'), 11);
    CHECK_EQ(matrix.score('H', 'H'), 8);
    CHECK_EQ(matrix.score('Y', 'Y'), 7);
    CHECK_EQ(matrix.score('P', 'P'), 7);
    CHECK_EQ(matrix.score('F', 'F'), 6);
    CHECK_EQ(matrix.score('M', 'M'), 5);
    CHECK_EQ(matrix.score('I', 'I'), 4);
    CHECK_EQ(matrix.score('V', 'V'), 4);
    CHECK_EQ(matrix.score('L', 'L'), 4);
    CHECK_EQ(matrix.score('D', 'D'), 6);
    CHECK_EQ(matrix.score('E', 'E'), 5);
    CHECK_EQ(matrix.score('K', 'K'), 5);
    CHECK_EQ(matrix.score('R', 'R'), 5);
    CHECK_EQ(matrix.score('Q', 'Q'), 5);
    CHECK_EQ(matrix.score('N', 'N'), 6);
    CHECK_EQ(matrix.score('S', 'S'), 4);
    CHECK_EQ(matrix.score('T', 'T'), 5);
    CHECK_EQ(matrix.score('A', 'A'), 4);
    CHECK_EQ(matrix.score('G', 'G'), 6);
}

TEST_CASE("BLOSUM62 - Full 24x24 Mathematical Symmetry") {
    const auto& matrix = Blosum62::instance();
    const std::string alphabet = "ARNDCQEGHILKMFPSTWYVBZX*";

    REQUIRE_EQ(alphabet.size(), static_cast<size_t>(24));

    for (size_t i = 0; i < alphabet.size(); ++i) {
        for (size_t j = 0; j < alphabet.size(); ++j) {
            char a = alphabet[i];
            char b = alphabet[j];
            CHECK_EQ(matrix.score(a, b), matrix.score(b, a));
        }
    }
}

TEST_CASE("BLOSUM62 - Case Insensitivity") {
    const auto& matrix = Blosum62::instance();

    CHECK_EQ(matrix.score('a', 'a'), matrix.score('A', 'A'));
    CHECK_EQ(matrix.score('w', 'w'), matrix.score('W', 'W'));
    CHECK_EQ(matrix.score('c', 'C'), matrix.score('C', 'C'));
    CHECK_EQ(matrix.score('r', 'N'), matrix.score('R', 'n'));
    CHECK_EQ(matrix.score('d', 'e'), matrix.score('D', 'E'));
}

TEST_CASE("BLOSUM62 - Ambiguity and Special Residue Codes") {
    const auto& matrix = Blosum62::instance();

    // 'B' represents Asp(D) or Asn(N)
    CHECK_EQ(matrix.score('B', 'B'), 4);
    CHECK_EQ(matrix.score('B', 'D'), 4);
    CHECK_EQ(matrix.score('B', 'N'), 3);

    // 'Z' represents Glu(E) or Gln(Q)
    CHECK_EQ(matrix.score('Z', 'Z'), 4);
    CHECK_EQ(matrix.score('Z', 'E'), 4);
    CHECK_EQ(matrix.score('Z', 'Q'), 3);

    // 'X' represents any amino acid
    CHECK_EQ(matrix.score('X', 'X'), -1);
    CHECK_EQ(matrix.score('X', 'A'), 0);
    CHECK_EQ(matrix.score('X', 'W'), -2);

    // '*' represents stop or unknown residue
    CHECK_EQ(matrix.score('*', '*'), 1);
    CHECK_EQ(matrix.score('*', 'A'), -4);
    CHECK_EQ(matrix.score('*', 'W'), -4);
}

TEST_CASE("BLOSUM62 - Known Cross-Scores") {
    const auto& matrix = Blosum62::instance();

    CHECK_EQ(matrix.score('A', 'R'), -1);
    CHECK_EQ(matrix.score('N', 'D'), 1);
    CHECK_EQ(matrix.score('I', 'V'), 3);
    CHECK_EQ(matrix.score('L', 'M'), 2);
    CHECK_EQ(matrix.score('F', 'Y'), 3);
    CHECK_EQ(matrix.score('W', 'C'), -2);
    CHECK_EQ(matrix.score('P', 'G'), -2);
}

TEST_CASE("BLOSUM62 - Fallback and Out-of-Alphabet Safety") {
    const auto& matrix = Blosum62::instance();

    CHECK_NOTHROW(matrix.score('?', '!'));
    CHECK_NOTHROW(matrix.score('1', '9'));
    CHECK_NOTHROW(matrix.score(' ', '-'));
}

// =============================================================================
// ScoreModel Tests
// =============================================================================

TEST_CASE("ScoreModel - Default Constructor Values") {
    ScoreModel model;
    CHECK_EQ(model.gapOpen(), -10);
    CHECK_EQ(model.gapExtend(), -1);
}

TEST_CASE("ScoreModel - Custom Config & Sign Normalization") {
    ScoreModel model(12, 2);
    CHECK_EQ(model.gapOpen(), -12);
    CHECK_EQ(model.gapExtend(), -2);

    ScoreModel model2(-11, -1);
    CHECK_EQ(model2.gapOpen(), -11);
    CHECK_EQ(model2.gapExtend(), -1);
}

TEST_CASE("ScoreModel - Arithmetic Underflow Immunity (NEG_INF)") {
    ScoreModel model(-10, -1);

    CHECK_EQ(ScoreModel::NEG_INF, -1'000'000'000);

    int accumulated = ScoreModel::NEG_INF + 10000 * model.gapExtend();
    CHECK(accumulated < -1'000'000'000);
    CHECK(accumulated > std::numeric_limits<int>::min());

    int headroom = ScoreModel::NEG_INF - std::numeric_limits<int>::min();
    CHECK(headroom > 1'000'000'000);
}

TEST_CASE("ScoreModel - Cost of Gap Calculation") {
    ScoreModel model(-10, -1);

    // Length 1: gap_open + 1 * gap_extend = -10 + -1 = -11
    CHECK_EQ(model.gapCost(1), -11);
    // Length 5: gap_open + 5 * gap_extend = -10 + -5 = -15
    CHECK_EQ(model.gapCost(5), -15);
    // Length 0: 0
    CHECK_EQ(model.gapCost(0), 0);
}

TEST_CASE("ScoreModel - Profile Effective Gap Penalties") {
    ScoreModel model(-10, -1);

    // If gap_frequency is 0.0, effective penalties are 100%
    CHECK_NEAR(model.effectiveGapOpen(0.0), -10.0, 1e-6);
    CHECK_NEAR(model.effectiveGapExtend(0.0), -1.0, 1e-6);

    // If gap_frequency is 0.5, effective penalties are halved
    CHECK_NEAR(model.effectiveGapOpen(0.5), -5.0, 1e-6);
    CHECK_NEAR(model.effectiveGapExtend(0.5), -0.5, 1e-6);

    // If gap_frequency is 1.0, effective penalties are 0.0
    CHECK_NEAR(model.effectiveGapOpen(1.0), 0.0, 1e-6);
    CHECK_NEAR(model.effectiveGapExtend(1.0), 0.0, 1e-6);
}

// =============================================================================
// Profile Tests
// =============================================================================

TEST_CASE("Profile - Single Sequence Construction and Equivalence") {
    Sequence seq("seq1", "ACDEF");
    Profile prof(seq);

    REQUIRE_EQ(prof.length(), static_cast<size_t>(5));
    REQUIRE_EQ(prof.numSequences(), static_cast<size_t>(1));

    // Residue frequencies: exactly 1.0 for the present residue, 0.0 for others
    int idx_a = Blosum62::charToIndex('A');
    CHECK_NEAR(prof.columnFrequencies(0)[static_cast<size_t>(idx_a)], 1.0, 1e-6);
    CHECK_NEAR(prof.gapFrequency(0), 0.0, 1e-6);

    // Score columns between two single-sequence profiles should exactly match Blosum62::score
    Sequence seq2("seq2", "RCDEF");
    Profile prof2(seq2);
    const auto& blosum = Blosum62::instance();

    double score_0_0 = Profile::scoreColumns(prof, 0, prof2, 0, blosum);
    int expected_0_0 = blosum.score('A', 'R');
    CHECK_NEAR(score_0_0, static_cast<double>(expected_0_0), 1e-6);
}

TEST_CASE("Profile - Multi-Sequence Frequencies and Consensus") {
    std::vector<std::string> ids = {"s1", "s2", "s3"};
    std::vector<std::string> seqs = {
        "ACD-",
        "ACE-",
        "ACD-"
    };

    Profile prof(ids, seqs);
    REQUIRE_EQ(prof.length(), static_cast<size_t>(4));
    REQUIRE_EQ(prof.numSequences(), static_cast<size_t>(3));

    // Column 0: 100% 'A'
    int idx_a = Blosum62::charToIndex('A');
    CHECK_NEAR(prof.columnFrequencies(0)[static_cast<size_t>(idx_a)], 1.0, 1e-6);

    // Column 2: 2/3 'D', 1/3 'E'
    int idx_d = Blosum62::charToIndex('D');
    int idx_e = Blosum62::charToIndex('E');
    CHECK_NEAR(prof.columnFrequencies(2)[static_cast<size_t>(idx_d)], 2.0 / 3.0, 1e-5);
    CHECK_NEAR(prof.columnFrequencies(2)[static_cast<size_t>(idx_e)], 1.0 / 3.0, 1e-5);

    // Column 3: 100% gap
    CHECK_NEAR(prof.gapFrequency(3), 1.0, 1e-6);

    // Consensus sequence: column 2 should be 'D' (majority 2/3), column 3 should be '-'
    CHECK_EQ(prof.consensusSequence(), "ACD-");
}

TEST_CASE("Profile - Merging and Gap Propagation") {
    // Merge two profiles of 1 sequence each:
    // P1: "AC"
    // P2: "DE"
    // Aligned traces: "A-C" vs "-DE"
    Profile p1(Sequence("p1", "AC"));
    Profile p2(Sequence("p2", "DE"));

    Profile merged = Profile::mergeProfiles(p1, p2, "A-C", "-DE");
    REQUIRE_EQ(merged.numSequences(), static_cast<size_t>(2));
    REQUIRE_EQ(merged.length(), static_cast<size_t>(3));
    CHECK_EQ(merged.getAlignedSequence(0), "A-C");
    CHECK_EQ(merged.getAlignedSequence(1), "-DE");
}

// =============================================================================
// FASTA I/O Tests
// =============================================================================

TEST_CASE("FASTA Parser - Single Sequence with Description") {
    std::string data = ">seq1 Alpha hemoglobin chain\nMKVILLFVL\n";
    std::istringstream iss(data);

    auto sequences = FastaParser::read_stream(iss);
    REQUIRE_EQ(sequences.size(), static_cast<size_t>(1));
    CHECK_EQ(sequences[0].id(), "seq1");
    CHECK_EQ(sequences[0].description(), "Alpha hemoglobin chain");
    CHECK_EQ(sequences[0].seq(), "MKVILLFVL");
}

TEST_CASE("FASTA Parser - Multi-Line Wrapped Sequence") {
    std::string data = 
        ">seq2 Multi-line test\n"
        "MKVI\n"
        "LLFV\n"
        "L\n";
    std::istringstream iss(data);

    auto sequences = FastaParser::read_stream(iss);
    REQUIRE_EQ(sequences.size(), static_cast<size_t>(1));
    CHECK_EQ(sequences[0].seq(), "MKVILLFVL");
}

TEST_CASE("FASTA Parser - Multi-Sequence File with CRLF") {
    std::string data = 
        ">prot_A First protein\r\n"
        "ACDEF\r\n"
        ">prot_B Second protein\r\n"
        "GHIKL\r\n";
    std::istringstream iss(data);

    auto sequences = FastaParser::read_stream(iss);
    REQUIRE_EQ(sequences.size(), static_cast<size_t>(2));
    CHECK_EQ(sequences[0].id(), "prot_A");
    CHECK_EQ(sequences[0].seq(), "ACDEF");
    CHECK_EQ(sequences[1].id(), "prot_B");
    CHECK_EQ(sequences[1].seq(), "GHIKL");
}

TEST_CASE("FASTA Parser - Blank Lines & Leading Whitespace") {
    std::string data = 
        "\n\n"
        ">seq_padded\n"
        "  ACDE\n"
        "\n"
        "  FGH\n";
    std::istringstream iss(data);

    auto sequences = FastaParser::read_stream(iss);
    REQUIRE_EQ(sequences.size(), static_cast<size_t>(1));
    CHECK_EQ(sequences[0].id(), "seq_padded");
    CHECK_EQ(sequences[0].seq(), "ACDEFGH");
}

TEST_CASE("FASTA Parser - Malformed Header Detection") {
    std::string data = "MKVILLFVL\n>seq2\nACDEF\n";
    std::istringstream iss(data);

    CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
}

TEST_CASE("FASTA Writer - Line Wrapping") {
    std::vector<Sequence> seqs = {
        Sequence("long_seq", std::string(130, 'A'), "130 residues")
    };

    std::ostringstream oss;
    FastaWriter::write_stream(oss, seqs, 60);
    std::string output = oss.str();

    CHECK(output.find(">long_seq 130 residues") != std::string::npos);

    std::istringstream iss(output);
    std::string header, line1, line2, line3;
    std::getline(iss, header);
    std::getline(iss, line1);
    std::getline(iss, line2);
    std::getline(iss, line3);

    CHECK_EQ(line1.length(), static_cast<size_t>(60));
    CHECK_EQ(line2.length(), static_cast<size_t>(60));
    CHECK_EQ(line3.length(), static_cast<size_t>(10));
}

TEST_CASE("FASTA Round-Trip Fidelity") {
    std::vector<Sequence> original = {
        Sequence("s1", "MKVILLFVL", "desc1"),
        Sequence("s2", "ACDEFGHIKLMNPQRSTVWY", "desc2"),
        Sequence("s3", "BZX*", "ambig")
    };

    std::stringstream ss;
    FastaWriter::write_stream(ss, original, 80);

    auto parsed = FastaParser::read_stream(ss);
    REQUIRE_EQ(parsed.size(), original.size());

    for (size_t i = 0; i < original.size(); ++i) {
        CHECK_EQ(parsed[i].id(), original[i].id());
        CHECK_EQ(parsed[i].description(), original[i].description());
        CHECK_EQ(parsed[i].seq(), original[i].seq());
    }
}

TEST_CASE("FASTA Alignment Integrity Verifier") {
    std::vector<Sequence> raw = {
        Sequence("p1", "MKVL"),
        Sequence("p2", "ML")
    };

    std::vector<Sequence> valid_aligned = {
        Sequence("p1", "MKVL"),
        Sequence("p2", "M--L")
    };

    std::vector<Sequence> unequal_lengths = {
        Sequence("p1", "MKVL"),
        Sequence("p2", "M-L")
    };

    std::vector<Sequence> corrupted_residues = {
        Sequence("p1", "MKVL"),
        Sequence("p2", "W--L")
    };

    CHECK(FastaWriter::verify_alignment_integrity(raw, valid_aligned));
    CHECK(!FastaWriter::verify_alignment_integrity(raw, unequal_lengths));
    CHECK(!FastaWriter::verify_alignment_integrity(raw, corrupted_residues));
}

// =============================================================================
// CLI Parser Tests
// =============================================================================

TEST_CASE("CLI Parser - Full Flag Options and Types") {
    const char* argv[] = {
        "msa_align",
        "-i", "input.fa",
        "-o", "output.fa",
        "-t", "4",
        "--gap-open", "-12",
        "--gap-extend", "-2",
        "--benchmark",
        "--baseline-compare",
        "-v"
    };
    int argc = sizeof(argv) / sizeof(argv[0]);

    CliParser parser;
    CliConfig config = parser.parse(argc, argv, false);

    CHECK_EQ(config.input_file.string(), "input.fa");
    CHECK_EQ(config.output_file.string(), "output.fa");
    CHECK_EQ(config.num_threads, 4);
    CHECK_EQ(config.gap_open, -12);
    CHECK_EQ(config.gap_extend, -2);
    CHECK(config.benchmark);
    CHECK(config.baseline_compare);
    CHECK(config.verbose);
}

TEST_CASE("CLI Parser - Inline Equal Syntax and Positive Gap Normalization") {
    const char* argv[] = {
        "msa_align",
        "--input=in.fa",
        "--output=out.fa",
        "--threads=8",
        "--gap-open=11",   // Must normalize to -11
        "--gap-extend=1"   // Must normalize to -1
    };
    int argc = sizeof(argv) / sizeof(argv[0]);

    CliParser parser;
    CliConfig config = parser.parse(argc, argv, false);

    CHECK_EQ(config.input_file.string(), "in.fa");
    CHECK_EQ(config.output_file.string(), "out.fa");
    CHECK_EQ(config.num_threads, 8);
    CHECK_EQ(config.gap_open, -11);
    CHECK_EQ(config.gap_extend, -1);
}

TEST_CASE("CLI Parser - Help and Version Flags") {
    const char* argv_help[] = {"msa_align", "--help"};
    CliParser parser;
    CliConfig cfg_help = parser.parse(2, argv_help, false);
    CHECK(cfg_help.show_help);

    const char* argv_ver[] = {"msa_align", "--version"};
    CliConfig cfg_ver = parser.parse(2, argv_ver, false);
    CHECK(cfg_ver.show_version);
}

TEST_CASE("CLI Parser - Error Conditions") {
    CliParser parser;

    // Missing required --input
    const char* argv_no_in[] = {"msa_align", "-o", "out.fa"};
    CHECK_THROWS_AS(parser.parse(3, argv_no_in, false), CliParseException);

    // Missing value for option
    const char* argv_no_val[] = {"msa_align", "-i", "in.fa", "--threads"};
    CHECK_THROWS_AS(parser.parse(4, argv_no_val, false), CliParseException);

    // Invalid non-integer value for threads
    const char* argv_bad_threads[] = {"msa_align", "-i", "in.fa", "--threads", "four"};
    CHECK_THROWS_AS(parser.parse(5, argv_bad_threads, false), CliParseException);

    // Unknown option
    const char* argv_unknown[] = {"msa_align", "-i", "in.fa", "--nonexistent-flag"};
    CHECK_THROWS_AS(parser.parse(4, argv_unknown, false), CliParseException);
}
