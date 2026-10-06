#ifndef MSA_EVAL_BALIBASE_PARSER_HPP
#define MSA_EVAL_BALIBASE_PARSER_HPP

#include "msa/core/sequence.hpp"
#include <string>
#include <vector>
#include <istream>
#include <filesystem>

namespace msa::eval {

struct CoreBlock {
    size_t start_col{0};
    size_t end_col{0}; // inclusive: [start_col, end_col]
};

struct BalibaseReference {
    std::string id;
    std::vector<std::string> sequence_ids;
    std::vector<std::string> aligned_sequences;
    std::vector<CoreBlock> core_blocks;

    [[nodiscard]] size_t numSequences() const noexcept { return sequence_ids.size(); }
    [[nodiscard]] size_t length() const noexcept {
        return aligned_sequences.empty() ? 0 : aligned_sequences[0].length();
    }
    [[nodiscard]] bool empty() const noexcept { return sequence_ids.empty(); }

    [[nodiscard]] bool isCoreColumn(size_t col) const noexcept;
    [[nodiscard]] size_t numCoreColumns() const noexcept;

    /// Extract unaligned sequences (with gaps stripped) to run progressive aligner
    [[nodiscard]] std::vector<core::Sequence> extractRawSequences() const;
};

class BalibaseParser {
public:
    /// Parse MSF format from file or stream
    [[nodiscard]] static BalibaseReference parseMSF(const std::filesystem::path& path);
    [[nodiscard]] static BalibaseReference parseMSF(std::istream& stream, const std::string& id = "");

    /// Parse aligned FASTA format as reference
    [[nodiscard]] static BalibaseReference parseFASTA(const std::filesystem::path& path);
    [[nodiscard]] static BalibaseReference parseFASTA(std::istream& stream, const std::string& id = "");

    /// Automatically extract core blocks from uppercase residues or core criteria
    static void detectCoreBlocksFromResidues(BalibaseReference& ref);
};

} // namespace msa::eval

#endif // MSA_EVAL_BALIBASE_PARSER_HPP
