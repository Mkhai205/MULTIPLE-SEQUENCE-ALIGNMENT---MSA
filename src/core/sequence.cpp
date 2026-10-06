#include "msa/core/sequence.hpp"
#include <algorithm>
#include <cctype>

namespace msa::core {

std::array<bool, 256> Sequence::initValidTable() noexcept {
    std::array<bool, 256> table{};
    table.fill(false);

    // 20 standard amino acids (uppercase and lowercase)
    const char standard_aa[] = "ACDEFGHIKLMNPQRSTVWYacdefghiklmnpqrstvwy";
    for (const char* p = standard_aa; *p != '\0'; ++p) {
        table[static_cast<unsigned char>(*p)] = true;
    }

    // Ambiguity codes: B, Z, X, *
    const char ambiguity[] = "BZX*bzx";
    for (const char* p = ambiguity; *p != '\0'; ++p) {
        table[static_cast<unsigned char>(*p)] = true;
    }

    // Extended codes: U (Selenocysteine), O (Pyrrolysine), J (Leu/Ile)
    const char extended[] = "UOJuoj";
    for (const char* p = extended; *p != '\0'; ++p) {
        table[static_cast<unsigned char>(*p)] = true;
    }

    // Alignment gap characters: -, .
    table[static_cast<unsigned char>('-')] = true;
    table[static_cast<unsigned char>('.')] = true;

    return table;
}

const std::array<bool, 256> Sequence::VALID_AA_TABLE = Sequence::initValidTable();

Sequence::Sequence(std::string id, std::string raw_seq, std::string description, bool validate)
    : id_(std::move(id)), description_(std::move(description)) {
    setSeq(std::move(raw_seq));
    if (validate && !isValid()) {
        auto invalid_idx = findFirstInvalidChar();
        char bad_c = invalid_idx ? raw_seq_[*invalid_idx] : '?';
        throw std::invalid_argument("Sequence: Invalid residue character '" + std::string(1, bad_c) + "' in sequence '" + id_ + "'");
    }
}

void Sequence::setSeq(std::string seq) {
    raw_seq_ = sanitize(seq);
}

void Sequence::append(char c) {
    if (!std::isspace(static_cast<unsigned char>(c))) {
        char upper = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
        if (upper == '.') upper = '-';
        raw_seq_.push_back(upper);
    }
}

void Sequence::append(std::string_view sv) {
    raw_seq_.reserve(raw_seq_.size() + sv.size());
    for (char c : sv) {
        if (!std::isspace(static_cast<unsigned char>(c))) {
            char upper = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
            if (upper == '.') upper = '-';
            raw_seq_.push_back(upper);
        }
    }
}

void Sequence::clear() noexcept {
    id_.clear();
    description_.clear();
    raw_seq_.clear();
}

bool Sequence::isValidAminoAcid(char c, bool allow_gap) noexcept {
    if (!allow_gap && (c == '-' || c == '.')) {
        return false;
    }
    return VALID_AA_TABLE[static_cast<unsigned char>(c)];
}

bool Sequence::isValid() const noexcept {
    for (char c : raw_seq_) {
        if (!VALID_AA_TABLE[static_cast<unsigned char>(c)]) {
            return false;
        }
    }
    return true;
}

std::optional<size_t> Sequence::findFirstInvalidChar() const noexcept {
    for (size_t i = 0; i < raw_seq_.size(); ++i) {
        if (!VALID_AA_TABLE[static_cast<unsigned char>(raw_seq_[i])]) {
            return i;
        }
    }
    return std::nullopt;
}

std::string Sequence::sanitize(std::string_view raw) {
    std::string clean;
    clean.reserve(raw.size());
    for (char c : raw) {
        if (!std::isspace(static_cast<unsigned char>(c))) {
            char upper = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
            if (upper == '.') upper = '-';
            clean.push_back(upper);
        }
    }
    return clean;
}

std::ostream& operator<<(std::ostream& os, const Sequence& seq) {
    os << ">" << seq.id();
    if (!seq.description().empty()) {
        os << " " << seq.description();
    }
    os << "\n" << seq.raw_seq();
    return os;
}

} // namespace msa::core
