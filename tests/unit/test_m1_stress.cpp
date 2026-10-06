#include "test_framework.hpp"
#include "msa/core/sequence.hpp"
#include "msa/core/blosum62.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/profile.hpp"
#include "msa/io/fasta_io.hpp"
#include "msa/io/cli_parser.hpp"

#include <sstream>
#include <limits>
#include <string>
#include <vector>
#include <array>
#include <stdexcept>

using namespace msa::core;
using namespace msa::io;

// =============================================================================
// GROUP 1: Adversarial FASTA Parser Stress Tests
// =============================================================================

TEST_CASE("Stress FASTA - Completely Empty File & Stream") {
    // 0-byte stream
    {
        std::istringstream iss("");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // Whitespace-only stream
    {
        std::istringstream iss("   \n\t  \r\n   \n\n\t");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // Comment-only stream
    {
        std::istringstream iss("; This is a comment\n; Another comment\n;\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
}

TEST_CASE("Stress FASTA - Header Without Sequence (EOF and Consecutive)") {
    // Header immediately followed by EOF (no newline)
    {
        std::istringstream iss(">seq_eof");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // Header followed by newline then EOF
    {
        std::istringstream iss(">seq_eof_nl\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // Consecutive headers without sequence body between them
    {
        std::istringstream iss(">seq1 First protein\n>seq2 Second protein\nACDEF\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // Header with empty blank lines before next header
    {
        std::istringstream iss(">seq1\n\n\n\n>seq2\nACDEF\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // When allow_empty_sequences is enabled: should parse with empty raw_seq
    {
        std::istringstream iss(">seq_empty Empty record\n");
        FastaParser::Options opts;
        opts.allow_empty_sequences = true;
        auto seqs = FastaParser::read_stream(iss, opts);
        REQUIRE_EQ(seqs.size(), static_cast<size_t>(1));
        CHECK_EQ(seqs[0].id(), "seq_empty");
        CHECK(seqs[0].empty());
        CHECK_EQ(seqs[0].length(), static_cast<size_t>(0));
    }
}

TEST_CASE("Stress FASTA - Sequence Without Header") {
    // Sequence data on line 1 before any '>'
    {
        std::istringstream iss("MKVILLFVL\n>seq1\nACDEF\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // Leading spaces before sequence data without header
    {
        std::istringstream iss("   ACDEFGHIKLMNPQRSTVWY\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // Header indented with leading spaces (FASTA requires '>' at column 1)
    {
        std::istringstream iss("  >seq_indented\nACDEF\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
}

TEST_CASE("Stress FASTA - Non-ASCII and Binary Content") {
    // Embedded null character in sequence line
    {
        std::string raw = ">seq_null\nACD";
        raw.push_back('\0');
        raw += "EF\n";
        std::istringstream iss(raw);
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // Multi-byte UTF-8 character in sequence
    {
        std::string raw = ">seq_utf8\nACD\xC3\xA9""EF\n";
        std::istringstream iss(raw);
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // High-ASCII bytes (0x80 and 0xFF)
    {
        std::string raw80 = ">seq_hi\nACD\x80""EF\n";
        std::istringstream iss80(raw80);
        CHECK_THROWS_AS(FastaParser::read_stream(iss80), FastaParseException);

        std::string rawFF = ">seq_ff\nACD\xFF""EF\n";
        std::istringstream issFF(rawFF);
        CHECK_THROWS_AS(FastaParser::read_stream(issFF), FastaParseException);
    }
    // Control characters (bell, escape)
    {
        std::string raw_bell = ">seq_bell\nACD\x07""EF\n";
        std::istringstream iss(raw_bell);
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);

        std::string raw_esc = ">seq_esc\nACD\x1B""EF\n";
        std::istringstream iss_esc(raw_esc);
        CHECK_THROWS_AS(FastaParser::read_stream(iss_esc), FastaParseException);
    }
    // Numeric and punctuation characters in sequence
    {
        std::istringstream iss_num(">seq_num\nACD123EF\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss_num), FastaParseException);

        std::istringstream iss_sym(">seq_sym\nACD@#$EF\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss_sym), FastaParseException);
    }
}

TEST_CASE("Stress FASTA - Huge Headers and Extreme Sequences") {
    // Huge description in header (10,000 characters)
    {
        std::string huge_desc(10000, 'D');
        std::string fasta_text = ">seq_huge " + huge_desc + "\nMKVILLFVL\n";
        std::istringstream iss(fasta_text);
        auto seqs = FastaParser::read_stream(iss);
        REQUIRE_EQ(seqs.size(), static_cast<size_t>(1));
        CHECK_EQ(seqs[0].id(), "seq_huge");
        CHECK_EQ(seqs[0].description(), huge_desc);
        CHECK_EQ(seqs[0].seq(), "MKVILLFVL");
    }
    // Huge identifier (2,000 characters)
    {
        std::string huge_id(2000, 'I');
        std::string fasta_text = ">" + huge_id + " Description\nACDEF\n";
        std::istringstream iss(fasta_text);
        auto seqs = FastaParser::read_stream(iss);
        REQUIRE_EQ(seqs.size(), static_cast<size_t>(1));
        CHECK_EQ(seqs[0].id(), huge_id);
        CHECK_EQ(seqs[0].seq(), "ACDEF");
    }
    // Extreme sequence length (50,000 residues)
    {
        std::string huge_seq(50000, 'A');
        std::string fasta_text = ">seq_50k\n" + huge_seq + "\n";
        std::istringstream iss(fasta_text);
        auto seqs = FastaParser::read_stream(iss);
        REQUIRE_EQ(seqs.size(), static_cast<size_t>(1));
        CHECK_EQ(seqs[0].length(), static_cast<size_t>(50000));
        CHECK_EQ(seqs[0].seq(), huge_seq);
    }
}

TEST_CASE("Stress FASTA - Mixed CRLF, LF, and Fragmented Lines") {
    // Mixed line terminators in single record
    {
        std::string data = ">seq_mixed Mixed CRLF and LF\r\nACDE\nFGH\r\nIKLM\n";
        std::istringstream iss(data);
        auto seqs = FastaParser::read_stream(iss);
        REQUIRE_EQ(seqs.size(), static_cast<size_t>(1));
        CHECK_EQ(seqs[0].seq(), "ACDEFGHIKLM");
    }
    // Extreme fragmentation: 1 residue per line across 20 lines
    {
        std::string data = ">seq_frag\n";
        std::string expected = "ACDEFGHIKLMNPQRSTVWY";
        for (char c : expected) {
            data.push_back(c);
            data += "\r\n";
        }
        std::istringstream iss(data);
        auto seqs = FastaParser::read_stream(iss);
        REQUIRE_EQ(seqs.size(), static_cast<size_t>(1));
        CHECK_EQ(seqs[0].seq(), expected);
    }
    // Multiple records with erratic blank lines
    {
        std::string data = "\n\n>s1\n\nACD\n\n\n>s2\n\nEFG\n\n";
        std::istringstream iss(data);
        auto seqs = FastaParser::read_stream(iss);
        REQUIRE_EQ(seqs.size(), static_cast<size_t>(2));
        CHECK_EQ(seqs[0].id(), "s1");
        CHECK_EQ(seqs[0].seq(), "ACD");
        CHECK_EQ(seqs[1].id(), "s2");
        CHECK_EQ(seqs[1].seq(), "EFG");
    }
}

TEST_CASE("Stress FASTA - Duplicate Identifier Detection") {
    std::string data = ">seq1 First\nACDEF\n>seq1 Duplicate\nGHIKL\n";
    std::istringstream iss(data);

    // Default mode rejects duplicates
    CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);

    // Explicit opt-out allows duplicates
    std::istringstream iss2(data);
    FastaParser::Options opts;
    opts.check_duplicate_ids = false;
    auto seqs = FastaParser::read_stream(iss2, opts);
    REQUIRE_EQ(seqs.size(), static_cast<size_t>(2));
    CHECK_EQ(seqs[0].id(), "seq1");
    CHECK_EQ(seqs[1].id(), "seq1");
}

TEST_CASE("Stress FASTA - Malformed Headers") {
    // Standalone '>'
    {
        std::istringstream iss(">\nACDEF\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // '>' followed only by spaces
    {
        std::istringstream iss(">    \nACDEF\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
    // '>' followed only by tabs
    {
        std::istringstream iss(">\t\t\t\nACDEF\n");
        CHECK_THROWS_AS(FastaParser::read_stream(iss), FastaParseException);
    }
}

TEST_CASE("Stress FASTA - Nonexistent File Path") {
    CHECK_THROWS_AS(
        FastaParser::read_file("nonexistent_path_msa_stress_test_12345.fa"),
        FastaParseException
    );
}

TEST_CASE("Stress FASTA - Alignment Integrity Verifier Boundaries") {
    std::string err;

    // Both empty: alignment verification fails
    CHECK(!FastaWriter::verify_alignment_integrity({}, {}, &err));
    CHECK(!err.empty());

    // Count mismatch
    std::vector<Sequence> raw = {Sequence("s1", "ACD"), Sequence("s2", "EFG")};
    std::vector<Sequence> aln1 = {Sequence("s1", "ACD")};
    CHECK(!FastaWriter::verify_alignment_integrity(raw, aln1, &err));

    // ID mismatch
    std::vector<Sequence> aln_bad_id = {Sequence("s1", "ACD"), Sequence("wrong_id", "EFG")};
    CHECK(!FastaWriter::verify_alignment_integrity(raw, aln_bad_id, &err));

    // Mutation of residues
    std::vector<Sequence> aln_mutated = {Sequence("s1", "ACD"), Sequence("s2", "E-W")};
    CHECK(!FastaWriter::verify_alignment_integrity(raw, aln_mutated, &err));

    // Correct alignment with gaps
    std::vector<Sequence> aln_valid = {Sequence("s1", "A-CD"), Sequence("s2", "EF-G")};
    CHECK(FastaWriter::verify_alignment_integrity(raw, aln_valid, &err));
}

// =============================================================================
// GROUP 2: BLOSUM62 & Ambiguity Stress Tests
// =============================================================================

TEST_CASE("Stress BLOSUM62 - Ambiguity Codes Exhaustive Pairwise") {
    const auto& blosum = Blosum62::instance();
    const char ambig_codes[] = {'B', 'Z', 'X', '*'};

    // Verify self-scores
    CHECK_EQ(blosum.score('B', 'B'), 4);
    CHECK_EQ(blosum.score('Z', 'Z'), 4);
    CHECK_EQ(blosum.score('X', 'X'), -1);
    CHECK_EQ(blosum.score('*', '*'), 1);

    // Verify symmetry between all ambiguity pairs
    for (char a : ambig_codes) {
        for (char b : ambig_codes) {
            CHECK_EQ(blosum.score(a, b), blosum.score(b, a));
        }
    }

    // Verify B cross-scores against Asp (D) and Asn (N)
    CHECK_EQ(blosum.score('B', 'D'), 4);
    CHECK_EQ(blosum.score('B', 'N'), 3);
    CHECK_EQ(blosum.score('B', 'A'), -2);

    // Verify Z cross-scores against Glu (E) and Gln (Q)
    CHECK_EQ(blosum.score('Z', 'E'), 4);
    CHECK_EQ(blosum.score('Z', 'Q'), 3);
    CHECK_EQ(blosum.score('Z', 'A'), -1);

    // Verify X against standard amino acids (X self is -1, X against others is 0 or -1 or -2)
    const std::string canonical = "ACDEFGHIKLMNPQRSTVWY";
    for (char aa : canonical) {
        int score_x = blosum.score('X', aa);
        CHECK(score_x >= -2 && score_x <= 0);
        CHECK_EQ(blosum.score('X', aa), blosum.score(aa, 'X'));
    }

    // Verify * against standard amino acids (all -4 except stop self 1)
    for (char aa : canonical) {
        CHECK_EQ(blosum.score('*', aa), -4);
        CHECK_EQ(blosum.score(aa, '*'), -4);
    }
}

TEST_CASE("Stress BLOSUM62 - Extended Residues U, O, J") {
    const auto& blosum = Blosum62::instance();

    // U is Selenocysteine, mapped to Cysteine (C)
    CHECK_EQ(blosum.score('U', 'U'), blosum.score('C', 'C'));
    CHECK_EQ(blosum.score('U', 'C'), blosum.score('C', 'C'));
    CHECK_EQ(blosum.score('U', 'A'), blosum.score('C', 'A'));
    CHECK_EQ(blosum.score('u', 'u'), blosum.score('C', 'C'));

    // O is Pyrrolysine, mapped to Lysine (K)
    CHECK_EQ(blosum.score('O', 'O'), blosum.score('K', 'K'));
    CHECK_EQ(blosum.score('O', 'K'), blosum.score('K', 'K'));
    CHECK_EQ(blosum.score('O', 'A'), blosum.score('K', 'A'));
    CHECK_EQ(blosum.score('o', 'o'), blosum.score('K', 'K'));

    // J is Leu/Ile ambiguity, mapped to Unknown (X)
    CHECK_EQ(blosum.score('J', 'J'), blosum.score('X', 'X'));
    CHECK_EQ(blosum.score('J', 'X'), blosum.score('X', 'X'));
    CHECK_EQ(blosum.score('J', 'A'), blosum.score('X', 'A'));
    CHECK_EQ(blosum.score('j', 'j'), blosum.score('X', 'X'));
}

TEST_CASE("Stress BLOSUM62 - Out-of-Alphabet & Extreme Characters") {
    const auto& blosum = Blosum62::instance();

    // Characters outside IUPAC must safely resolve to 'X' without throwing or segfaulting
    const char rogue_chars[] = {'0', '9', '?', '!', '@', '#', '$', ' ', '\t', '\n', '-', '.'};
    for (char rc : rogue_chars) {
        CHECK_NOTHROW(blosum.score(rc, rc));
        CHECK_NOTHROW(blosum.score(rc, 'A'));
        CHECK_NOTHROW(blosum.score('W', rc));
        CHECK_EQ(blosum.score(rc, 'A'), blosum.score('X', 'A'));
    }

    // High-ASCII and negative signed char values
    for (int byte_val = 128; byte_val < 256; ++byte_val) {
        char c = static_cast<char>(byte_val);
        CHECK_NOTHROW(blosum.score(c, 'A'));
        CHECK_EQ(blosum.score(c, 'A'), blosum.score('X', 'A'));
    }

    // Null character '\0'
    CHECK_NOTHROW(blosum.score('\0', '\0'));
    CHECK_EQ(blosum.score('\0', 'A'), blosum.score('X', 'A'));
}

TEST_CASE("Stress Sequence - Ambiguity and Extended Residue Sanitization") {
    // Valid IUPAC sequences with ambiguity and extended codes
    CHECK_NOTHROW(Sequence("s_amb", "BZX*UOJ"));
    Sequence seq("s_amb", "BZX*UOJ");
    CHECK_EQ(seq.seq(), "BZX*UOJ");

    // Case normalization: lowercase extended codes become uppercase
    Sequence seq_low("s_low", "bzx*uoj");
    CHECK_EQ(seq_low.seq(), "BZX*UOJ");

    // Whitespace is sanitized and stripped automatically
    Sequence seq_ws("s_ws", "ACDEF ");
    CHECK_EQ(seq_ws.seq(), "ACDEF");

    // Rejection of invalid characters
    CHECK_THROWS_AS(Sequence("bad1", "ACDEF1"), std::invalid_argument);
    CHECK_THROWS_AS(Sequence("bad2", "ACDEF?"), std::invalid_argument);
    CHECK_THROWS_AS(Sequence("bad3", "ACDEF%"), std::invalid_argument);
    CHECK_THROWS_AS(Sequence("bad4", "ACDEF~"), std::invalid_argument);
    CHECK_THROWS_AS(Sequence("bad5", "ACDEF\x01"), std::invalid_argument);
}

TEST_CASE("Stress BLOSUM62 - Exhaustive 65536 Byte Domain Matrix Safety") {
    const auto& blosum = Blosum62::instance();

    // Verify all 256 * 256 = 65,536 possible byte inputs execute safely without UB or memory faults
    for (int byte_a = 0; byte_a < 256; ++byte_a) {
        char ca = static_cast<char>(byte_a);
        for (int byte_b = 0; byte_b < 256; ++byte_b) {
            char cb = static_cast<char>(byte_b);
            int s = blosum.score(ca, cb);
            // Every score must fall within valid BLOSUM62 score bounds [-4, 11]
            CHECK(s >= -4 && s <= 11);
            // Symmetry must hold for all byte pairs
            CHECK_EQ(s, blosum.score(cb, ca));
        }
    }
}

// =============================================================================
// GROUP 3: Profile Boundary Cases
// =============================================================================

TEST_CASE("Stress Profile - Default and Empty Profile Operations") {
    Profile p_def;
    CHECK(p_def.empty());
    CHECK_EQ(p_def.length(), static_cast<size_t>(0));
    CHECK_EQ(p_def.numSequences(), static_cast<size_t>(0));
    CHECK_EQ(p_def.size(), static_cast<size_t>(0));
    CHECK_EQ(p_def.consensusSequence(), "");
    CHECK_EQ(p_def.conservationScore(0), 0.0);
    CHECK_EQ(p_def.aminoAcidFrequency(0, 'A'), 0.0);

    auto letter_freq = p_def.getLetterFrequencies(0);
    for (double f : letter_freq) {
        CHECK_EQ(f, 0.0);
    }

    // Out-of-range indexing throws std::out_of_range
    CHECK_THROWS_AS(p_def.columnFrequencies(0), std::out_of_range);
    CHECK_THROWS_AS(p_def.gapFrequency(0), std::out_of_range);
    CHECK_THROWS_AS(p_def.columnCounts(0), std::out_of_range);
    CHECK_THROWS_AS(p_def.gapCount(0), std::out_of_range);

    // Profile from empty sequence
    Sequence empty_seq("empty", "");
    Profile p_from_empty(empty_seq);
    CHECK(p_from_empty.empty());
    CHECK_EQ(p_from_empty.length(), static_cast<size_t>(0));
}

TEST_CASE("Stress Profile - Single Sequence Profile Equivalence") {
    Sequence seq("s1", "A");
    Profile prof(seq);
    REQUIRE_EQ(prof.length(), static_cast<size_t>(1));
    REQUIRE_EQ(prof.numSequences(), static_cast<size_t>(1));

    int idx_a = Blosum62::charToIndex('A');
    CHECK_NEAR(prof.columnFrequencies(0)[static_cast<size_t>(idx_a)], 1.0, 1e-6);
    CHECK_NEAR(prof.gapFrequency(0), 0.0, 1e-6);
    CHECK_EQ(prof.consensusSequence(), "A");
    CHECK_NEAR(prof.conservationScore(0), 1.0, 1e-6);

    // Single residue profile column scoring matches Blosum62 self-score
    const auto& blosum = Blosum62::instance();
    double score = Profile::scoreColumns(prof, 0, prof, 0, blosum);
    CHECK_NEAR(score, static_cast<double>(blosum.score('A', 'A')), 1e-6);
}

TEST_CASE("Stress Profile - 100% Gap Columns") {
    std::vector<std::string> ids = {"g1", "g2"};
    std::vector<std::string> seqs = {"---", "-.-"};
    Profile prof(ids, seqs);

    REQUIRE_EQ(prof.length(), static_cast<size_t>(3));
    REQUIRE_EQ(prof.numSequences(), static_cast<size_t>(2));

    for (size_t c = 0; c < 3; ++c) {
        CHECK_NEAR(prof.gapFrequency(c), 1.0, 1e-6);
        CHECK_EQ(prof.gapCount(c), 2);
        CHECK_NEAR(prof.conservationScore(c), 0.0, 1e-6);

        for (size_t a = 0; a < Profile::ALPHABET_SIZE; ++a) {
            CHECK_NEAR(prof.columnFrequencies(c)[a], 0.0, 1e-6);
        }
    }

    CHECK_EQ(prof.consensusSequence(), "---");

    // Profile-to-profile column scoring against a normal profile yields 0.0
    Sequence s_normal("norm", "ACD");
    Profile p_norm(s_normal);
    const auto& blosum = Blosum62::instance();

    for (size_t c = 0; c < 3; ++c) {
        double pair_score = Profile::scoreColumns(prof, c, p_norm, c, blosum);
        CHECK_NEAR(pair_score, 0.0, 1e-6);
    }
}

TEST_CASE("Stress Profile - 100% Homogeneous Columns") {
    std::vector<std::string> ids = {"w1", "w2", "w3", "w4"};
    std::vector<std::string> seqs = {"WWWW", "WWWW", "WWWW", "WWWW"};
    Profile prof(ids, seqs);

    REQUIRE_EQ(prof.length(), static_cast<size_t>(4));
    REQUIRE_EQ(prof.numSequences(), static_cast<size_t>(4));

    int idx_w = Blosum62::charToIndex('W');
    for (size_t c = 0; c < 4; ++c) {
        CHECK_NEAR(prof.columnFrequencies(c)[static_cast<size_t>(idx_w)], 1.0, 1e-6);
        CHECK_NEAR(prof.gapFrequency(c), 0.0, 1e-6);
        CHECK_NEAR(prof.conservationScore(c), 1.0, 1e-6);
    }
    CHECK_EQ(prof.consensusSequence(), "WWWW");

    const auto& blosum = Blosum62::instance();
    double self_score = Profile::scoreColumns(prof, 0, prof, 0, blosum);
    CHECK_NEAR(self_score, static_cast<double>(blosum.score('W', 'W')), 1e-6);
    CHECK_NEAR(self_score, 11.0, 1e-6);
}

TEST_CASE("Stress Profile - Invalid Dimensions in Constructor") {
    // Mismatched sequence IDs count and sequences count
    CHECK_THROWS_AS(
        Profile({"id1"}, {"ACD", "DEF"}),
        std::invalid_argument
    );

    // Mismatched sequence lengths in profile
    CHECK_THROWS_AS(
        Profile({"id1", "id2"}, {"ACD", "AC"}),
        std::invalid_argument
    );
    CHECK_THROWS_AS(
        Profile({"id1", "id2", "id3"}, {"ACD", "ACD", "ACDEF"}),
        std::invalid_argument
    );
}

TEST_CASE("Stress Profile - MergeProfiles Boundaries") {
    Profile p1(Sequence("s1", "AC"));
    Profile p2(Sequence("s2", "DF"));

    // Mismatched trace lengths throw invalid_argument
    CHECK_THROWS_AS(
        Profile::mergeProfiles(p1, p2, "A-C", "DF"),
        std::invalid_argument
    );

    // Single residue merge
    Profile p_single1(Sequence("s1", "A"));
    Profile p_single2(Sequence("s2", "D"));
    Profile merged_single = Profile::mergeProfiles(p_single1, p_single2, "A", "D");
    REQUIRE_EQ(merged_single.length(), static_cast<size_t>(1));
    REQUIRE_EQ(merged_single.numSequences(), static_cast<size_t>(2));
    CHECK_EQ(merged_single.getAlignedSequence(0), "A");
    CHECK_EQ(merged_single.getAlignedSequence(1), "D");

    // Alternating insertions and gap propagation
    Profile merged_alt = Profile::mergeProfiles(p1, p2, "A-C-", "-D-F");
    REQUIRE_EQ(merged_alt.length(), static_cast<size_t>(4));
    REQUIRE_EQ(merged_alt.numSequences(), static_cast<size_t>(2));
    CHECK_EQ(merged_alt.getAlignedSequence(0), "A-C-");
    CHECK_EQ(merged_alt.getAlignedSequence(1), "-D-F");
}

// =============================================================================
// GROUP 4: CLI Parser Boundary Arguments
// =============================================================================

TEST_CASE("Stress CLI - Boundary Gap Penalties") {
    CliParser parser;

    // Boundary: gap-open 0
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "--gap-open", "0"};
        auto cfg = parser.parse(5, argv, false);
        CHECK_EQ(cfg.gap_open, 0);
    }
    // Boundary: positive gap-open 10 (normalizes to -10)
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "--gap-open", "10"};
        auto cfg = parser.parse(5, argv, false);
        CHECK_EQ(cfg.gap_open, -10);
    }
    // Boundary: negative gap-open -10
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "--gap-open", "-10"};
        auto cfg = parser.parse(5, argv, false);
        CHECK_EQ(cfg.gap_open, -10);
    }
    // Boundary: max allowable penalty 1000 (normalizes to -1000)
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "--gap-open", "1000"};
        auto cfg = parser.parse(5, argv, false);
        CHECK_EQ(cfg.gap_open, -1000);
    }
    // Boundary: min allowable penalty -1000
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "--gap-open", "-1000"};
        auto cfg = parser.parse(5, argv, false);
        CHECK_EQ(cfg.gap_open, -1000);
    }
    // Out of range: gap-open 1001 and -1001
    {
        const char* argv1[] = {"msa_align", "-i", "in.fa", "--gap-open", "1001"};
        CHECK_THROWS_AS(parser.parse(5, argv1, false), CliParseException);

        const char* argv2[] = {"msa_align", "-i", "in.fa", "--gap-open", "-1001"};
        CHECK_THROWS_AS(parser.parse(5, argv2, false), CliParseException);
    }

    // Boundary: gap-extend 0
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "--gap-extend", "0"};
        auto cfg = parser.parse(5, argv, false);
        CHECK_EQ(cfg.gap_extend, 0);
    }
    // Boundary: positive gap-extend 2 (normalizes to -2)
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "--gap-extend", "2"};
        auto cfg = parser.parse(5, argv, false);
        CHECK_EQ(cfg.gap_extend, -2);
    }
    // Out of range: gap-extend 1001 and -1001
    {
        const char* argv1[] = {"msa_align", "-i", "in.fa", "--gap-extend", "1001"};
        CHECK_THROWS_AS(parser.parse(5, argv1, false), CliParseException);

        const char* argv2[] = {"msa_align", "-i", "in.fa", "--gap-extend", "-1001"};
        CHECK_THROWS_AS(parser.parse(5, argv2, false), CliParseException);
    }
}

TEST_CASE("Stress CLI - Boundary Thread Values") {
    CliParser parser;

    // Minimum thread count: 1
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "-t", "1"};
        auto cfg = parser.parse(5, argv, false);
        CHECK_EQ(cfg.num_threads, 1);
    }
    // Maximum thread count: 256
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "-t", "256"};
        auto cfg = parser.parse(5, argv, false);
        CHECK_EQ(cfg.num_threads, 256);
    }
    // Out of range: threads 0
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "-t", "0"};
        CHECK_THROWS_AS(parser.parse(5, argv, false), CliParseException);
    }
    // Out of range: negative threads -1, -5
    {
        const char* argv1[] = {"msa_align", "-i", "in.fa", "-t", "-1"};
        CHECK_THROWS_AS(parser.parse(5, argv1, false), CliParseException);

        const char* argv2[] = {"msa_align", "-i", "in.fa", "-t", "-5"};
        CHECK_THROWS_AS(parser.parse(5, argv2, false), CliParseException);
    }
    // Out of range: threads 257
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "-t", "257"};
        CHECK_THROWS_AS(parser.parse(5, argv, false), CliParseException);
    }
    // Out of range: extreme thread count 999999999
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "-t", "999999999"};
        CHECK_THROWS_AS(parser.parse(5, argv, false), CliParseException);
    }
    // Integer overflow thread value
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "-t", "9999999999999999999999"};
        CHECK_THROWS_AS(parser.parse(5, argv, false), CliParseException);
    }
    // Non-numeric thread value
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "-t", "auto"};
        CHECK_THROWS_AS(parser.parse(5, argv, false), CliParseException);
    }
}

