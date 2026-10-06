#ifndef MSA_CORE_BLOSUM62_HPP
#define MSA_CORE_BLOSUM62_HPP

#include <array>
#include <cstddef>

namespace msa::core {

class Blosum62 {
public:
    static constexpr size_t DIMENSION = 24;
    static constexpr size_t STANDARD_AA_COUNT = 20;
    static constexpr int UNKNOWN_INDEX = 22; // 'X'

    Blosum62();

    // Fast O(1) score lookup
    [[nodiscard]] int score(char a, char b) const noexcept;
    [[nodiscard]] int scoreByIndex(int idx_a, int idx_b) const noexcept;

    // Index mappings
    [[nodiscard]] static int charToIndex(char c) noexcept;
    [[nodiscard]] static char indexToChar(int idx) noexcept;
    [[nodiscard]] static bool isValidChar(char c) noexcept;

    // Direct raw matrix access
    [[nodiscard]] const std::array<std::array<int, DIMENSION>, DIMENSION>& matrix() const noexcept {
        return matrix_;
    }

    // Singleton instance access
    static const Blosum62& instance() noexcept;

private:
    std::array<std::array<int, DIMENSION>, DIMENSION> matrix_{};
    static const std::array<int, 256> CHAR_TO_INDEX;
    static const std::array<char, DIMENSION> INDEX_TO_CHAR;

    static std::array<int, 256> initCharToIndexTable() noexcept;
    void initMatrix() noexcept;
};

} // namespace msa::core

#endif // MSA_CORE_BLOSUM62_HPP
