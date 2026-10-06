# CMake configuration for E2E Tests
cmake_minimum_required(VERSION 3.15)
project(msa_e2e_tests LANGUAGES CXX)

set(E2E_SOURCES
    main.cpp
    test_tier1_features.cpp
    test_tier2_boundaries.cpp
    test_tier3_combinations.cpp
    test_tier4_scenarios.cpp
)

add_executable(msa_e2e_tests ${E2E_SOURCES})

target_compile_features(msa_e2e_tests PRIVATE cxx_std_17)

target_include_directories(msa_e2e_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/include
)

# OpenMP support
find_package(OpenMP)
if(OpenMP_CXX_FOUND)
    target_link_libraries(msa_e2e_tests PRIVATE OpenMP::OpenMP_CXX)
endif()

# Link against project libraries when available
if(TARGET msa_core)
    target_link_libraries(msa_e2e_tests PRIVATE msa_core)
endif()
if(TARGET msa_align)
    target_link_libraries(msa_e2e_tests PRIVATE msa_align)
endif()
if(TARGET msa_tree)
    target_link_libraries(msa_e2e_tests PRIVATE msa_tree)
endif()
if(TARGET msa_eval)
    target_link_libraries(msa_e2e_tests PRIVATE msa_eval)
endif()

# Windows PSAPI library for memory tracking
if(WIN32)
    target_link_libraries(msa_e2e_tests PRIVATE psapi)
endif()

# Register test with CTest
add_test(NAME msa_e2e_tests COMMAND msa_e2e_tests)
