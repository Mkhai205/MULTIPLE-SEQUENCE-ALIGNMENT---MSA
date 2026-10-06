#ifndef MSA_CORE_SEQUENCE_HPP
#define MSA_CORE_SEQUENCE_HPP

#include <string>
#include <string_view>
#include <array>
#include <optional>
#include <iostream>
#include <stdexcept>

namespace msa::core {

class Sequence {
public:
    // Constructors
    Sequence() = default;
    Sequence(std::string id, std::string raw_seq, std::string description = "", bool validate = true);

    // Rule of 5
    Sequence(const Sequence&) = default;
    Sequence(Sequence&&) noexcept = default;
    Sequence& operator=(const Sequence&) = default;
    Sequence& operator=(Sequence&&) noexcept = default;
    ~Sequence() = default;

    // Accessors
    [[nodiscard]] const std::string& id() const noexcept { return id_; }
    [[nodiscard]] const std::string& description() const noexcept { return description_; }
    [[nodiscard]] const std::string& raw_seq() const noexcept { return raw_seq_; }
    [[nodiscard]] const std::string& seq() const noexcept { return raw_seq_; }
    [[nodiscard]] const std::string& str() const noexcept { return raw_seq_; }
    [[nodiscard]] const std::string& data() const noexcept { return raw_seq_; }
    [[nodiscard]] size_t length() const noexcept { return raw_seq_.length(); }
    [[nodiscard]] size_t size() const noexcept { return raw_seq_.size(); }
    [[nodiscard]] bool empty() const noexcept { return raw_seq_.empty(); }

    // Character indexing
    [[nodiscard]] char operator[](size_t index) const noexcept { return raw_seq_[index]; }
    [[nodiscard]] char at(size_t index) const { return raw_seq_.at(index); }
    [[nodiscard]] char front() const { return raw_seq_.front(); }
    [[nodiscard]] char back() const { return raw_seq_.back(); }

    // Mutators
    void setId(std::string id) { id_ = std::move(id); }
    void setDescription(std::string desc) { description_ = std::move(desc); }
    void setSeq(std::string seq);
    void append(char c);
    void append(std::string_view sv);
    void clear() noexcept;

    // Validation & Sanitization
    [[nodiscard]] bool isValid() const noexcept;
    [[nodiscard]] std::optional<size_t> findFirstInvalidChar() const noexcept;

    static bool isValidAminoAcid(char c, bool allow_gap = true) noexcept;
    static std::string sanitize(std::string_view raw);

    // Equality operators
    bool operator==(const Sequence& other) const noexcept {
        return id_ == other.id_ && raw_seq_ == other.raw_seq_;
    }
    bool operator!=(const Sequence& other) const noexcept {
        return !(*this == other);
    }

    // Stream operator
    friend std::ostream& operator<<(std::ostream& os, const Sequence& seq);

private:
    std::string id_;
    std::string description_;
    std::string raw_seq_;

    static const std::array<bool, 256> VALID_AA_TABLE;
    static std::array<bool, 256> initValidTable() noexcept;
};

} // namespace msa::core

#endif // MSA_CORE_SEQUENCE_HPP