TEST_CASE("Stress CLI - Missing Argument Values & Flag Collisions") {
    CliParser parser;

    // Missing value at end of argv
    {
        const char* argv_i[] = {"msa_align", "-i"};
        CHECK_THROWS_AS(parser.parse(2, argv_i, false), CliParseException);

        const char* argv_o[] = {"msa_align", "-i", "in.fa", "-o"};
        CHECK_THROWS_AS(parser.parse(4, argv_o, false), CliParseException);

        const char* argv_t[] = {"msa_align", "-i", "in.fa", "-t"};
        CHECK_THROWS_AS(parser.parse(4, argv_t, false), CliParseException);

        const char* argv_go[] = {"msa_align", "-i", "in.fa", "--gap-open"};
        CHECK_THROWS_AS(parser.parse(4, argv_go, false), CliParseException);

        const char* argv_ge[] = {"msa_align", "-i", "in.fa", "--gap-extend"};
        CHECK_THROWS_AS(parser.parse(4, argv_ge, false), CliParseException);
    }

    // Flag collision: an option immediately followed by another flag
    {
        const char* argv[] = {"msa_align", "-i", "-o", "out.fa"};
        CHECK_THROWS_AS(parser.parse(4, argv, false), CliParseException);

        const char* argv2[] = {"msa_align", "-i", "in.fa", "-t", "--gap-open", "-10"};
        CHECK_THROWS_AS(parser.parse(6, argv2, false), CliParseException);
    }
}

