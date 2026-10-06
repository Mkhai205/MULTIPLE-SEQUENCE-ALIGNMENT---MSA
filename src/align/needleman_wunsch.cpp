#include "msa/align/needleman_wunsch.hpp"

#include <vector>
#include <algorithm>
#include <stdexcept>

namespace msa::align {

NeedlemanWunsch::NeedlemanWunsch(
    const core::ScoreModel& model,
    const core::Blosum62& matrix
) noexcept
    : model_(model), matrix_(matrix) {}

AlignmentResult NeedlemanWunsch::align(
    const core::Sequence& seq1,
    const core::Sequence& seq2
) const {
    return align(seq1.seq(), seq2.seq());
}

AlignmentResult NeedlemanWunsch::align(
    std::string_view seq1,
    std::string_view seq2
) const {
    const int m = static_cast<int>(seq1.length());
    const int n = static_cast<int>(seq2.length());

    if (m == 0 || n == 0) {
        throw std::invalid_argument("Sequences cannot be empty for Gotoh alignment");
    }

    const int NEG_INF = core::ScoreModel::NEG_INF;
    const int gap_open = model_.gapOpen();
    const int gap_extend = model_.gapExtend();
    const auto& matrix = matrix_.get();

    const size_t stride = static_cast<size_t>(n + 1);
    const size_t total_cells = static_cast<size_t>(m + 1) * stride;

    // 1D flat buffers for cache locality and exact O(mn) allocation
    std::vector<int> M(total_cells, NEG_INF);
    std::vector<int> Ix(total_cells, NEG_INF);
    std::vector<int> Iy(total_cells, NEG_INF);

    auto idx = [stride](int r, int c) noexcept -> size_t {
        return static_cast<size_t>(r) * stride + static_cast<size_t>(c);
    };

    // 1. Boundary Initializations
    M[idx(0, 0)] = 0;
    Ix[idx(0, 0)] = NEG_INF;
    Iy[idx(0, 0)] = NEG_INF;

    for (int i = 1; i <= m; ++i) {
        Ix[idx(i, 0)] = gap_open + (i - 1) * gap_extend;
        M[idx(i, 0)] = NEG_INF;
        Iy[idx(i, 0)] = NEG_INF;
    }
    for (int j = 1; j <= n; ++j) {
        Iy[idx(0, j)] = gap_open + (j - 1) * gap_extend;
        M[idx(0, j)] = NEG_INF;
        Ix[idx(0, j)] = NEG_INF;
    }

    // 2. Dynamic Programming Matrix Fill
    for (int i = 1; i <= m; ++i) {
        const char char_a = seq1[static_cast<size_t>(i - 1)];
        const size_t row_offset = static_cast<size_t>(i) * stride;
        const size_t prev_row_offset = static_cast<size_t>(i - 1) * stride;

        for (int j = 1; j <= n; ++j) {
            const char char_b = seq2[static_cast<size_t>(j - 1)];
            const size_t curr = row_offset + static_cast<size_t>(j);

            // M(i, j): Match / substitution from diagonal
            const int diag_m  = M[prev_row_offset + static_cast<size_t>(j - 1)];
            const int diag_ix = Ix[prev_row_offset + static_cast<size_t>(j - 1)];
            const int diag_iy = Iy[prev_row_offset + static_cast<size_t>(j - 1)];
            const int diag_max = std::max({diag_m, diag_ix, diag_iy});

            M[curr] = (diag_max <= NEG_INF / 2)
                ? NEG_INF
                : (diag_max + matrix.score(char_a, char_b));

            // Ix(i, j): Vertical gap (insertion in seq1 / deletion in seq2)
            const int prev_m_x  = M[prev_row_offset + static_cast<size_t>(j)];
            const int prev_ix_x = Ix[prev_row_offset + static_cast<size_t>(j)];
            const int prev_iy_x = Iy[prev_row_offset + static_cast<size_t>(j)];
            const int ix_from_m  = (prev_m_x <= NEG_INF / 2) ? NEG_INF : (prev_m_x + gap_open);
            const int ix_from_ix = (prev_ix_x <= NEG_INF / 2) ? NEG_INF : (prev_ix_x + gap_extend);
            const int ix_from_iy = (prev_iy_x <= NEG_INF / 2) ? NEG_INF : (prev_iy_x + gap_open);
            Ix[curr] = std::max({ix_from_m, ix_from_ix, ix_from_iy});

            // Iy(i, j): Horizontal gap (deletion in seq1 / insertion in seq2)
            const int prev_m_y  = M[row_offset + static_cast<size_t>(j - 1)];
            const int prev_iy_y = Iy[row_offset + static_cast<size_t>(j - 1)];
            const int prev_ix_y = Ix[row_offset + static_cast<size_t>(j - 1)];
            const int iy_from_m  = (prev_m_y <= NEG_INF / 2) ? NEG_INF : (prev_m_y + gap_open);
            const int iy_from_iy = (prev_iy_y <= NEG_INF / 2) ? NEG_INF : (prev_iy_y + gap_extend);
            const int iy_from_ix = (prev_ix_y <= NEG_INF / 2) ? NEG_INF : (prev_ix_y + gap_open);
            Iy[curr] = std::max({iy_from_m, iy_from_iy, iy_from_ix});
        }
    }

    // 3. Terminal State Selection at (m, n)
    const size_t terminal = idx(m, n);
    const int opt_score = std::max({M[terminal], Ix[terminal], Iy[terminal]});

    enum class State { M, IX, IY } curr_state;
    if (opt_score == M[terminal]) {
        curr_state = State::M;
    } else if (opt_score == Ix[terminal]) {
        curr_state = State::IX;
    } else {
        curr_state = State::IY;
    }

    // 4. Traceback
    std::string out1;
    std::string out2;
    out1.reserve(static_cast<size_t>(m + n));
    out2.reserve(static_cast<size_t>(m + n));

    int i = m;
    int j = n;

    while (i > 0 || j > 0) {
        const size_t curr_idx = idx(i, j);
        if (curr_state == State::M) {
            out1.push_back(seq1[static_cast<size_t>(i - 1)]);
            out2.push_back(seq2[static_cast<size_t>(j - 1)]);
            const size_t diag = idx(i - 1, j - 1);
            const int prev_max = std::max({M[diag], Ix[diag], Iy[diag]});
            if (M[diag] == prev_max) {
                curr_state = State::M;
            } else if (Ix[diag] == prev_max) {
                curr_state = State::IX;
            } else {
                curr_state = State::IY;
            }
            --i;
            --j;
        } else if (curr_state == State::IX) {
            out1.push_back(seq1[static_cast<size_t>(i - 1)]);
            out2.push_back('-');
            if (j == 0) {
                --i;
                continue;
            }
            const size_t up_idx = idx(i - 1, j);
            const int prev_ix = Ix[up_idx];
            const int prev_m = M[up_idx];
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
            if (i == 0) {
                --j;
                continue;
            }
            const size_t left_idx = idx(i, j - 1);
            const int prev_iy = Iy[left_idx];
            const int prev_m = M[left_idx];
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

    AlignmentResult result;
    result.score = opt_score;
    result.aligned_seq1 = std::move(out1);
    result.aligned_seq2 = std::move(out2);
    result.peak_memory_bytes = 3 * sizeof(int) * total_cells +
                               (result.aligned_seq1.capacity() + result.aligned_seq2.capacity()) * sizeof(char);

    return result;
}

AlignmentResult needleman_wunsch_align(
    const core::Sequence& seq1,
    const core::Sequence& seq2,
    const core::ScoreModel& model,
    const core::Blosum62& matrix
) {
    NeedlemanWunsch aligner(model, matrix);
    return aligner.align(seq1, seq2);
}

AlignmentResult needleman_wunsch_align(
    std::string_view seq1,
    std::string_view seq2,
    const core::ScoreModel& model,
    const core::Blosum62& matrix
) {
    NeedlemanWunsch aligner(model, matrix);
    return aligner.align(seq1, seq2);
}

} // namespace msa::align
