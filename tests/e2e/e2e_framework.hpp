#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <array>
#include <map>
#include <sstream>
#include <functional>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <cctype>
#include <algorithm>
#include <stdexcept>
#include <fstream>
#include <iomanip>
#include <memory>

#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <psapi.h>
#else
#include <sys/wait.h>
#include <unistd.h>
#endif

namespace msa::e2e {

// ============================================================================
// 1. Process Execution Result
// ============================================================================
struct ProcessResult {
    int exit_code{-1};
    std::string stdout_output;
    std::string stderr_output;
    bool execution_success{false};
};

// Execute external CLI process and capture output
inline ProcessResult RunProcess(const std::string& command) {
    ProcessResult result;
#ifdef _WIN32
    FILE* pipe = _popen(command.c_str(), "r");
#else
    FILE* pipe = popen(command.c_str(), "r");
#endif
    if (!pipe) {
        result.stderr_output = "Failed to launch process: " + command;
        result.execution_success = false;
        result.exit_code = -1;
        return result;
    }

    char buffer[512];
    std::string output;
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        output += buffer;
    }

#ifdef _WIN32
    result.exit_code = _pclose(pipe);
#else
    int status = pclose(pipe);
    result.exit_code = WIFEXITED(status) ? WEXITSTATUS(status) : -1;
#endif

    result.stdout_output = output;
    result.execution_success = (result.exit_code == 0);
    return result;
}

// ============================================================================
// 2. Reference BLOSUM62 Scoring Table (Authoritative Standard)
// ============================================================================
inline const std::string BLOSUM62_ORDER = "ARNDCQEGHILKMFPSTWYVBZX*";