TEST_CASE("Stress CLI - Inline Equal Syntax Edge Cases") {
    CliParser parser;

    // Valid inline values
    {
        const char* argv[] = {
            "msa_align",
            "--input=target.fa",
            "--output=result.aln",
            "--threads=16",
            "--gap-open=-12",
            "--gap-extend=-2"
        };
        auto cfg = parser.parse(6, argv, false);
        CHECK_EQ(cfg.input_file.string(), "target.fa");
        CHECK_EQ(cfg.output_file.string(), "result.aln");
        CHECK_EQ(cfg.num_threads, 16);
        CHECK_EQ(cfg.gap_open, -12);
        CHECK_EQ(cfg.gap_extend, -2);
    }

    // Empty inline value: --input=
    {
        const char* argv[] = {"msa_align", "--input="};
        CHECK_THROWS_AS(parser.parse(2, argv, false), CliParseException);
    }

    // Empty inline value for numeric flag: --threads=
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "--threads="};
        CHECK_THROWS_AS(parser.parse(4, argv, false), CliParseException);
    }

    // Empty inline value for gap penalty: --gap-open=
    {
        const char* argv[] = {"msa_align", "-i", "in.fa", "--gap-open="};
        CHECK_THROWS_AS(parser.parse(4, argv, false), CliParseException);
    }
}

