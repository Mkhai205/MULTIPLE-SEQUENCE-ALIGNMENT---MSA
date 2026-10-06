#include "msa/io/cli_parser.hpp"
#include <iostream>
#include <sstream>
#include <iomanip>

namespace msa::io {

CliParser::CliParser(std::string program_name, std::string description)
    : program_name_(std::move(program_name)), description_(std::move(description)) {}

bool CliParser::is_numeric_value(std::string_view token) noexcept {
    if (token.empty()) return false;
    size_t start = 0;
    if (token[0] == '-' || token[0] == '+') {
        if (token.size() == 1) return false;
        start = 1;
    }
    for (size_t i = start; i < token.size(); ++i) {
        if (token[i] < '0' || token[i] > '9') return false;
    }
    return true;
}

int CliParser::parse_int(std::string_view name, std::string_view val, int min_val, int max_val) {
    try {
        size_t idx = 0;
        std::string s(val);
        int parsed = std::stoi(s, &idx);
        if (idx != s.size()) {
            throw CliParseException("Invalid integer value '" + s + "' for option '" + std::string(name) + "'");
        }
        if (parsed < min_val || parsed > max_val) {
            throw CliParseException("Value " + s + " out of allowed range [" + std::to_string(min_val) + ", " + std::to_string(max_val) + "] for option '" + std::string(name) + "'");
        }
        return parsed;
    } catch (const CliParseException&) {
        throw;
    } catch (const std::exception&) {
        throw CliParseException("Invalid integer format '" + std::string(val) + "' for option '" + std::string(name) + "'");
    }
}

CliConfig CliParser::parse(int argc, const char* const argv[], bool validate_file_exists) {
    CliConfig config;

    for (int i = 1; i < argc; ++i) {
        std::string_view arg(argv[i]);

        if (arg == "-h" || arg == "--help") {
            config.show_help = true;
            return config;
        }
        if (arg == "--version") {
            config.show_version = true;
            return config;
        }

        std::string_view key;
        std::optional<std::string_view> inline_val;

        // Check for --key=value
        size_t eq_pos = arg.find('=');
        if (eq_pos != std::string_view::npos) {
            key = arg.substr(0, eq_pos);
            inline_val = arg.substr(eq_pos + 1);
        } else {
            key = arg;
        }

        auto get_value = [&](std::string_view opt_name) -> std::string_view {
            if (inline_val.has_value()) {
                return *inline_val;
            }
            if (i + 1 < argc) {
                std::string_view next_arg(argv[i + 1]);
                if (next_arg.empty() || next_arg[0] != '-' || is_numeric_value(next_arg)) {
                    ++i;
                    return next_arg;
                }
            }
            throw CliParseException("Option '" + std::string(opt_name) + "' requires a value.");
        };

        if (key == "-i" || key == "--input") {
            config.input_file = std::string(get_value(key));
        } else if (key == "-o" || key == "--output") {
            config.output_file = std::string(get_value(key));
        } else if (key == "-t" || key == "--threads") {
            config.num_threads = parse_int(key, get_value(key), 1, 256);
        } else if (key == "--gap-open") {
            config.gap_open = parse_int(key, get_value(key), -1000, 1000);
            if (config.gap_open > 0) {
                config.gap_open = -config.gap_open;
            }
        } else if (key == "--gap-extend") {
            config.gap_extend = parse_int(key, get_value(key), -1000, 1000);
            if (config.gap_extend > 0) {
                config.gap_extend = -config.gap_extend;
            }
        } else if (key == "--benchmark") {
            config.benchmark = true;
        } else if (key == "--baseline-compare") {
            config.baseline_compare = true;
        } else if (key == "-v" || key == "--verbose") {
            config.verbose = true;
        } else {
            throw CliParseException("Unknown option: '" + std::string(key) + "'");
        }
    }

    if (!config.show_help && !config.show_version) {
        if (config.input_file.empty()) {
            throw CliParseException("Missing required option: --input <FILE>");
        }
        if (validate_file_exists && !std::filesystem::exists(config.input_file)) {
            throw CliParseException("Input file does not exist: " + config.input_file.string());
        }
    }

    return config;
}

std::string CliParser::format_version() const {
    return program_name_ + " version " + version_ + "\n";
}

std::string CliParser::format_help() const {
    std::ostringstream ss;
    ss << program_name_ << " - Multiple Sequence Alignment (MSA) C++17 System\n";
    ss << description_ << "\n\n";
    ss << "USAGE:\n";
    ss << "  " << program_name_ << " [OPTIONS] --input <FILE>\n\n";
    ss << "OPTIONS:\n";
    ss << "  -i, --input <FILE>           Path to input FASTA file containing protein sequences (REQUIRED)\n";
    ss << "  -o, --output <FILE>          Path to output aligned FASTA file [default: stdout or <input>.aln.fa]\n";
    ss << "  -t, --threads <NUM>          Number of OpenMP worker threads [default: 1]\n";
    ss << "      --gap-open <NUM>         Affine gap open penalty [default: -10]\n";
    ss << "      --gap-extend <NUM>       Affine gap extension penalty [default: -1]\n";
    ss << "      --benchmark              Enable performance benchmarking (wall-clock time, peak memory)\n";
    ss << "      --baseline-compare       Execute baseline Needleman-Wunsch alongside Hirschberg to verify score identity\n";
    ss << "  -v, --verbose                Enable verbose stage logging\n";
    ss << "  -h, --help                   Display this help message and exit\n";
    ss << "      --version                Display version information and exit\n\n";
    ss << "EXAMPLES:\n";
    ss << "  " << program_name_ << " --input sequences.fa --output aligned.fa\n";
    ss << "  " << program_name_ << " -i sequences.fa -o aligned.fa -t 4 --benchmark\n";
    ss << "  " << program_name_ << " -i sequences.fa --gap-open -10 --gap-extend -1 --baseline-compare\n";
    return ss.str();
}

} // namespace msa::io
