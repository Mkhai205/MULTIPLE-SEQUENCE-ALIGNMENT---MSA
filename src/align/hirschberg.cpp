#include "msa/align/hirschberg.hpp"
#include "msa/core/score_model.hpp"
#include "msa/core/profile.hpp"

#include <vector>
#include <string>
#include <algorithm>
#include <stdexcept>
#include <cmath>

namespace msa::align {

namespace {

// Generic Myers-Miller divide-and-conquer implementation
template <typename ScoreFunc>
class MyersMillerKernel {
public:
    MyersMillerKernel(
        ScoreFunc score_fn,
        int gap_open,
        int gap_extend,
        std::string_view chars1,
        std::string_view chars2
    ) : score_fn_(std::move(score_fn)),
        gap_open_(gap_open),
        gap_extend_(gap_extend),
        chars1_(chars1),
        chars2_(chars2) {}

    std::pair<std::string, std::string> align(size_t i1, size_t i2, size_t j1, size_t j2, bool tb, bool te) {
        size_t m = i2 - i1;
        size_t n = j2 - j1;

        if (m == 0) {
            return {std::string(n, '-'), std::string(chars2_.substr(j1, n))};
        }
        if (n == 0) {
            return {std::string(chars1_.substr(i1, m)), std::string(m, '-')};
        }

        // Base case: small dimension solves with full DP traceback in O(m) or O(n) space
        if (m <= 2 || n <= 2) {
            return solveBaseCase(i1, i2, j1, j2, tb, te);
        }

        size_t mid = i1 + m / 2;

        std::vector<int> fM, fIx, fIy;
        forwardPass(i1, mid, j1, j2, tb, fM, fIx, fIy);

        std::vector<int> bM, bIx, bIy;
        backwardPass(mid, i2, j1, j2, te, bM, bIx, bIy);

        const int NEG_INF = core::ScoreModel::NEG_INF;
        int max_C = NEG_INF;
        size_t j_C = 0;
        int max_D = NEG_INF;
        size_t j_D = 0;

        for (size_t col = 0; col <= n; ++col) {
            int c_fwd = std::max({fM[col], fIx[col], fIy[col]});
            int c_bwd = std::max({bM[col], bIx[col], bIy[col]});
            if (c_fwd > NEG_INF / 2 && c_bwd > NEG_INF / 2) {
                int score_c = c_fwd + c_bwd;
                if (score_c > max_C) {
                    max_C = score_c;
                    j_C = col;
                }
            }

            if (fIx[col] > NEG_INF / 2 && bIx[col] > NEG_INF / 2) {
                int score_d = (tb && te)
                    ? (fIx[col] + bIx[col] + gap_extend_)
                    : (fIx[col] + bIx[col] - gap_open_ + gap_extend_);
                if (score_d > max_D) {
                    max_D = score_d;
                    j_D = col;
                }
            }
        }

        size_t split_j = (max_C >= max_D) ? (j1 + j_C) : (j1 + j_D);

        if (max_C >= max_D) {
            auto left = align(i1, mid, j1, split_j, tb, false);
            auto right = align(mid, i2, split_j, j2, false, te);
            return {left.first + right.first, left.second + right.second};
        } else {
            auto left = align(i1, mid, j1, split_j, tb, true);
            auto right = align(mid, i2, split_j, j2, true, te);
            return {left.first + right.first, left.second + right.second};
        }
    }

private:
    ScoreFunc score_fn_;
    int gap_open_;
    int gap_extend_;
    std::string_view chars1_;
    std::string_view chars2_;

