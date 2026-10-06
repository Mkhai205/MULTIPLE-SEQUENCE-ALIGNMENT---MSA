#include "msa/eval/tc_score.hpp"

#include <unordered_map>
#include <algorithm>

namespace msa::eval {

TCResult TCScore::compute(
    const BalibaseReference& reference,
    const core::Profile& test_profile,
    bool core_blocks_only
) {
    std::vector<std::string> test_seqs;
    test_seqs.reserve(test_profile.numSequences());
    for (size_t i = 0; i < test_profile.numSequences(); ++i) {
        test_seqs.push_back(test_profile.getAlignedSequence(i));
    }

    return compute(
        reference.sequence_ids,
        reference.aligned_sequences,
        test_profile.sequenceIds(),
        test_seqs,
        reference.core_blocks,
        core_blocks_only
    );
}

TCResult TCScore::compute(
    const std::vector<std::string>& ref_ids,
    const std::vector<std::string>& ref_seqs,
    const std::vector<std::string>& test_ids,
    const std::vector<std::string>& test_seqs,
    const std::vector<CoreBlock>& core_blocks,
    bool core_blocks_only
) {
    TCResult result;
    size_t num_ref = ref_ids.size();
    if (num_ref < 2 || ref_seqs.empty() || test_seqs.empty()) {
        result.score = 1.0;
        return result;
    }

    // Map test sequence index to reference sequence index by ID
    std::unordered_map<std::string, size_t> id_to_ref;
    for (size_t i = 0; i < num_ref; ++i) {
        id_to_ref[ref_ids[i]] = i;
    }

    std::vector<int> test_to_ref(test_ids.size(), -1);
    for (size_t k = 0; k < test_ids.size(); ++k) {
        auto it = id_to_ref.find(test_ids[k]);
        if (it != id_to_ref.end()) {
            test_to_ref[k] = static_cast<int>(it->second);
        }
    }

    // Build residue index mapping for reference sequences: ref_res_pos[seq][c] = residue_idx
    size_t ref_len = ref_seqs[0].length();
    std::vector<std::vector<int>> ref_res_pos(num_ref, std::vector<int>(ref_len, -1));

    for (size_t i = 0; i < num_ref; ++i) {
        int r_idx = 0;
        for (size_t c = 0; c < ref_len; ++c) {
            char ch = ref_seqs[i][c];
            if (ch != '-' && ch != '.' && ch != '~') {
                ref_res_pos[i][c] = r_idx++;
            }
        }
    }

    // Build residue to column index mapping for test sequences: test_res_to_col[ref_seq_idx][res_idx] = col_in_test
    size_t test_len = test_seqs[0].length();
    size_t num_test = test_seqs.size();
    std::vector<std::unordered_map<int, size_t>> test_res_to_col(num_ref);

    for (size_t k = 0; k < num_test; ++k) {
        int ref_idx = test_to_ref[k];
        if (ref_idx < 0) continue;

        int r_idx = 0;
        for (size_t c = 0; c < test_len; ++c) {
            char ch = test_seqs[k][c];
            if (ch != '-' && ch != '.' && ch != '~') {
                test_res_to_col[static_cast<size_t>(ref_idx)][r_idx++] = c;
            }
        }
    }

    auto is_core = [&](size_t col) -> bool {
        if (!core_blocks_only || core_blocks.empty()) return true;
        for (const auto& cb : core_blocks) {
            if (col >= cb.start_col && col <= cb.end_col) return true;
        }
        return false;
    };

    size_t total_core_cols = 0;
    size_t correct_cols = 0;

    for (size_t c = 0; c < ref_len; ++c) {
        if (!is_core(c)) continue;

        // Check if all sequences have non-gap residues in this column
        bool all_sequences_have_residue = true;
        std::vector<int> residues(num_ref, -1);
        for (size_t i = 0; i < num_ref; ++i) {
            residues[i] = ref_res_pos[i][c];
            if (residues[i] < 0) {
                all_sequences_have_residue = false;
                break;
            }
        }

        if (!all_sequences_have_residue) {
            continue;
        }

        total_core_cols++;

        // Check if all residues align in the same column in test
        int expected_test_col = -1;
        bool column_matches = true;

        for (size_t i = 0; i < num_ref; ++i) {
            int r = residues[i];
            auto it = test_res_to_col[i].find(r);
            if (it == test_res_to_col[i].end()) {
                column_matches = false;
                break;
            }

            int actual_col = static_cast<int>(it->second);
            if (expected_test_col == -1) {
                expected_test_col = actual_col;
            } else if (actual_col != expected_test_col) {
                column_matches = false;
                break;
            }
        }

        if (column_matches) {
            correct_cols++;
        }
    }

    result.total_ref_columns = total_core_cols;
    result.correct_columns = correct_cols;
    result.score = (total_core_cols > 0)
        ? (static_cast<double>(correct_cols) / static_cast<double>(total_core_cols))
        : 1.0;
    if (result.score > 1.0) result.score = 1.0;
    if (result.score < 0.0) result.score = 0.0;

    return result;
}

} // namespace msa::eval
