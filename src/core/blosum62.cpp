#include "msa/core/blosum62.hpp"
#include <cassert>

namespace msa::core {

const std::array<char, Blosum62::DIMENSION> Blosum62::INDEX_TO_CHAR = {
    'A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I',
    'L', 'K', 'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V',
    'B', 'Z', 'X', '*'
};

std::array<int, 256> Blosum62::initCharToIndexTable() noexcept {
    std::array<int, 256> table{};
    table.fill(UNKNOWN_INDEX); // Default to 'X' for safety

    // Populate uppercase and lowercase
    for (int i = 0; i < static_cast<int>(DIMENSION); ++i) {
        char c = INDEX_TO_CHAR[i];
        table[static_cast<unsigned char>(c)] = i;
        if (c >= 'A' && c <= 'Z') {
            table[static_cast<unsigned char>(c - 'A' + 'a')] = i;
        }
    }

    // Extended amino acid mappings
    table[static_cast<unsigned char>('U')] = 4;  // 'C'
    table[static_cast<unsigned char>('u')] = 4;
    table[static_cast<unsigned char>('O')] = 11; // 'K'
    table[static_cast<unsigned char>('o')] = 11;
    table[static_cast<unsigned char>('J')] = UNKNOWN_INDEX; // 'X'
    table[static_cast<unsigned char>('j')] = UNKNOWN_INDEX;

    return table;
}

const std::array<int, 256> Blosum62::CHAR_TO_INDEX = Blosum62::initCharToIndexTable();

Blosum62::Blosum62() {
    initMatrix();
}

void Blosum62::initMatrix() noexcept {
    // 24x24 matrix matching canonical NCBI BLOSUM62
    const int raw[DIMENSION][DIMENSION] = {
        /* A */ {  4, -1, -2, -2,  0, -1, -1,  0, -2, -1, -1, -1, -1, -2, -1,  1,  0, -3, -2,  0, -2, -1,  0, -4 },
        /* R */ { -1,  5,  0, -2, -3,  1,  0, -2,  0, -3, -2,  2, -1, -3, -2, -1, -1, -3, -2, -3, -1,  0, -1, -4 },
        /* N */ { -2,  0,  6,  1, -3,  0,  0,  0,  1, -3, -3,  0, -2, -3, -2,  1,  0, -4, -2, -3,  3,  0, -1, -4 },
        /* D */ { -2, -2,  1,  6, -3,  0,  2, -1, -1, -3, -4, -1, -3, -3, -1,  0, -1, -4, -3, -3,  4,  1, -1, -4 },
        /* C */ {  0, -3, -3, -3,  9, -3, -4, -3, -3, -1, -1, -3, -1, -2, -3, -1, -1, -2, -2, -1, -3, -3, -2, -4 },
        /* Q */ { -1,  1,  0,  0, -3,  5,  2, -2,  0, -3, -2,  1,  0, -3, -1,  0, -1, -2, -1, -2,  0,  3, -1, -4 },
        /* E */ { -1,  0,  0,  2, -4,  2,  5, -2,  0, -3, -3,  1, -2, -3, -1,  0, -1, -3, -2, -2,  1,  4, -1, -4 },
        /* G */ {  0, -2,  0, -1, -3, -2, -2,  6, -2, -4, -4, -2, -3, -3, -2,  0, -2, -2, -3, -3, -1, -2, -1, -4 },
        /* H */ { -2,  0,  1, -1, -3,  0,  0, -2,  8, -3, -3, -1, -2, -1, -2, -1, -2, -2,  2, -3,  0,  0, -1, -4 },
        /* I */ { -1, -3, -3, -3, -1, -3, -3, -4, -3,  4,  2, -3,  1,  0, -3, -2, -1, -3, -1,  3, -3, -3, -1, -4 },
        /* L */ { -1, -2, -3, -4, -1, -2, -3, -4, -3,  2,  4, -2,  2,  0, -3, -2, -1, -2, -1,  1, -4, -3, -1, -4 },
        /* K */ { -1,  2,  0, -1, -3,  1,  1, -2, -1, -3, -2,  5, -1, -3, -1,  0, -1, -3, -2, -2,  0,  1, -1, -4 },
        /* M */ { -1, -1, -2, -3, -1,  0, -2, -3, -2,  1,  2, -1,  5,  0, -2, -1, -1, -1, -1,  1, -3, -1, -1, -4 },
        /* F */ { -2, -3, -3, -3, -2, -3, -3, -3, -1,  0,  0, -3,  0,  6, -4, -2, -2,  1,  3, -1, -3, -3, -1, -4 },
        /* P */ { -1, -2, -2, -1, -3, -1, -1, -2, -2, -3, -3, -1, -2, -4,  7, -1, -1, -4, -3, -2, -1, -1, -2, -4 },
        /* S */ {  1, -1,  1,  0, -1,  0,  0,  0, -1, -2, -2,  0, -1, -2, -1,  4,  1, -3, -2, -2,  0,  0,  0, -4 },
        /* T */ {  0, -1,  0, -1, -1, -1, -1, -2, -2, -1, -1, -1, -1, -2, -1,  1,  5, -2, -2,  0, -1, -1,  0, -4 },
        /* W */ { -3, -3, -4, -4, -2, -2, -3, -2, -2, -3, -2, -3, -1,  1, -4, -3, -2, 11,  2, -3, -4, -3, -2, -4 },
        /* Y */ { -2, -2, -2, -3, -2, -1, -2, -3,  2, -1, -1, -2, -1,  3, -3, -2, -2,  2,  7, -1, -3, -2, -1, -4 },
        /* V */ {  0, -3, -3, -3, -1, -2, -2, -3, -3,  3,  1, -2,  1, -1, -2, -2,  0, -3, -1,  4, -3, -2, -1, -4 },
        /* B */ { -2, -1,  3,  4, -3,  0,  1, -1,  0, -3, -4,  0, -3, -3, -1,  0, -1, -4, -3, -3,  4,  1, -1, -4 },
        /* Z */ { -1,  0,  0,  1, -3,  3,  4, -2,  0, -3, -3,  1, -1, -3, -1,  0, -1, -3, -2, -2,  1,  4, -1, -4 },
        /* X */ {  0, -1, -1, -1, -2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -2,  0,  0, -2, -1, -1, -1, -1, -1, -4 },
        /* * */ { -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4, -4,  1 }
    };

    for (size_t i = 0; i < DIMENSION; ++i) {
        for (size_t j = 0; j < DIMENSION; ++j) {
            matrix_[i][j] = raw[i][j];
            assert(matrix_[i][j] == raw[j][i]);
        }
    }
}

int Blosum62::charToIndex(char c) noexcept {
    return CHAR_TO_INDEX[static_cast<unsigned char>(c)];
}

char Blosum62::indexToChar(int idx) noexcept {
    if (idx >= 0 && idx < static_cast<int>(DIMENSION)) {
        return INDEX_TO_CHAR[idx];
    }
    return 'X';
}

bool Blosum62::isValidChar(char c) noexcept {
    unsigned char uc = static_cast<unsigned char>(c);
    return CHAR_TO_INDEX[uc] != UNKNOWN_INDEX || uc == 'X' || uc == 'x';
}

int Blosum62::score(char a, char b) const noexcept {
    int idx_a = CHAR_TO_INDEX[static_cast<unsigned char>(a)];
    int idx_b = CHAR_TO_INDEX[static_cast<unsigned char>(b)];
    return matrix_[idx_a][idx_b];
}

int Blosum62::scoreByIndex(int idx_a, int idx_b) const noexcept {
    assert(idx_a >= 0 && idx_a < static_cast<int>(DIMENSION));
    assert(idx_b >= 0 && idx_b < static_cast<int>(DIMENSION));
    return matrix_[idx_a][idx_b];
}

const Blosum62& Blosum62::instance() noexcept {
    static const Blosum62 inst;
    return inst;
}

} // namespace msa::core