    std::pair<std::string, std::string> solveBaseCase(
        size_t i1, size_t i2, size_t j1, size_t j2, bool tb, bool te
    ) {
        size_t m = i2 - i1;
        size_t n = j2 - j1;
        size_t stride = n + 1;
        const int NEG_INF = core::ScoreModel::NEG_INF;

        std::vector<int> M((m + 1) * stride, NEG_INF);
        std::vector<int> Ix((m + 1) * stride, NEG_INF);
        std::vector<int> Iy((m + 1) * stride, NEG_INF);

        auto idx = [stride](size_t r, size_t c) noexcept -> size_t {
            return r * stride + c;
        };

        if (tb) {
            Ix[0] = 0;
        } else {
            M[0] = 0;
        }

        for (size_t i = 1; i <= m; ++i) {
            Ix[idx(i, 0)] = tb ? (static_cast<int>(i) * gap_extend_)
                               : (gap_open_ + static_cast<int>(i - 1) * gap_extend_);
        }
        for (size_t j = 1; j <= n; ++j) {
            Iy[idx(0, j)] = gap_open_ + static_cast<int>(j - 1) * gap_extend_;
        }

        for (size_t i = 1; i <= m; ++i) {
            for (size_t j = 1; j <= n; ++j) {
                size_t curr = idx(i, j);

                int diag_max = std::max({M[idx(i - 1, j - 1)], Ix[idx(i - 1, j - 1)], Iy[idx(i - 1, j - 1)]});
                M[curr] = (diag_max <= NEG_INF / 2)
                    ? NEG_INF
                    : (diag_max + score_fn_(i1 + i - 1, j1 + j - 1));

                int prev_m_x = M[idx(i - 1, j)];
                int prev_ix_x = Ix[idx(i - 1, j)];
                int prev_iy_x = Iy[idx(i - 1, j)];
                int ix_from_m = (prev_m_x <= NEG_INF / 2) ? NEG_INF : (prev_m_x + gap_open_);
                int ix_from_ix = (prev_ix_x <= NEG_INF / 2) ? NEG_INF : (prev_ix_x + gap_extend_);
                int ix_from_iy = (prev_iy_x <= NEG_INF / 2) ? NEG_INF : (prev_iy_x + gap_open_);
                Ix[curr] = std::max({ix_from_m, ix_from_ix, ix_from_iy});

                int prev_m_y = M[idx(i, j - 1)];
                int prev_iy_y = Iy[idx(i, j - 1)];
                int prev_ix_y = Ix[idx(i, j - 1)];
                int iy_from_m = (prev_m_y <= NEG_INF / 2) ? NEG_INF : (prev_m_y + gap_open_);
                int iy_from_iy = (prev_iy_y <= NEG_INF / 2) ? NEG_INF : (prev_iy_y + gap_extend_);
                int iy_from_ix = (prev_ix_y <= NEG_INF / 2) ? NEG_INF : (prev_ix_y + gap_open_);
                Iy[curr] = std::max({iy_from_m, iy_from_iy, iy_from_ix});
            }
        }

        size_t terminal = idx(m, n);
        enum class State { M, IX, IY } curr_state;

        if (te) {
            curr_state = State::IX;
        } else {
            int opt_score = std::max({M[terminal], Ix[terminal], Iy[terminal]});
            if (opt_score == M[terminal]) curr_state = State::M;
            else if (opt_score == Ix[terminal]) curr_state = State::IX;
            else curr_state = State::IY;
        }

        std::string out1;
        std::string out2;
        out1.reserve(m + n);
        out2.reserve(m + n);

        int curr_i = static_cast<int>(m);
        int curr_j = static_cast<int>(n);

        while (curr_i > 0 || curr_j > 0) {
            size_t curr_idx = idx(static_cast<size_t>(curr_i), static_cast<size_t>(curr_j));
            if (curr_state == State::M) {
                out1.push_back(chars1_[i1 + static_cast<size_t>(curr_i - 1)]);
                out2.push_back(chars2_[j1 + static_cast<size_t>(curr_j - 1)]);
                size_t diag = idx(static_cast<size_t>(curr_i - 1), static_cast<size_t>(curr_j - 1));
                int prev_max = std::max({M[diag], Ix[diag], Iy[diag]});
                if (M[diag] == prev_max) curr_state = State::M;
                else if (Ix[diag] == prev_max) curr_state = State::IX;
                else curr_state = State::IY;
                --curr_i;
                --curr_j;
            } else if (curr_state == State::IX) {
                out1.push_back(chars1_[i1 + static_cast<size_t>(curr_i - 1)]);
                out2.push_back('-');
                if (curr_j == 0) { --curr_i; continue; }
                size_t up_idx = idx(static_cast<size_t>(curr_i - 1), static_cast<size_t>(curr_j));
                int prev_ix = Ix[up_idx];
                int prev_m = M[up_idx];
                if (prev_ix > NEG_INF / 2 && Ix[curr_idx] == prev_ix + gap_extend_) {
                    curr_state = State::IX;
                } else if (prev_m > NEG_INF / 2 && Ix[curr_idx] == prev_m + gap_open_) {
                    curr_state = State::M;
                } else {
                    curr_state = State::IY;
                }
                --curr_i;
            } else {
                out1.push_back('-');
                out2.push_back(chars2_[j1 + static_cast<size_t>(curr_j - 1)]);
                if (curr_i == 0) { --curr_j; continue; }
                size_t left_idx = idx(static_cast<size_t>(curr_i), static_cast<size_t>(curr_j - 1));
                int prev_iy = Iy[left_idx];
                int prev_m = M[left_idx];
                if (prev_iy > NEG_INF / 2 && Iy[curr_idx] == prev_iy + gap_extend_) {
                    curr_state = State::IY;
                } else if (prev_m > NEG_INF / 2 && Iy[curr_idx] == prev_m + gap_open_) {
                    curr_state = State::M;
                } else {
                    curr_state = State::IX;
                }
                --curr_j;
            }
        }

        std::reverse(out1.begin(), out1.end());
        std::reverse(out2.begin(), out2.end());
        return {std::move(out1), std::move(out2)};
    }

