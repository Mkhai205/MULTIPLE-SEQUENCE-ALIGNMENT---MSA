#include "msa/eval/sp_score.hpp"

#include <unordered_set>
#include <unordered_map>
#include <cstdint>
#include <algorithm>

namespace msa::eval {

SPResult SPScore::compute(
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

SPResult SPScore::compute(
    const std::vector<std::string>& ref_ids,
    const std::vector<std::string>& ref_seqs,
    const std::vector<std::string>& test_ids,
    const std::vector<std::string>& test_seqs,
    const std::vector<CoreBlock>& core_blocks,
    bool core_blocks_only
) {
    SPResult result;
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

    // Build residue index mapping for reference sequences
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

    auto is_core = [&](size_t col) -> bool {
        if (!core_blocks_only || core_blocks.empty()) return true;
        for (const auto& cb : core_blocks) {
            if (col >= cb.start_col && col <= cb.end_col) return true;
        }
        return false;
    };

    auto pack_pair = [](uint64_t i, uint64_t j, uint64_t ri, uint64_t rj) -> uint64_t {
        return (i << 48) | (j << 32) | (ri << 16) | rj;
    };

    std::unordered_set<uint64_t> ref_pairs;

    for (size_t c = 0; c < ref_len; ++c) {
        if (!is_core(c)) continue;

        for (size_t i = 0; i < num_ref; ++i) {
            int ri = ref_res_pos[i][c];
            if (ri < 0) continue;

            for (size_t j = i + 1; j < num_ref; ++j) {
                int rj = ref_res_pos[j][c];
                if (rj < 0) continue;

                ref_pairs.insert(pack_pair(i, j, static_cast<uint64_t>(ri), static_cast<uint64_t>(rj)));
            }
        }
    }

    result.total_ref_pairs = ref_pairs.size();
    if (result.total_ref_pairs == 0) {
        result.score = 1.0;
        return result;
    }

    // Build residue index mapping for test sequences
    size_t test_len = test_seqs[0].length();
    size_t num_test = test_seqs.size();
    std::vector<std::vector<int>> test_res_pos(num_test, std::vector<int>(test_len, -1));

    for (size_t k = 0; k < num_test; ++k) {
        int r_idx = 0;
        for (size_t c = 0; c < test_len; ++c) {
            char ch = test_seqs[k][c];
            if (ch != '-' && ch != '.' && ch != '~') {
                test_res_pos[k][c] = r_idx++;
            }
        }
    }

    // Check test alignment columns against reference pairs
    size_t correct = 0;
    std::unordered_set<uint64_t> counted_pairs;

    for (size_t c = 0; c < test_len; ++c) {
        for (size_t k1 = 0; k1 < num_test; ++k1) {
            int ref_i = test_to_ref[k1];
            if (ref_i < 0) continue;
            int ri = test_res_pos[k1][c];
            if (ri < 0) continue;

            for (size_t k2 = k1 + 1; k2 < num_test; ++k2) {
                int ref_j = test_to_ref[k2];
                if (ref_j < 0) continue;
                int rj = test_res_pos[k2][c];
                if (rj < 0) continue;

                size_t u = static_cast<size_t>(ref_i);
                size_t v = static_cast<size_t>(ref_j);
                uint64_t ru = static_cast<uint64_t>(ri);
                uint64_t rv = static_cast<uint64_t>(rj);
                if (u > v) {
                    std::swap(u, v);
                    std::swap(ru, rv);
                }

                uint64_t key = pack_pair(u, v, ru, rv);
                if (ref_pairs.find(key) != ref_pairs.end()) {
                    if (counted_pairs.insert(key).second) {
                        correct++;
                    }
                }
            }
        }
    }

    result.correct_pairs = correct;
    result.score = static_cast<double>(correct) / static_cast<double>(result.total_ref_pairs);
    if (result.score > 1.0) result.score = 1.0;
    if (result.score < 0.0) result.score = 0.0;

    return result;
}

} // namespace msa::eval
