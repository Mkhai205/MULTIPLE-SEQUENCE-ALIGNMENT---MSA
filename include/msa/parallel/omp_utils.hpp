#ifndef MSA_PARALLEL_OMP_UTILS_HPP
#define MSA_PARALLEL_OMP_UTILS_HPP

#if defined(_OPENMP)
#include <omp.h>
#endif

namespace msa::parallel {

inline bool is_openmp_enabled() noexcept {
#if defined(_OPENMP)
    return true;
#else
    return false;
#endif
}

inline int get_max_threads() noexcept {
#if defined(_OPENMP)
    return omp_get_max_threads();
#else
    return 1;
#endif
}

inline int get_thread_num() noexcept {
#if defined(_OPENMP)
    return omp_get_thread_num();
#else
    return 0;
#endif
}

inline void set_num_threads(int n) noexcept {
#if defined(_OPENMP)
    if (n > 0) {
        omp_set_num_threads(n);
    }
#else
    (void)n;
#endif
}

} // namespace msa::parallel

#endif // MSA_PARALLEL_OMP_UTILS_HPP