    void forwardPass(
        size_t i1, size_t i2, size_t j1, size_t j2, bool tb,
        std::vector<int>& out_M, std::vector<int>& out_Ix, std::vector<int>& out_Iy
    ) {
        size_t m = i2 - i1;
        size_t n = j2 - j1;
        const int NEG_INF = core::ScoreModel::NEG_INF;

        out_M.assign(n + 1, NEG_INF);
        out_Ix.assign(n + 1, NEG_INF);
        out_Iy.assign(n + 1, NEG_INF);

        if (tb) {
            out_Ix[0] = 0;
        } else {
            out_M[0] = 0;
        }
        for (size_t j = 1; j <= n; ++j) {
            out_Iy[j] = gap_open_ + static_cast<int>(j - 1) * gap_extend_;
        }

        std::vector<int> prev_M(n + 1);
        std::vector<int> prev_Ix(n + 1);
        std::vector<int> prev_Iy(n + 1);

        for (size_t i = 1; i <= m; ++i) {
            prev_M = out_M;
            prev_Ix = out_Ix;
            prev_Iy = out_Iy;

            out_M[0] = NEG_INF;
            out_Ix[0] = tb ? (static_cast<int>(i) * gap_extend_)
                           : (gap_open_ + static_cast<int>(i - 1) * gap_extend_);
            out_Iy[0] = NEG_INF;

            for (size_t j = 1; j <= n; ++j) {
                int diag_max = std::max({prev_M[j - 1], prev_Ix[j - 1], prev_Iy[j - 1]});
                out_M[j] = (diag_max <= NEG_INF / 2)
                    ? NEG_INF
                    : (diag_max + score_fn_(i1 + i - 1, j1 + j - 1));

                int pxm = (prev_M[j] <= NEG_INF / 2) ? NEG_INF : (prev_M[j] + gap_open_);
                int pxx = (prev_Ix[j] <= NEG_INF / 2) ? NEG_INF : (prev_Ix[j] + gap_extend_);
                int pxy = (prev_Iy[j] <= NEG_INF / 2) ? NEG_INF : (prev_Iy[j] + gap_open_);
                out_Ix[j] = std::max({pxm, pxx, pxy});

                int pym = (out_M[j - 1] <= NEG_INF / 2) ? NEG_INF : (out_M[j - 1] + gap_open_);
                int pyy = (out_Iy[j - 1] <= NEG_INF / 2) ? NEG_INF : (out_Iy[j - 1] + gap_extend_);
                int pyx = (out_Ix[j - 1] <= NEG_INF / 2) ? NEG_INF : (out_Ix[j - 1] + gap_open_);
                out_Iy[j] = std::max({pym, pyy, pyx});
            }
        }
    }

