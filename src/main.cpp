#include "msa/io/cli_parser.hpp"
#include <iostream>

int main(int argc, char* argv[]) {
    try {
        msa::io::CliParser parser;
        auto config = parser.parse(argc, argv, true);
        if (config.show_help) {
            std::cout << parser.format_help();
            return 0;
        }
        if (config.show_version) {
            std::cout << parser.format_version();
            return 0;
        }
        std::cout << "Multiple Sequence Alignment (MSA) C++17 System\n";
        std::cout << "Input: " << config.input_file << "\n";
        return 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
}