TEST_CASE("Stress CLI - Unknown Flags, Precedence, and File Validation") {
    CliParser parser;

    // No arguments at all (missing --input)
    {
        const char* argv[] = {"msa_align"};
        CHECK_THROWS_AS(parser.parse(1, argv, false), CliParseException);
    }

    // Unknown options
    {
        const char* argv1[] = {"msa_align", "-i", "in.fa", "-z"};
        CHECK_THROWS_AS(parser.parse(4, argv1, false), CliParseException);

        const char* argv2[] = {"msa_align", "-i", "in.fa", "--unknown-flag"};
        CHECK_THROWS_AS(parser.parse(4, argv2, false), CliParseException);
    }

    // Precedence: --help immediately returns show_help without validating missing --input
    {
        const char* argv[] = {"msa_align", "--help"};
        auto cfg = parser.parse(2, argv, false);
        CHECK(cfg.show_help);
    }
    // Precedence: -h overrides unknown flags
    {
        const char* argv[] = {"msa_align", "-h", "--bogus-flag"};
        auto cfg = parser.parse(3, argv, false);
        CHECK(cfg.show_help);
    }
    // Precedence: --version immediately returns show_version
    {
        const char* argv[] = {"msa_align", "--version"};
        auto cfg = parser.parse(2, argv, false);
        CHECK(cfg.show_version);
    }

    // validate_file_exists = true on missing input file
    {
        const char* argv[] = {"msa_align", "-i", "definitely_nonexistent_fasta_file_12345.fa"};
        CHECK_THROWS_AS(parser.parse(3, argv, true), CliParseException);
    }
}