    void backwardPass(
        size_t i1, size_t i2, size_t j1, size_t j2, bool te,
        std::vector<int>& out_M, std::vector<int>& out_Ix, std::vector<int>& out_Iy
    ) {
        size_t m = i2 - i1;
        size_t n = j2 - j1;
        const int NEG_INF = core::ScoreModel::NEG_INF;

        out_M.assign(n + 1, NEG_INF);
        out_Ix.assign(n + 1, NEG_INF);
        out_Iy.assign(n + 1, NEG_INF);

        if (te) {
            out_Ix[0] = 0;
        } else {
            out_M[0] = 0;
        }
        for (size_t j = 1; j <= n; ++j) {
            out_Iy[j] = gap_open_ + static_cast<int>(j - 1) * gap_extend_;
        }

        std::vector<int> prev_M(n + 1);
        std::vector<int> prev_Ix(n + 1);
        std::vector<int> prev_Iy(n + 1);

        for (size_t i = 1; i <= m; ++i) {
            prev_M = out_M;
            prev_Ix = out_Ix;
            prev_Iy = out_Iy;

            out_M[0] = NEG_INF;
            out_Ix[0] = te ? (static_cast<int>(i) * gap_extend_)
                           : (gap_open_ + static_cast<int>(i - 1) * gap_extend_);
            out_Iy[0] = NEG_INF;

            for (size_t j = 1; j <= n; ++j) {
                int diag_max = std::max({prev_M[j - 1], prev_Ix[j - 1], prev_Iy[j - 1]});
                out_M[j] = (diag_max <= NEG_INF / 2)
                    ? NEG_INF
                    : (diag_max + score_fn_(i2 - i, j2 - j));

                int pxm = (prev_M[j] <= NEG_INF / 2) ? NEG_INF : (prev_M[j] + gap_open_);
                int pxx = (prev_Ix[j] <= NEG_INF / 2) ? NEG_INF : (prev_Ix[j] + gap_extend_);
                int pxy = (prev_Iy[j] <= NEG_INF / 2) ? NEG_INF : (prev_Iy[j] + gap_open_);
                out_Ix[j] = std::max({pxm, pxx, pxy});

                int pym = (out_M[j - 1] <= NEG_INF / 2) ? NEG_INF : (out_M[j - 1] + gap_open_);
                int pyy = (out_Iy[j - 1] <= NEG_INF / 2) ? NEG_INF : (out_Iy[j - 1] + gap_extend_);
                int pyx = (out_Ix[j - 1] <= NEG_INF / 2) ? NEG_INF : (out_Ix[j - 1] + gap_open_);
                out_Iy[j] = std::max({pym, pyy, pyx});
            }
        }

        // Reverse back so index col corresponds to column col in sequence 2
        std::reverse(out_M.begin(), out_M.end());
        std::reverse(out_Ix.begin(), out_Ix.end());
        std::reverse(out_Iy.begin(), out_Iy.end());
    }
};

// Calculate alignment score from aligned string traces
int evaluateAlignmentScore(
    std::string_view a1,
    std::string_view a2,
    int gap_open,
    int gap_extend,
    const std::function<int(size_t, size_t)>& score_fn
) {
    int score = 0;
    bool in_gap1 = false;
    bool in_gap2 = false;
    size_t col1 = 0;
    size_t col2 = 0;

    for (size_t k = 0; k < a1.length(); ++k) {
        if (a1[k] == '-') {
            score += in_gap1 ? gap_extend : gap_open;
            in_gap1 = true;
            in_gap2 = false;
            ++col2;
        } else if (a2[k] == '-') {
            score += in_gap2 ? gap_extend : gap_open;
            in_gap2 = true;
            in_gap1 = false;
            ++col1;
        } else {
            score += score_fn(col1, col2);
            in_gap1 = false;
            in_gap2 = false;
            ++col1;
            ++col2;
        }
    }
    return score;
}

} // anonymous namespace

HirschbergAligner::HirschbergAligner(
    const core::ScoreModel& model,
    const core::Blosum62& matrix
) noexcept
    : model_(model), matrix_(matrix) {}

AlignmentResult HirschbergAligner::align(
    const core::Sequence& seq1,
    const core::Sequence& seq2
) const {
    return align(seq1.seq(), seq2.seq());
}

AlignmentResult HirschbergAligner::align(
    std::string_view seq1,
    std::string_view seq2
) const {
    size_t m = seq1.length();
    size_t n = seq2.length();

    if (m == 0 || n == 0) {
        throw std::invalid_argument("Sequences cannot be empty for Hirschberg alignment");
    }

    const auto& matrix = matrix_.get();
    int gap_open = model_.gapOpen();
    int gap_extend = model_.gapExtend();

    auto score_fn = [&](size_t i, size_t j) noexcept -> int {
        return matrix.score(seq1[i], seq2[j]);
    };

    MyersMillerKernel kernel(score_fn, gap_open, gap_extend, seq1, seq2);
    auto [aligned1, aligned2] = kernel.align(0, m, 0, n, false, false);

    AlignmentResult res;
    res.score = evaluateAlignmentScore(aligned1, aligned2, gap_open, gap_extend, score_fn);
    res.aligned_seq1 = std::move(aligned1);
    res.aligned_seq2 = std::move(aligned2);

    // Guaranteed linear space: 2 rows of size min(m, n) + 1
    size_t min_dim = std::min(m, n);
    res.peak_memory_bytes = 2ULL * (min_dim + 1) * sizeof(int);

    return res;
}

AlignmentResult HirschbergAligner::align(
    const core::Profile& p1,
    const core::Profile& p2
) const {
    size_t m = p1.length();
    size_t n = p2.length();

    if (m == 0 || n == 0) {
        throw std::invalid_argument("Profiles cannot be empty for Hirschberg alignment");
    }

    const auto& matrix = matrix_.get();
    int gap_open = model_.gapOpen();
    int gap_extend = model_.gapExtend();

    auto score_fn = [&](size_t i, size_t j) noexcept -> int {
        return static_cast<int>(std::round(core::Profile::scoreColumns(p1, i, p2, j, matrix)));
    };

    std::string c1 = p1.consensusSequence();
    std::string c2 = p2.consensusSequence();

    MyersMillerKernel kernel(score_fn, gap_open, gap_extend, c1, c2);
    auto [aligned1, aligned2] = kernel.align(0, m, 0, n, false, false);

    AlignmentResult res;
    res.score = evaluateAlignmentScore(aligned1, aligned2, gap_open, gap_extend, score_fn);
    res.aligned_seq1 = std::move(aligned1);
    res.aligned_seq2 = std::move(aligned2);

    size_t min_dim = std::min(m, n);
    res.peak_memory_bytes = 2ULL * (min_dim + 1) * sizeof(int);

    return res;
}

AlignmentResult hirschberg_align(
    const core::Sequence& seq1,
    const core::Sequence& seq2,
    const core::ScoreModel& model,
    const core::Blosum62& matrix
) {
    HirschbergAligner aligner(model, matrix);
    return aligner.align(seq1, seq2);
}

AlignmentResult hirschberg_align(
    std::string_view seq1,
    std::string_view seq2,
    const core::ScoreModel& model,
    const core::Blosum62& matrix
) {
    HirschbergAligner aligner(model, matrix);
    return aligner.align(seq1, seq2);
}

AlignmentResult hirschberg_align(
    const core::Profile& p1,
    const core::Profile& p2,
    const core::ScoreModel& model,
    const core::Blosum62& matrix
) {
    HirschbergAligner aligner(model, matrix);
    return aligner.align(p1, p2);
}

} // namespace msa::align
