#include "msa/parallel/wavefront.hpp"
#include "msa/core/score_model.hpp"

#include <vector>
#include <algorithm>
#include <stdexcept>

#if defined(_OPENMP)
#include <omp.h>
#endif

namespace msa::parallel {

int wavefront_gotoh_score(
    std::string_view seq1,
    std::string_view seq2,
    const core::ScoreModel& model,
    const core::Blosum62& matrix,
    int threshold
) {
    const size_t m = seq1.length();
    const size_t n = seq2.length();

    if (m == 0 || n == 0) {
        throw std::invalid_argument("Sequences cannot be empty for wavefront alignment");
    }

    const int NEG_INF = core::ScoreModel::NEG_INF;
    const int gap_open = model.gapOpen();
    const int gap_extend = model.gapExtend();

    // 3 rotating ring buffers of size (n + 1) for strictly linear O(n) space
    std::vector<std::vector<int>> M(3, std::vector<int>(n + 1, NEG_INF));
    std::vector<std::vector<int>> Ix(3, std::vector<int>(n + 1, NEG_INF));
    std::vector<std::vector<int>> Iy(3, std::vector<int>(n + 1, NEG_INF));

    // Full 1D boundary tables for column 0 and row 0
    std::vector<int> col0_Ix(m + 1, NEG_INF);
    std::vector<int> row0_Iy(n + 1, NEG_INF);
    for (size_t i = 1; i <= m; ++i) {
        col0_Ix[i] = gap_open + static_cast<int>(i - 1) * gap_extend;
    }
    for (size_t j = 1; j <= n; ++j) {
        row0_Iy[j] = gap_open + static_cast<int>(j - 1) * gap_extend;
    }

    // Diagonal 0: (0, 0)
    M[0][0] = 0;
    Ix[0][0] = NEG_INF;
    Iy[0][0] = NEG_INF;

    // Diagonal 1: (1, 0) and (0, 1)
    M[1][0] = NEG_INF;
    Ix[1][0] = col0_Ix[1];
    Iy[1][0] = NEG_INF;

    M[1][1] = NEG_INF;
    Ix[1][1] = NEG_INF;
    Iy[1][1] = row0_Iy[1];

    // Anti-diagonals d = 2 to m + n
    for (size_t d = 2; d <= m + n; ++d) {
        size_t buf_curr = d % 3;
        size_t buf_prev1 = (d + 2) % 3; // (d - 1) % 3
        size_t buf_prev2 = (d + 1) % 3; // (d - 2) % 3

        // Boundary cells on this diagonal:
        // (d, 0) if d <= m
        if (d <= m) {
            M[buf_curr][0] = NEG_INF;
            Ix[buf_curr][0] = col0_Ix[d];
            Iy[buf_curr][0] = NEG_INF;
        }

        size_t min_i = (d > n) ? (d - n) : 1;
        size_t max_i = (d > m + 1) ? m : (d - 1);

        if (min_i <= max_i) {
            size_t num_cells = max_i - min_i + 1;

#if defined(_OPENMP)
            if (num_cells >= static_cast<size_t>(threshold)) {
                #pragma omp parallel for schedule(static)
                for (int idx_i = static_cast<int>(min_i); idx_i <= static_cast<int>(max_i); ++idx_i) {
                    size_t i = static_cast<size_t>(idx_i);
                    size_t j = d - i;
                    char a = seq1[i - 1];
                    char b = seq2[j - 1];

                    // Diagonal predecessor: (i-1, j-1)
                    int diag_m = (i == 1 && j == 1) ? M[0][0] : ((i == 1 || j == 1) ? NEG_INF : M[buf_prev2][j - 1]);
                    int diag_ix = (i == 1 && j == 1) ? Ix[0][0] : ((i == 1 || j == 1) ? (j == 1 ? col0_Ix[i - 1] : NEG_INF) : Ix[buf_prev2][j - 1]);
                    int diag_iy = (i == 1 && j == 1) ? Iy[0][0] : ((i == 1 || j == 1) ? (i == 1 ? row0_Iy[j - 1] : NEG_INF) : Iy[buf_prev2][j - 1]);
                    int diag_max = std::max({diag_m, diag_ix, diag_iy});

                    M[buf_curr][j] = (diag_max <= NEG_INF / 2)
                        ? NEG_INF
                        : (diag_max + matrix.score(a, b));

                    // Up predecessor: (i-1, j)
                    int prev_m_x = (i == 1) ? NEG_INF : M[buf_prev1][j];
                    int prev_ix_x = (i == 1) ? NEG_INF : (j == 0 ? col0_Ix[i - 1] : Ix[buf_prev1][j]);
                    int prev_iy_x = (i == 1) ? row0_Iy[j] : Iy[buf_prev1][j];
                    int ix_m = (prev_m_x <= NEG_INF / 2) ? NEG_INF : (prev_m_x + gap_open);
                    int ix_ix = (prev_ix_x <= NEG_INF / 2) ? NEG_INF : (prev_ix_x + gap_extend);
                    int ix_iy = (prev_iy_x <= NEG_INF / 2) ? NEG_INF : (prev_iy_x + gap_open);
                    Ix[buf_curr][j] = std::max({ix_m, ix_ix, ix_iy});

                    // Left predecessor: (i, j-1)
                    int prev_m_y = (j == 1) ? NEG_INF : M[buf_prev1][j - 1];
                    int prev_iy_y = (j == 1) ? NEG_INF : (i == 0 ? row0_Iy[j - 1] : Iy[buf_prev1][j - 1]);
                    int prev_ix_y = (j == 1) ? col0_Ix[i] : Ix[buf_prev1][j - 1];
                    int iy_m = (prev_m_y <= NEG_INF / 2) ? NEG_INF : (prev_m_y + gap_open);
                    int iy_iy = (prev_iy_y <= NEG_INF / 2) ? NEG_INF : (prev_iy_y + gap_extend);
                    int iy_ix = (prev_ix_y <= NEG_INF / 2) ? NEG_INF : (prev_ix_y + gap_open);
                    Iy[buf_curr][j] = std::max({iy_m, iy_iy, iy_ix});
                }
            } else
#endif
            {
                for (size_t i = min_i; i <= max_i; ++i) {
                    size_t j = d - i;
                    char a = seq1[i - 1];
                    char b = seq2[j - 1];

                    int diag_m = (i == 1 && j == 1) ? M[0][0] : ((i == 1 || j == 1) ? NEG_INF : M[buf_prev2][j - 1]);
                    int diag_ix = (i == 1 && j == 1) ? Ix[0][0] : ((i == 1 || j == 1) ? (j == 1 ? col0_Ix[i - 1] : NEG_INF) : Ix[buf_prev2][j - 1]);
                    int diag_iy = (i == 1 && j == 1) ? Iy[0][0] : ((i == 1 || j == 1) ? (i == 1 ? row0_Iy[j - 1] : NEG_INF) : Iy[buf_prev2][j - 1]);
                    int diag_max = std::max({diag_m, diag_ix, diag_iy});

                    M[buf_curr][j] = (diag_max <= NEG_INF / 2)
                        ? NEG_INF
                        : (diag_max + matrix.score(a, b));

                    int prev_m_x = (i == 1) ? NEG_INF : M[buf_prev1][j];
                    int prev_ix_x = (i == 1) ? NEG_INF : (j == 0 ? col0_Ix[i - 1] : Ix[buf_prev1][j]);
                    int prev_iy_x = (i == 1) ? row0_Iy[j] : Iy[buf_prev1][j];
                    int ix_m = (prev_m_x <= NEG_INF / 2) ? NEG_INF : (prev_m_x + gap_open);
                    int ix_ix = (prev_ix_x <= NEG_INF / 2) ? NEG_INF : (prev_ix_x + gap_extend);
                    int ix_iy = (prev_iy_x <= NEG_INF / 2) ? NEG_INF : (prev_iy_x + gap_open);
                    Ix[buf_curr][j] = std::max({ix_m, ix_ix, ix_iy});

                    int prev_m_y = (j == 1) ? NEG_INF : M[buf_prev1][j - 1];
                    int prev_iy_y = (j == 1) ? NEG_INF : (i == 0 ? row0_Iy[j - 1] : Iy[buf_prev1][j - 1]);
                    int prev_ix_y = (j == 1) ? col0_Ix[i] : Ix[buf_prev1][j - 1];
                    int iy_m = (prev_m_y <= NEG_INF / 2) ? NEG_INF : (prev_m_y + gap_open);
                    int iy_iy = (prev_iy_y <= NEG_INF / 2) ? NEG_INF : (prev_iy_y + gap_extend);
                    int iy_ix = (prev_ix_y <= NEG_INF / 2) ? NEG_INF : (prev_ix_y + gap_open);
                    Iy[buf_curr][j] = std::max({iy_m, iy_iy, iy_ix});
                }
            }
        }
    }

    size_t term_buf = (m + n) % 3;
    return std::max({M[term_buf][n], Ix[term_buf][n], Iy[term_buf][n]});
}

align::AlignmentResult wavefront_gotoh_align(
    std::string_view seq1,
    std::string_view seq2,
    const core::ScoreModel& model,
    const core::Blosum62& matrix,
    int threshold
) {
    const size_t m = seq1.length();
    const size_t n = seq2.length();

    if (m == 0 || n == 0) {
        throw std::invalid_argument("Sequences cannot be empty for wavefront alignment");
    }

    const int NEG_INF = core::ScoreModel::NEG_INF;
    const int gap_open = model.gapOpen();
    const int gap_extend = model.gapExtend();

    const size_t stride = n + 1;
    const size_t total_cells = (m + 1) * stride;

    std::vector<int> M(total_cells, NEG_INF);
    std::vector<int> Ix(total_cells, NEG_INF);
    std::vector<int> Iy(total_cells, NEG_INF);

    auto idx = [stride](size_t r, size_t c) noexcept -> size_t {
        return r * stride + c;
    };

    M[0] = 0;
    for (size_t i = 1; i <= m; ++i) {
        Ix[idx(i, 0)] = gap_open + static_cast<int>(i - 1) * gap_extend;
    }
    for (size_t j = 1; j <= n; ++j) {
        Iy[idx(0, j)] = gap_open + static_cast<int>(j - 1) * gap_extend;
    }

    // Wavefront execution across anti-diagonals
    for (size_t d = 2; d <= m + n; ++d) {
        size_t min_i = (d > n) ? (d - n) : 1;
        size_t max_i = (d > m + 1) ? m : (d - 1);

        if (min_i <= max_i) {
            size_t num_cells = max_i - min_i + 1;

#if defined(_OPENMP)
            if (num_cells >= static_cast<size_t>(threshold)) {
                #pragma omp parallel for schedule(static)
                for (int idx_i = static_cast<int>(min_i); idx_i <= static_cast<int>(max_i); ++idx_i) {
                    size_t i = static_cast<size_t>(idx_i);
                    size_t j = d - i;
                    size_t curr = idx(i, j);

                    int diag_m = M[idx(i - 1, j - 1)];
                    int diag_ix = Ix[idx(i - 1, j - 1)];
                    int diag_iy = Iy[idx(i - 1, j - 1)];
                    int diag_max = std::max({diag_m, diag_ix, diag_iy});

                    M[curr] = (diag_max <= NEG_INF / 2)
                        ? NEG_INF
                        : (diag_max + matrix.score(seq1[i - 1], seq2[j - 1]));

                    int prev_m_x = M[idx(i - 1, j)];
                    int prev_ix_x = Ix[idx(i - 1, j)];
                    int prev_iy_x = Iy[idx(i - 1, j)];
                    int ix_m = (prev_m_x <= NEG_INF / 2) ? NEG_INF : (prev_m_x + gap_open);
                    int ix_ix = (prev_ix_x <= NEG_INF / 2) ? NEG_INF : (prev_ix_x + gap_extend);
                    int ix_iy = (prev_iy_x <= NEG_INF / 2) ? NEG_INF : (prev_iy_x + gap_open);
                    Ix[curr] = std::max({ix_m, ix_ix, ix_iy});

                    int prev_m_y = M[idx(i, j - 1)];
                    int prev_iy_y = Iy[idx(i, j - 1)];
                    int prev_ix_y = Ix[idx(i, j - 1)];
                    int iy_m = (prev_m_y <= NEG_INF / 2) ? NEG_INF : (prev_m_y + gap_open);
                    int iy_iy = (prev_iy_y <= NEG_INF / 2) ? NEG_INF : (prev_iy_y + gap_extend);
                    int iy_ix = (prev_ix_y <= NEG_INF / 2) ? NEG_INF : (prev_ix_y + gap_open);
                    Iy[curr] = std::max({iy_m, iy_iy, iy_ix});
                }
            } else
#endif
            {
                for (size_t i = min_i; i <= max_i; ++i) {
                    size_t j = d - i;
                    size_t curr = idx(i, j);

                    int diag_m = M[idx(i - 1, j - 1)];
                    int diag_ix = Ix[idx(i - 1, j - 1)];
                    int diag_iy = Iy[idx(i - 1, j - 1)];
                    int diag_max = std::max({diag_m, diag_ix, diag_iy});

                    M[curr] = (diag_max <= NEG_INF / 2)
                        ? NEG_INF
                        : (diag_max + matrix.score(seq1[i - 1], seq2[j - 1]));

                    int prev_m_x = M[idx(i - 1, j)];
                    int prev_ix_x = Ix[idx(i - 1, j)];
                    int prev_iy_x = Iy[idx(i - 1, j)];
                    int ix_m = (prev_m_x <= NEG_INF / 2) ? NEG_INF : (prev_m_x + gap_open);
                    int ix_ix = (prev_ix_x <= NEG_INF / 2) ? NEG_INF : (prev_ix_x + gap_extend);
                    int ix_iy = (prev_iy_x <= NEG_INF / 2) ? NEG_INF : (prev_iy_x + gap_open);
                    Ix[curr] = std::max({ix_m, ix_ix, ix_iy});

                    int prev_m_y = M[idx(i, j - 1)];
                    int prev_iy_y = Iy[idx(i, j - 1)];
                    int prev_ix_y = Ix[idx(i, j - 1)];
                    int iy_m = (prev_m_y <= NEG_INF / 2) ? NEG_INF : (prev_m_y + gap_open);
                    int iy_iy = (prev_iy_y <= NEG_INF / 2) ? NEG_INF : (prev_iy_y + gap_extend);
                    int iy_ix = (prev_ix_y <= NEG_INF / 2) ? NEG_INF : (prev_ix_y + gap_open);
                    Iy[curr] = std::max({iy_m, iy_iy, iy_ix});
                }
            }
        }
    }

    // Traceback
    size_t terminal = idx(m, n);
    int opt_score = std::max({M[terminal], Ix[terminal], Iy[terminal]});

    enum class State { M, IX, IY } curr_state;
    if (opt_score == M[terminal]) curr_state = State::M;
    else if (opt_score == Ix[terminal]) curr_state = State::IX;
    else curr_state = State::IY;

    std::string out1, out2;
    out1.reserve(m + n);
    out2.reserve(m + n);

    int i = static_cast<int>(m);
    int j = static_cast<int>(n);

    while (i > 0 || j > 0) {
        size_t curr_idx = idx(static_cast<size_t>(i), static_cast<size_t>(j));
        if (curr_state == State::M) {
            out1.push_back(seq1[static_cast<size_t>(i - 1)]);
            out2.push_back(seq2[static_cast<size_t>(j - 1)]);
            size_t diag = idx(static_cast<size_t>(i - 1), static_cast<size_t>(j - 1));
            int prev_max = std::max({M[diag], Ix[diag], Iy[diag]});
            if (M[diag] == prev_max) curr_state = State::M;
            else if (Ix[diag] == prev_max) curr_state = State::IX;
            else curr_state = State::IY;
            --i; --j;
        } else if (curr_state == State::IX) {
            out1.push_back(seq1[static_cast<size_t>(i - 1)]);
            out2.push_back('-');
            if (j == 0) { --i; continue; }
            size_t up_idx = idx(static_cast<size_t>(i - 1), static_cast<size_t>(j));
            int prev_ix = Ix[up_idx];
            int prev_m = M[up_idx];
            if (prev_ix > NEG_INF / 2 && Ix[curr_idx] == prev_ix + gap_extend) {
                curr_state = State::IX;
            } else if (prev_m > NEG_INF / 2 && Ix[curr_idx] == prev_m + gap_open) {
                curr_state = State::M;
            } else {
                curr_state = State::IY;
            }
            --i;
        } else {
            out1.push_back('-');
            out2.push_back(seq2[static_cast<size_t>(j - 1)]);
            if (i == 0) { --j; continue; }
            size_t left_idx = idx(static_cast<size_t>(i), static_cast<size_t>(j - 1));
            int prev_iy = Iy[left_idx];
            int prev_m = M[left_idx];
            if (prev_iy > NEG_INF / 2 && Iy[curr_idx] == prev_iy + gap_extend) {
                curr_state = State::IY;
            } else if (prev_m > NEG_INF / 2 && Iy[curr_idx] == prev_m + gap_open) {
                curr_state = State::M;
            } else {
                curr_state = State::IX;
            }
            --j;
        }
    }

    std::reverse(out1.begin(), out1.end());
    std::reverse(out2.begin(), out2.end());

    align::AlignmentResult res;
    res.score = opt_score;
    res.aligned_seq1 = std::move(out1);
    res.aligned_seq2 = std::move(out2);
    res.peak_memory_bytes = 3 * sizeof(int) * total_cells;

    return res;
}

} // namespace msa::parallel
