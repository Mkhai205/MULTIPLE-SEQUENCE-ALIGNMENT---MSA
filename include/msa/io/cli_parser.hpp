#ifndef MSA_IO_CLI_PARSER_HPP
#define MSA_IO_CLI_PARSER_HPP

#include <string>
#include <string_view>
#include <vector>
#include <filesystem>
#include <optional>
#include <stdexcept>

namespace msa::io {

struct CliConfig {
    std::filesystem::path input_file;
    std::filesystem::path output_file;
    int num_threads = 1;
    int gap_open = -10;
    int gap_extend = -1;
    bool benchmark = false;
    bool baseline_compare = false;
    bool show_help = false;
    bool show_version = false;
    bool verbose = false;
};

class CliParseException : public std::runtime_error {
public:
    explicit CliParseException(const std::string& msg)
        : std::runtime_error("[CLI Error] " + msg) {}
};

class CliParser {
public:
    explicit CliParser(
        std::string program_name = "msa_align",
        std::string description = "Progressive Multiple Sequence Alignment C++17 System"
    );

    /// Parse argc and argv
    [[nodiscard]] CliConfig parse(int argc, const char* const argv[], bool validate_file_exists = false);

    /// Format standard help text
    [[nodiscard]] std::string format_help() const;

    /// Format version text
    [[nodiscard]] std::string format_version() const;

private:
    std::string program_name_;
    std::string description_;
    std::string version_ = "1.0.0";

    static bool is_numeric_value(std::string_view token) noexcept;
    static int parse_int(std::string_view name, std::string_view val, int min_val = -1000000, int max_val = 1000000);
};

} // namespace msa::io

#endif // MSA_IO_CLI_PARSER_HPP
