#ifndef MSA_IO_FASTA_IO_HPP
#define MSA_IO_FASTA_IO_HPP

#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <cstdint>
#include <array>
#include "msa/core/sequence.hpp"

namespace msa::io {

enum CharClass : uint8_t {
    CHAR_INVALID    = 0x00,
    CHAR_STANDARD   = 0x01, // 20 canonical amino acids
    CHAR_AMBIGUITY  = 0x02, // B, Z, X, *
    CHAR_EXTENDED   = 0x04, // U, O, J
    CHAR_GAP        = 0x08, // -, .
    CHAR_WHITESPACE = 0x10  // ' ', '\t', '\r', '\n'
};

enum class ValidationMode {
    STRICT_CANONICAL,   // Only 20 standard amino acids
    STANDARD_BLOSUM62,  // 20 standard + B, Z, X, *
    PERMISSIVE,         // BLOSUM62 + U, O, J + gaps
    ALIGNED_FASTA       // BLOSUM62 + '-' gaps allowed
};

class ResidueValidator {
public:
    static const std::array<uint8_t, 256> CHAR_TABLE;
    static const std::array<char, 256> NORMALIZE_UPPER;

    [[nodiscard]] static bool is_valid(char c, ValidationMode mode) noexcept;
    [[nodiscard]] static char normalize(char c) noexcept;
};

class FastaParseException : public std::runtime_error {
public:
    FastaParseException(const std::string& message, size_t line = 0, size_t column = 0, const std::string& seq_id = "")
        : std::runtime_error(format_msg(message, line, column, seq_id)),
          line_(line), column_(column), seq_id_(seq_id) {}

    [[nodiscard]] size_t line() const noexcept { return line_; }
    [[nodiscard]] size_t column() const noexcept { return column_; }
    [[nodiscard]] const std::string& seq_id() const noexcept { return seq_id_; }

private:
    size_t line_;
    size_t column_;
    std::string seq_id_;

    static std::string format_msg(const std::string& msg, size_t line, size_t col, const std::string& id) {
        if (line == 0) return "[FastaParser Error] " + msg;
        std::string res = "[FastaParser Error at line " + std::to_string(line);
        if (col > 0) res += ", col " + std::to_string(col);
        if (!id.empty()) res += " (seq: '" + id + "')";
        res += "]: " + msg;
        return res;
    }
};

class FastaParser {
public:
    struct Options {
        ValidationMode mode = ValidationMode::STANDARD_BLOSUM62;
        bool allow_empty_sequences = false;
        bool check_duplicate_ids = true;
        bool trim_whitespace = true;
    };

    /// Parse sequences from a file path
    [[nodiscard]] static std::vector<msa::core::Sequence> read_file(
        const std::filesystem::path& filepath,
        const Options& options = Options{}
    );

    /// Parse sequences from an input stream
    [[nodiscard]] static std::vector<msa::core::Sequence> read_stream(
        std::istream& is,
        const Options& options = Options{}
    );

    /// Parse sequences from an in-memory string
    [[nodiscard]] static std::vector<msa::core::Sequence> read_string(
        std::string_view fasta_content,
        const Options& options = Options{}
    );
};

class FastaWriter {
public:
    struct Options {
        size_t line_width = 60; // 0 = single line, >0 = wrapped
        bool write_description = true;
        bool validate_alignment = false;
    };

    /// Write sequences to a file path
    static void write_file(
        const std::filesystem::path& filepath,
        const std::vector<msa::core::Sequence>& sequences,
        const Options& options = Options{}
    );

    static void write_file(
        const std::filesystem::path& filepath,
        const std::vector<msa::core::Sequence>& sequences,
        size_t line_width
    ) {
        Options opt;
        opt.line_width = line_width;
        write_file(filepath, sequences, opt);
    }

    /// Write sequences to an output stream
    static void write_stream(
        std::ostream& os,
        const std::vector<msa::core::Sequence>& sequences,
        const Options& options = Options{}
    );

    static void write_stream(
        std::ostream& os,
        const std::vector<msa::core::Sequence>& sequences,
        size_t line_width
    ) {
        Options opt;
        opt.line_width = line_width;
        write_stream(os, sequences, opt);
    }

    /// Format sequences to an in-memory string
    [[nodiscard]] static std::string write_string(
        const std::vector<msa::core::Sequence>& sequences,
        const Options& options = Options{}
    );

    [[nodiscard]] static std::string write_string(
        const std::vector<msa::core::Sequence>& sequences,
        size_t line_width
    ) {
        Options opt;
        opt.line_width = line_width;
        return write_string(sequences, opt);
    }

    /// Validate alignment invariants: equal length and gap-stripped equality
    [[nodiscard]] static bool verify_alignment_integrity(
        const std::vector<msa::core::Sequence>& raw_sequences,
        const std::vector<msa::core::Sequence>& aligned_sequences,
        std::string* error_msg = nullptr
    );
};

} // namespace msa::io

#endif // MSA_IO_FASTA_IO_HPP