TEST_CASE("Stress ScoreModel - Extreme Calculations & Clamping") {
    // Zero penalties
    ScoreModel model_zero(0, 0);
    CHECK_EQ(model_zero.gapOpen(), 0);
    CHECK_EQ(model_zero.gapExtend(), 0);
    CHECK_EQ(model_zero.gapCost(0), 0);
    CHECK_EQ(model_zero.gapCost(10), 0);

    // Normal penalties
    ScoreModel model(-10, -1);
    CHECK_EQ(model.gapCost(-5), 0); // negative length returns 0
    CHECK_EQ(model.gapCost(0), 0);
    CHECK_EQ(model.gapCost(1), -11);
    CHECK_EQ(model.gapCost(1000), -1010);

    // Effective gap penalty occupancy bounds
    CHECK_NEAR(model.effectiveGapOpen(0.0), -10.0, 1e-6);
    CHECK_NEAR(model.effectiveGapOpen(0.5), -5.0, 1e-6);
    CHECK_NEAR(model.effectiveGapOpen(1.0), 0.0, 1e-6);
    // When gap_frequency > 1.0 (anomalous input), occupancy clamps to 0.0
    CHECK_NEAR(model.effectiveGapOpen(1.5), 0.0, 1e-6);
    CHECK_NEAR(model.effectiveGapExtend(1.5), 0.0, 1e-6);
}
