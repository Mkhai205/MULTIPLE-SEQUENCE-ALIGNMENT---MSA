#ifndef MSA_EVAL_MEMORY_TRACKER_HPP
#define MSA_EVAL_MEMORY_TRACKER_HPP

#include <cstddef>

namespace msa::eval {

class MemoryTracker {
public:
    /// Returns current working set memory usage in bytes
    [[nodiscard]] static size_t getCurrentMemoryUsageBytes() noexcept;

    /// Returns peak working set memory usage in bytes since process start
    [[nodiscard]] static size_t getPeakMemoryUsageBytes() noexcept;

    /// RAII scope helper to measure peak memory during a workload
    class Scope {
    public:
        Scope() noexcept;
        [[nodiscard]] size_t initialBytes() const noexcept { return initial_bytes_; }
        [[nodiscard]] size_t currentBytes() const noexcept;
        [[nodiscard]] size_t peakBytes() const noexcept;
        [[nodiscard]] size_t peakDeltaBytes() const noexcept;

    private:
        size_t initial_bytes_{0};
        size_t initial_peak_{0};
    };
};

} // namespace msa::eval

#endif // MSA_EVAL_MEMORY_TRACKER_HPP
