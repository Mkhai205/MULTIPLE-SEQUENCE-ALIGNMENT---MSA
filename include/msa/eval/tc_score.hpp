#ifndef MSA_EVAL_TC_SCORE_HPP
#define MSA_EVAL_TC_SCORE_HPP

#include "msa/eval/balibase_parser.hpp"
#include "msa/core/profile.hpp"
#include <vector>
#include <string>

namespace msa::eval {

struct TCResult {
    double score{0.0};              // Normalized [0.0, 1.0]
    size_t correct_columns{0};
    size_t total_ref_columns{0};
};

class TCScore {
public:
    /// Calculate TC Score comparing test profile against BAliBASE reference
    [[nodiscard]] static TCResult compute(
        const BalibaseReference& reference,
        const core::Profile& test_profile,
        bool core_blocks_only = true
    );

    /// Calculate TC Score comparing two sets of aligned sequences directly
    [[nodiscard]] static TCResult compute(
        const std::vector<std::string>& ref_ids,
        const std::vector<std::string>& ref_seqs,
        const std::vector<std::string>& test_ids,
        const std::vector<std::string>& test_seqs,
        const std::vector<CoreBlock>& core_blocks = {},
        bool core_blocks_only = true
    );
};

} // namespace msa::eval

#endif // MSA_EVAL_TC_SCORE_HPP
