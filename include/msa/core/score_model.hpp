#ifndef MSA_CORE_SCORE_MODEL_HPP
#define MSA_CORE_SCORE_MODEL_HPP

#include <cmath>
#include <cstdlib>

namespace msa::core {

class ScoreModel {
public:
    // Sentinel constant: safe against signed 32-bit int underflow
    static constexpr int NEG_INF = -1'000'000'000;

    // Constructors
    constexpr ScoreModel() noexcept : gap_open_(-10), gap_extend_(-1) {}
    constexpr ScoreModel(int open, int extend) noexcept
        : gap_open_(open > 0 ? -open : open),
          gap_extend_(extend > 0 ? -extend : extend) {}

    // Accessors
    [[nodiscard]] constexpr int gapOpen() const noexcept { return gap_open_; }
    [[nodiscard]] constexpr int gapExtend() const noexcept { return gap_extend_; }

    // Gap cost calculation for length k: W(k) = gap_open + k * gap_extend
    [[nodiscard]] constexpr int gapCost(int length) const noexcept {
        if (length <= 0) return 0;
        return gap_open_ + length * gap_extend_;
    }

    // Check if score represents unreachable / negative infinity
    [[nodiscard]] static constexpr bool isNegInf(int score) noexcept {
        return score <= NEG_INF / 2;
    }

    // Profile-to-profile effective gap penalties (scaled by residue occupancy)
    [[nodiscard]] double effectiveGapOpen(double gap_frequency) const noexcept {
        double occupancy = 1.0 - gap_frequency;
        if (occupancy < 0.0) occupancy = 0.0;
        return static_cast<double>(gap_open_) * occupancy;
    }

    [[nodiscard]] double effectiveGapExtend(double gap_frequency) const noexcept {
        double occupancy = 1.0 - gap_frequency;
        if (occupancy < 0.0) occupancy = 0.0;
        return static_cast<double>(gap_extend_) * occupancy;
    }

    bool operator==(const ScoreModel& other) const noexcept {
        return gap_open_ == other.gap_open_ && gap_extend_ == other.gap_extend_;
    }
    bool operator!=(const ScoreModel& other) const noexcept {
        return !(*this == other);
    }

private:
    int gap_open_{-10};
    int gap_extend_{-1};
};

} // namespace msa::core

#endif // MSA_CORE_SCORE_MODEL_HPP
