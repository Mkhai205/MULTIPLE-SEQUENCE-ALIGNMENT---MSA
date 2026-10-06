#include "msa/eval/memory_tracker.hpp"

#if defined(_WIN32)
#include <windows.h>
#include <psapi.h>
#else
#include <sys/resource.h>
#include <unistd.h>
#endif

#include <algorithm>

namespace msa::eval {

size_t MemoryTracker::getCurrentMemoryUsageBytes() noexcept {
#if defined(_WIN32)
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        return static_cast<size_t>(pmc.WorkingSetSize);
    }
    return 0;
#else
    struct rusage usage;
    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        return static_cast<size_t>(usage.ru_maxrss) * 1024ULL;
    }
    return 0;
#endif
}

size_t MemoryTracker::getPeakMemoryUsageBytes() noexcept {
#if defined(_WIN32)
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        return static_cast<size_t>(pmc.PeakWorkingSetSize);
    }
    return 0;
#else
    struct rusage usage;
    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        return static_cast<size_t>(usage.ru_maxrss) * 1024ULL;
    }
    return 0;
#endif
}

MemoryTracker::Scope::Scope() noexcept
    : initial_bytes_(getCurrentMemoryUsageBytes()),
      initial_peak_(getPeakMemoryUsageBytes()) {}

size_t MemoryTracker::Scope::currentBytes() const noexcept {
    return getCurrentMemoryUsageBytes();
}

size_t MemoryTracker::Scope::peakBytes() const noexcept {
    return getPeakMemoryUsageBytes();
}

size_t MemoryTracker::Scope::peakDeltaBytes() const noexcept {
    size_t current_peak = getPeakMemoryUsageBytes();
    return (current_peak > initial_peak_) ? (current_peak - initial_peak_) : 0;
}

} // namespace msa::eval