inline const int BLOSUM62_MATRIX[24][24] = {
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

inline int ReferenceBlosum62Score(char a, char b) {
    char ua = static_cast<char>(std::toupper(static_cast<unsigned char>(a)));
    char ub = static_cast<char>(std::toupper(static_cast<unsigned char>(b)));
    if (ua == 'U') ua = 'C';
    if (ua == 'O') ua = 'K';
    if (ub == 'U') ub = 'C';
    if (ub == 'O') ub = 'K';

    auto pos_a = BLOSUM62_ORDER.find(ua);
    auto pos_b = BLOSUM62_ORDER.find(ub);
    if (pos_a == std::string::npos) pos_a = BLOSUM62_ORDER.find('X');
    if (pos_b == std::string::npos) pos_b = BLOSUM62_ORDER.find('X');

    return BLOSUM62_MATRIX[pos_a][pos_b];
}

// ============================================================================
// 3. Reference Gotoh (1982) 3-Matrix Aligner (Authoritative Oracle)
// ============================================================================
struct ReferenceAlignmentResult {
    int score{0};
    std::string aligned_seq1;
    std::string aligned_seq2;
};

inline ReferenceAlignmentResult ReferenceGotohAlign(
    const std::string& seq1,
    const std::string& seq2,
    int gap_open = -10,
    int gap_extend = -1)
{
    const int NEG_INF = -1'000'000'000;
    int m = static_cast<int>(seq1.length());
    int n = static_cast<int>(seq2.length());

    if (m == 0 || n == 0) {
        throw std::invalid_argument("Sequences cannot be empty for Gotoh alignment");
    }

    std::vector<std::vector<int>> M(m + 1, std::vector<int>(n + 1, NEG_INF));
    std::vector<std::vector<int>> Ix(m + 1, std::vector<int>(n + 1, NEG_INF));
    std::vector<std::vector<int>> Iy(m + 1, std::vector<int>(n + 1, NEG_INF));

    M[0][0] = 0;
    Ix[0][0] = NEG_INF;
    Iy[0][0] = NEG_INF;

    for (int i = 1; i <= m; ++i) {
        Ix[i][0] = gap_open + (i - 1) * gap_extend;
        M[i][0] = NEG_INF;
        Iy[i][0] = NEG_INF;
    }
    for (int j = 1; j <= n; ++j) {
        Iy[0][j] = gap_open + (j - 1) * gap_extend;
        M[0][j] = NEG_INF;
        Ix[0][j] = NEG_INF;
    }

    for (int i = 1; i <= m; ++i) {
        for (int j = 1; j <= n; ++j) {
            int diag_max = std::max({M[i-1][j-1], Ix[i-1][j-1], Iy[i-1][j-1]});
            M[i][j] = (diag_max <= NEG_INF / 2) ? NEG_INF : (diag_max + ReferenceBlosum62Score(seq1[i-1], seq2[j-1]));

            int ix_from_m  = (M[i-1][j] <= NEG_INF / 2) ? NEG_INF : (M[i-1][j] + gap_open);
            int ix_from_ix = (Ix[i-1][j] <= NEG_INF / 2) ? NEG_INF : (Ix[i-1][j] + gap_extend);
            int ix_from_iy = (Iy[i-1][j] <= NEG_INF / 2) ? NEG_INF : (Iy[i-1][j] + gap_open);
            Ix[i][j] = std::max({ix_from_m, ix_from_ix, ix_from_iy});

            int iy_from_m  = (M[i][j-1] <= NEG_INF / 2) ? NEG_INF : (M[i][j-1] + gap_open);
            int iy_from_iy = (Iy[i][j-1] <= NEG_INF / 2) ? NEG_INF : (Iy[i][j-1] + gap_extend);
            int iy_from_ix = (Ix[i][j-1] <= NEG_INF / 2) ? NEG_INF : (Ix[i][j-1] + gap_open);
            Iy[i][j] = std::max({iy_from_m, iy_from_iy, iy_from_ix});
        }
    }

    int opt_score = std::max({M[m][n], Ix[m][n], Iy[m][n]});
    enum State { STATE_M, STATE_IX, STATE_IY } curr_state;
    if (opt_score == M[m][n]) curr_state = STATE_M;
    else if (opt_score == Ix[m][n]) curr_state = STATE_IX;
    else curr_state = STATE_IY;

    std::string out1, out2;
    int i = m, j = n;

    while (i > 0 || j > 0) {
        if (curr_state == STATE_M) {
            out1.push_back(seq1[i - 1]);
            out2.push_back(seq2[j - 1]);
            int prev_max = std::max({M[i-1][j-1], Ix[i-1][j-1], Iy[i-1][j-1]});
            if (M[i-1][j-1] == prev_max) curr_state = STATE_M;
            else if (Ix[i-1][j-1] == prev_max) curr_state = STATE_IX;
            else curr_state = STATE_IY;
            --i; --j;
        } else if (curr_state == STATE_IX) {
            out1.push_back(seq1[i - 1]);
            out2.push_back('-');
            if (Ix[i][j] == M[i-1][j] + gap_open) curr_state = STATE_M;
            else if (Ix[i][j] == Ix[i-1][j] + gap_extend) curr_state = STATE_IX;
            else curr_state = STATE_IY;
            --i;
        } else {
            out1.push_back('-');
            out2.push_back(seq2[j - 1]);
            if (Iy[i][j] == M[i][j-1] + gap_open) curr_state = STATE_M;
            else if (Iy[i][j] == Iy[i][j-1] + gap_extend) curr_state = STATE_IY;
            else curr_state = STATE_IX;
            --j;
        }
    }

    std::reverse(out1.begin(), out1.end());
    std::reverse(out2.begin(), out2.end());

    ReferenceAlignmentResult res;
    res.score = opt_score;
    res.aligned_seq1 = out1;
    res.aligned_seq2 = out2;
    return res;
}

// ============================================================================
// 4. Reference Normalized Distance & UPGMA Formulas
// ============================================================================
inline double ReferenceNormalizedDistance(int s_ab, int s_aa, int s_bb) {
    int max_self = std::max(s_aa, s_bb);
    if (max_self <= 0) return 1.0;
    double d = 1.0 - (static_cast<double>(s_ab) / static_cast<double>(max_self));
    if (d < 0.0) d = 0.0;
    if (d > 2.0) d = 2.0;
    return d;
}

// ============================================================================
// 5. Reference BAliBASE Evaluation Metrics (SP and TC Scores)
// ============================================================================
struct CoreBlockInterval {
    int start_col{0}; // 0-indexed column in reference alignment
    int end_col{0};   // inclusive
};

struct ReferenceAlignmentData {
    std::vector<std::string> seq_ids;
    std::vector<std::string> aligned_seqs; // reference alignment (with gaps)
    std::vector<CoreBlockInterval> core_blocks;
};

inline double ReferenceComputeSP(
    const std::vector<std::string>& test_seqs,
    const ReferenceAlignmentData& ref_data)
{
    int num_seqs = static_cast<int>(ref_data.seq_ids.size());
    if (num_seqs < 2) return 1.0;

    int test_len = static_cast<int>(test_seqs[0].length());
    // Map test sequence (seq_idx, residue_pos) -> test_col
    std::vector<std::vector<int>> test_col_map(num_seqs);
    for (int i = 0; i < num_seqs; ++i) {
        for (int c = 0; c < test_len; ++c) {
            if (test_seqs[i][c] != '-') {
                test_col_map[i].push_back(c);
            }
        }
    }

    long long ref_pairs = 0;
    long long correct_pairs = 0;

    int ref_len = static_cast<int>(ref_data.aligned_seqs[0].length());
    // Map ref sequence (seq_idx, ref_col) -> residue_idx
    std::vector<std::vector<int>> ref_residue_idx(num_seqs, std::vector<int>(ref_len, -1));
    for (int i = 0; i < num_seqs; ++i) {
        int r_idx = 0;
        for (int c = 0; c < ref_len; ++c) {
            if (ref_data.aligned_seqs[i][c] != '-') {
                ref_residue_idx[i][c] = r_idx++;
            }
        }
    }

    for (const auto& block : ref_data.core_blocks) {
        for (int col = block.start_col; col <= block.end_col; ++col) {
            for (int i = 0; i < num_seqs; ++i) {
                int r_i = ref_residue_idx[i][col];
                if (r_i < 0) continue;
                for (int j = i + 1; j < num_seqs; ++j) {
                    int r_j = ref_residue_idx[j][col];
                    if (r_j < 0) continue;

                    ref_pairs++;
                    if (r_i < static_cast<int>(test_col_map[i].size()) &&
                        r_j < static_cast<int>(test_col_map[j].size())) {
                        if (test_col_map[i][r_i] == test_col_map[j][r_j]) {
                            correct_pairs++;
                        }
                    }
                }
            }
        }
    }

    return (ref_pairs == 0) ? 0.0 : (static_cast<double>(correct_pairs) / static_cast<double>(ref_pairs));
}

inline double ReferenceComputeTC(
    const std::vector<std::string>& test_seqs,
    const ReferenceAlignmentData& ref_data)
{
    int num_seqs = static_cast<int>(ref_data.seq_ids.size());
    if (num_seqs < 2) return 1.0;

    int test_len = static_cast<int>(test_seqs[0].length());
    std::vector<std::vector<int>> test_col_map(num_seqs);
    for (int i = 0; i < num_seqs; ++i) {
        for (int c = 0; c < test_len; ++c) {
            if (test_seqs[i][c] != '-') {
                test_col_map[i].push_back(c);
            }
        }
    }

    int ref_len = static_cast<int>(ref_data.aligned_seqs[0].length());
    std::vector<std::vector<int>> ref_residue_idx(num_seqs, std::vector<int>(ref_len, -1));
    for (int i = 0; i < num_seqs; ++i) {
        int r_idx = 0;
        for (int c = 0; c < ref_len; ++c) {
            if (ref_data.aligned_seqs[i][c] != '-') {
                ref_residue_idx[i][c] = r_idx++;
            }
        }
    }

    int core_col_count = 0;
    int correct_col_count = 0;

    for (const auto& block : ref_data.core_blocks) {
        for (int col = block.start_col; col <= block.end_col; ++col) {
            int non_gap_count = 0;
            for (int i = 0; i < num_seqs; ++i) {
                if (ref_residue_idx[i][col] >= 0) non_gap_count++;
            }
            if (non_gap_count < 2) continue;

            core_col_count++;
            int target_test_col = -1;
            bool col_perfect = true;

            for (int i = 0; i < num_seqs; ++i) {
                int r_i = ref_residue_idx[i][col];
                if (r_i >= 0) {
                    if (r_i >= static_cast<int>(test_col_map[i].size())) {
                        col_perfect = false;
                        break;
                    }
                    int t_col = test_col_map[i][r_i];
                    if (target_test_col == -1) {
                        target_test_col = t_col;
                    } else if (target_test_col != t_col) {
                        col_perfect = false;
                        break;
                    }
                }
            }

            if (col_perfect) {
                correct_col_count++;
            }
        }
    }

    return (core_col_count == 0) ? 0.0 : (static_cast<double>(correct_col_count) / static_cast<double>(core_col_count));
}

// ============================================================================
// 6. Invariant Validators (Sequence Conservation & Format Integrity)
// ============================================================================
inline bool ValidateSequenceConservation(const std::string& raw_seq, const std::string& aligned_seq) {
    std::string stripped;
    for (char c : aligned_seq) {
        if (c != '-') stripped.push_back(c);
    }
    return (stripped == raw_seq);
}

inline bool ValidateEqualAlignmentLengths(const std::vector<std::string>& aligned_seqs) {
    if (aligned_seqs.empty()) return true;
    size_t expected_len = aligned_seqs[0].length();
    for (const auto& s : aligned_seqs) {
        if (s.length() != expected_len) return false;
    }
    return true;
}

// ============================================================================
// 7. Test Framework Registry and Assertion Harness
// ============================================================================
class TestException : public std::runtime_error {
public:
    TestException(const std::string& msg, const char* file, int line)
        : std::runtime_error(msg + " at " + file + ":" + std::to_string(line)),
          file_(file), line_(line) {}

    const char* file() const noexcept { return file_; }
    int line() const noexcept { return line_; }
private:
    const char* file_;
    int line_;
};

#define E2E_ASSERT(condition, msg) \
    do { \
        if (!(condition)) { \
            throw ::msa::e2e::TestException("Assertion failed: (" #condition ") - " + std::string(msg), __FILE__, __LINE__); \
        } \
    } while (0)

#define E2E_ASSERT_EQ(actual, expected, msg) \
    do { \
        if (!((actual) == (expected))) { \
            std::ostringstream _oss; \
            _oss << "Expected [" << (expected) << "] but got [" << (actual) << "] - " << (msg); \
            throw ::msa::e2e::TestException(_oss.str(), __FILE__, __LINE__); \
        } \
    } while (0)

#define E2E_ASSERT_NEAR(actual, expected, tolerance, msg) \
    do { \
        if (std::fabs(static_cast<double>(actual) - static_cast<double>(expected)) > (tolerance)) { \
            std::ostringstream _oss; \
            _oss << "Expected [" << (expected) << " +/- " << (tolerance) << "] but got [" << (actual) << "] - " << (msg); \
            throw ::msa::e2e::TestException(_oss.str(), __FILE__, __LINE__); \
        } \
    } while (0)

#define E2E_ASSERT_THROWS(expression, ExceptionType, msg) \
    do { \
        bool _threw = false; \
        try { \
            expression; \
        } catch (const ExceptionType&) { \
            _threw = true; \
        } catch (...) { \
            throw ::msa::e2e::TestException("Expected " #ExceptionType " but caught different exception - " + std::string(msg), __FILE__, __LINE__); \
        } \
        if (!_threw) { \
            throw ::msa::e2e::TestException("Expected exception " #ExceptionType " was not thrown - " + std::string(msg), __FILE__, __LINE__); \
        } \
    } while (0)

struct TestCase {
    int tier{1};
    std::string feature_id;
    std::string test_id;
    std::string description;
    std::function<void()> func;
};

class TestRegistry {
public:
    static TestRegistry& Instance() {
        static TestRegistry instance;
        return instance;
    }

    void Register(int tier, const std::string& feature_id, const std::string& test_id, const std::string& desc, std::function<void()> func) {
        tests_.push_back({tier, feature_id, test_id, desc, func});
    }

    const std::vector<TestCase>& GetAllTests() const {
        return tests_;
    }

    std::vector<TestCase> GetTestsByTier(int tier) const {
        std::vector<TestCase> subset;
        for (const auto& t : tests_) {
            if (t.tier == tier) subset.push_back(t);
        }
        return subset;
    }

    size_t TotalCount() const { return tests_.size(); }

private:
    std::vector<TestCase> tests_;
};

struct TestRegistrar {
    TestRegistrar(int tier, const std::string& feature_id, const std::string& test_id, const std::string& desc, std::function<void()> func) {
        TestRegistry::Instance().Register(tier, feature_id, test_id, desc, func);
    }
};

#define E2E_TEST(tier_num, feature_id_str, test_id_str, desc_str) \
    static void test_func_##test_id_str(); \
    static ::msa::e2e::TestRegistrar registrar_##test_id_str(tier_num, feature_id_str, #test_id_str, desc_str, test_func_##test_id_str); \
    static void test_func_##test_id_str()

// ============================================================================
// 8. Embedded Benchmark & Reference Datasets
// ============================================================================
namespace datasets {

// Globin Family
inline const std::vector<std::pair<std::string, std::string>> GLOBIN_FAMILY = {
    {"HBA_HUMAN", "VLSPADKTNVKAAWGKVGAHAGEYGAEALERMFLSFPTTKTYFPHFDLSHGSAQVKGHGKKVADALTNAVAHVDDMPNALSALSDLHAHKLRVDPVNFKLLSHCLLVTLAAHLPAEFTPAVHASLDKFLASVSTVLTSKYR"},
    {"HBB_HUMAN", "VHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLSTPDAVMGNPKVKAHGKKVLGAFSDGLAHLDNLKGTFATLSELHCDKLHVDPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVAGVANALAHKYH"},
    {"MYG_HUMAN", "GLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASEDLKKHGATVLTALGGILKKKGHHEAEIKPLAQSHATKHKIPVKYLEFISECIIQVLQSKHPGDFGADAQGAMNKALELFRKDMASNYKELGFQG"},
    {"LGB1_SOYBN", "VAFTEKQDALVSSSFEAFKANIPQYSVVFYTSILEKAPAAKDLFSFLANGVDPTNPKLTGHAEKLFGLVRDSAGQLKASGTVVADAALGSVHAQKAVTDPQFVVVKEALLKTIKAAVGDKWSDELSRAWEVAYDELAAAIKKA"},
    {"NGB_HUMAN", "MERPEPELIRQSWRAVSRSPLEHGTVLFARLFALEPDLLPLFQYNCRQFSSPEDCLSSPEFLDHIRKVMLVIDAAVTNVEDLSSLEEYLASLGRKHRAVGVKLSSFSTVGESLLYMLEKCLGPAFTPATRAAWSQLYGAVVQAMSRGWDGE"}
};

// Kinase Catalytic Domain
inline const std::vector<std::pair<std::string, std::string>> KINASE_DOMAIN = {
    {"KAPCA_HUMAN", "FERIKTLGTGSFGRVMLVKHKETGNHYAMKILDKQKVVKLKQIEHTLNEKRILQAVNFPFLVKLEFSFKDNSNLYMVMEYVPGGEMFSHLRRIGRFSEPHARFYAAQIVLTFEYLHSLDLIYRDLKPENLLIDQQGYIQVTDFGFAKRVKGRTWTLCGTPEYLAPEIILSKGYNKAVDWWALGVLIYEMAAGYPPFFADQPIQIYEKIVSGKVRFPSHFSSDLKDLLRNLLQVDLTKRFGNLKNGVNDIKNHKWFATTDWIAIYQRKVEAPFIPKFKGPGDTSNFDDYEEEEIRVSINEKCGKEFTEF"},
    {"CDK2_HUMAN", "MENFQKVEKIGEGTYGVVYKARNKLTGEVVALKKIRLDTETEGVPSTAIREISLLKELNHPNIVKLLDVIHTENKLYLVFEFLHQDLKKFMDASALTGIPLPLIKSYLFQLLQGLAFCHSHRVLHRDLKPQNLLINTEGAIKLADFGLARAFGVPVRTYTHEVVTLWYRAPEILLGCKYYSTAVDIWSLGCIFAEMVTRRALFPGDSEIDQLFRIFRTLGTPDEVVWPGVTSMPDYKPSFPKWARQDFSKVVPPLDEDGRSLLSQMLHYDPNKRISAKAALAHPFFQDVTKPVPHLRL"},
    {"MK01_HUMAN", "MAAAAAQGGGGGEPRRTEGVGPGVPGEVEMVKGQPFDVGPRYTQLQYIGEGAYGMVSSAYDHVRKTRVAIKKISPFEHQTYCQRTLREIQILLRFRHENVIGIRDILRASTLEAMRDVYIVQDLMETDLYKLLKSQQLSNDHICYFLYQILRGLKYIHSANVLHRDLKPSNLLLNTTCDLKICDFGLARVADPDHDHTGFLTEYVATRWYRAPEIMLNSKGYTKSIDIWSVGCILAEMLSNRPIFPGKHYLDQLNHILGILGSPSQEDLNCIINLKARNYLLSLPHKNKVPWNRLFPNADSKALDLLDKMLTFNPHKRIEVEQALAHPYLEQYYDPSDEPIAEAPFKFDMELDDLPKEKLKELIFEETARFQPGYRS"},
    {"SRC_HUMAN", "MGSNKSKPKDASQRRRSLEPAENVHGAGGGAFPASQTPSKPASADGHRGPSAAFAPAAAEPKLFGGFNSSDTVTSPQRAGPLAGGVTTFVALYDYESRTETDLSFKKGERLQIVNNTEGDWWLAHSLSTGQTGYIPSNYVAPSDSIQAEEWYFGKITRRESERLLLNAENPRGTFLVRESETTKGAYCLSVSDFDNAKGLNVKHYKIRKLDSGGFYITSRTQFNSLQQLVAYYSKHADGLCHRLTTVCPTSKPQTQGLAKDAWEIPRESLRLEVKLGQGCFGEVWMGTWNGTTRVAIKTLKGTMSPEAFLQEAQVMKKLRHEKLVQLYAVVSEEPIYIVIEYMSKGSLLDFLKGETGKYLRLPQLVDMAAQIASGMAYVERMNYVHRDLRAANILVGENLVCKVADFGLARLIEDNEYTARQGAKFPIKWTAPEAALYGRFTIKSDVWSFGILLTELTTKGRVPYPGMVNREVLDQVERGYRMPCPPECPESLHDLMCQCWRKEPEERPTFEYLQAFLEDYFTSTEPQYQPGENL"}
};

// Zinc Finger C2H2
inline const std::vector<std::pair<std::string, std::string>> ZINC_FINGER = {
    {"ZF1_HUMAN", "PYKCPDCGKSFSQSSSLIRHQRTH"},
    {"ZF2_HUMAN", "PYKCNECGKVFSHSSNLIKHHRTH"},
    {"ZF3_HUMAN", "PYECHQCGKAFRHSSSLLRHHRTH"}
};

// Cytochrome C
inline const std::vector<std::pair<std::string, std::string>> CYTOCHROME_C = {
    {"CYC_HUMAN", "MGDVEKGKKIFIMKCSQCHTVEKGGKHKTGPNLHGLFGRKTGQAPGYSYTAANKNKGIIWGEDTLMEYLENPKKYIPGTKMIFVGIKKKEERADLIAYLKKATNE"},
    {"CYC_CHICK", "MGDIEKGKKIFVQKCSQCHTVEKGGKHKTGPNLHGLFGRKTGQAEGFSYTDANKNKGITWGEDTLMEYLENPKKYIPGTKMIFAGIKKKAERADLIAYLKQATAK"},
    {"CYC_DROME", "MGDVEKGKKLFVQRCAQCHTVEAGGKHKVGPNLHGLIGRKTGQAAGFAYTDANKAKGITWNEDTLFEYLENPKKYIPGTKMIFAGLKKPNERGDLIAYLKSATK"},
    {"CYC_YEAST", "TEFKAGSAKKGATLFKTRCELCHTVEKGGPHKVGPNLHGIFGRHSGQAEGYSYTDANIKKNVLWDENNMSEYLTNPKKYIPGTKMAFGGLKKEKDRNDLITYLKKACE"}
};

// BAliBASE RV11 Subset: BB11001 (Divergent < 20% identity)
inline const ReferenceAlignmentData BB11001_REF = {
    {"1aab_", "1j46_A", "1k99_A"},
    {
        "---GKGDPKKPRGKMSSYAFFVQTSREEHKKKHPDASVN-FAEFSKKCSERWKTMAKSEK-SKFEDMAKSDKARYDREMKNY---",
        "---MQDRVKRPMNAFIVWSRDQRRKMALENPRMRNSEIS-KQLGYQWKMLTEAEKWPFFQ-EAQKLQAMHREKYPNYKYRP---",
        "---MKKLKKHPDFPKKPLTPYFRFFMEKRAKYAKLHPEMSNLDLTKILSKKYKELPEKKKMKYIQDFQREKQEFERNLARFREDH"
    },
    { {3, 30}, {35, 78} } // Core blocks (intervals)
};

// BAliBASE RV12 Subset: BB12001 (Moderate 20-40% identity)
inline const ReferenceAlignmentData BB12001_REF = {
    {"1ivy_A", "1ac5_", "1ysc_A"},
    {
        "-APDQDEIQRLPGLAKQPSFRQYSGYLKSSG-SKHLHYWFVESQKDPENSPVVLWLNGGPGCSSLDGLLTEHGPFLVQPDGVTLEYNPYSWNLIANVLYLESPAGVGFSYSDDKFYATNDTEVAQSNFEALQDFFRLFPEYKNNKLFLTGESYAGIYIPTLAVLVMQDPSMNLQGLAVGNG--",
        "LPSSEEYKVAYELLPGLSEVPDPSNIPQMHAGHIPLRSEDADEQDSSDLEYFFWKFTNNDSNGNVDRPLIIWLNGGPGCSSMDGALVESGPFRVNSDGKLYLNEGSWISKGDLLFIDQPTGTGFSVEQNKDEGKIDKNKFDEDLEDVTKHFMDFLENYFKIFPEDLTRKIILSGESYAGQYIPFFANAILNHNKFSKIDGDTYDL-",
        "---KIKDPKILGIDPNVTQYTGYLDVEDED-KHFFFWTFESRNDPAKDPVILWLNGGPGCSSLTGLFFELGPSSIGPDLKPIGNPYSWNSNATVIFLDQPVNVGFSYSGSSGVSNTVAAGKDVYNFLELFFDQFPEYVNKGQDFHIAGESYAGHYIPVFASEILSHKDRNFNLTSVLIGNGLT"
    },
    { {20, 50}, {55, 95}, {100, 150} }
};

// BAliBASE RV20 Subset: BB20001 (Large family with core)
inline const ReferenceAlignmentData BB20001_REF = {
    {"1a75_A", "1bbt_ac", "1bbt_b", "1tmf_1", "1mec_1"},
    {
        "GSVTWPRPTD-AVVAPLSVAAGSFTITGFYRNPTGT-PVLPVTFTVGDTTTVTF---",
        "GAASWPRPVD-SVVAPLTVAAGSYTITGFYRNPTGT-PVLPVTFTVGDTTTVTF---",
        "GSVTWPRPTD-AVVAPLSVAAGSFTITGFYRNPTGT-PVLPVTFTVGDTTTVTF---",
        "GSVTWPRPTD-AVVAPLSVAAGSFTITGFYRNPTGT-PVLPVTFTVGDTTTVTF---",
        "GSVTWPRPTD-AVVAPLSVAAGSFTITGFYRNPTGT-PVLPVTFTVGDTTTVTF---"
    },
    { {0, 20}, {25, 45} }
};

} // namespace datasets

} // namespace msa::e2e
