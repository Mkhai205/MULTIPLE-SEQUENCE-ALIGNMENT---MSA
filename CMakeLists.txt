cmake_minimum_required(VERSION 3.16)
project(msa LANGUAGES CXX)

# ==============================================================================
# C++17 Standard Requirements
# ==============================================================================
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ==============================================================================
# Compiler Warnings and Options
# ==============================================================================
if(MSVC)
    add_compile_options(
        /std:c++17
        /W4
        /permissive-
        /EHsc
        /utf-8
        /MP
    )
    # Enable /O2 optimizations for Release builds
    string(APPEND CMAKE_CXX_FLAGS_RELEASE " /O2")
    add_compile_definitions(
        _CRT_SECURE_NO_WARNINGS
        NOMINMAX
        WIN32_LEAN_AND_MEAN
    )
else()
    add_compile_options(
        -Wall
        -Wextra
        -Wpedantic
    )
endif()

# ==============================================================================
# OpenMP Discovery
# ==============================================================================
find_package(OpenMP REQUIRED)

# ==============================================================================
# Helper Function for Milestone-Safe Target Sources
# ==============================================================================
# If a planned future milestone source file does not exist yet on disk, create
# a valid compilation unit stub so that CMake targets and libraries compile
# cleanly during early milestones.
function(msa_resolve_sources OUT_VAR)
    set(RESOLVED_FILES)
    foreach(SRC_PATH ${ARGN})
        set(ABS_PATH "${CMAKE_CURRENT_SOURCE_DIR}/${SRC_PATH}")
        if(EXISTS "${ABS_PATH}")
            list(APPEND RESOLVED_FILES "${SRC_PATH}")
        else()
            get_filename_component(FNAME "${SRC_PATH}" NAME_WE)
            set(STUB_PATH "${CMAKE_BINARY_DIR}/stubs/${SRC_PATH}")
            get_filename_component(STUB_DIR "${STUB_PATH}" DIRECTORY)
            file(MAKE_DIRECTORY "${STUB_DIR}")
            if(NOT EXISTS "${STUB_PATH}")
                file(WRITE "${STUB_PATH}" "// Auto-generated milestone placeholder for ${SRC_PATH}\nvoid placeholder_${FNAME}() {}\n")
            endif()
            list(APPEND RESOLVED_FILES "${STUB_PATH}")
        endif()
    endforeach()
    set(${OUT_VAR} "${RESOLVED_FILES}" PARENT_SCOPE)
endfunction()

# ==============================================================================
# Target: msa_core (Milestone 1)
# ==============================================================================
msa_resolve_sources(MSA_CORE_SRCS
    src/core/sequence.cpp
    src/core/profile.cpp
    src/core/blosum62.cpp
    src/core/score_model.cpp
    src/io/fasta_io.cpp
    src/io/cli_parser.cpp
    src/parallel/omp_utils.cpp
)

add_library(msa_core STATIC ${MSA_CORE_SRCS})
target_include_directories(msa_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(msa_core PUBLIC OpenMP::OpenMP_CXX)

# ==============================================================================
# Target: msa_align (Milestones 2 & 3)
# ==============================================================================
msa_resolve_sources(MSA_ALIGN_SRCS
    src/align/needleman_wunsch.cpp
    src/align/hirschberg.cpp
    src/align/profile_aligner.cpp
    src/parallel/wavefront.cpp
)

add_library(msa_align STATIC ${MSA_ALIGN_SRCS})
target_include_directories(msa_align PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(msa_align PUBLIC msa_core OpenMP::OpenMP_CXX)

# ==============================================================================
# Target: msa_tree (Milestones 4 & 5)
# ==============================================================================
msa_resolve_sources(MSA_TREE_SRCS
    src/tree/distance_matrix.cpp
    src/tree/upgma.cpp
    src/tree/guide_tree.cpp
    src/parallel/tree_scheduler.cpp
)

add_library(msa_tree STATIC ${MSA_TREE_SRCS})
target_include_directories(msa_tree PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(msa_tree PUBLIC msa_align msa_core OpenMP::OpenMP_CXX)

# ==============================================================================
# Target: msa_eval (Milestone 6)
# ==============================================================================
msa_resolve_sources(MSA_EVAL_SRCS
    src/eval/balibase_parser.cpp
    src/eval/sp_score.cpp
    src/eval/tc_score.cpp
    src/eval/benchmark.cpp
    src/eval/memory_tracker.cpp
)

add_library(msa_eval STATIC ${MSA_EVAL_SRCS})
target_include_directories(msa_eval PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(msa_eval PUBLIC msa_tree msa_align msa_core OpenMP::OpenMP_CXX)

if(WIN32)
    target_link_libraries(msa_eval PUBLIC psapi)
endif()

# ==============================================================================
# Executable: msa_align_bin (CLI Entry Point - Milestone 7)
# ==============================================================================
msa_resolve_sources(MSA_MAIN_SRCS
    src/main.cpp
)

add_executable(msa_align_bin ${MSA_MAIN_SRCS})
set_target_properties(msa_align_bin PROPERTIES OUTPUT_NAME "msa_align")
target_include_directories(msa_align_bin PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)
target_link_libraries(msa_align_bin PRIVATE
    msa_eval
    msa_tree
    msa_align
    msa_core
    OpenMP::OpenMP_CXX
)

# ==============================================================================
# Testing Infrastructure (Unit Tests)
# ==============================================================================
enable_testing()

file(GLOB_RECURSE UNIT_TEST_SOURCES "tests/unit/*.cpp")
if(NOT UNIT_TEST_SOURCES)
    set(UNIT_TEST_SOURCES
        tests/unit/test_runner.cpp
        tests/unit/test_m1_core.cpp
    )
endif()

add_executable(msa_unit_tests ${UNIT_TEST_SOURCES})
target_include_directories(msa_unit_tests PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/include"
    "${CMAKE_CURRENT_SOURCE_DIR}/tests"
    "${CMAKE_CURRENT_SOURCE_DIR}/tests/unit"
)
target_link_libraries(msa_unit_tests PRIVATE
    msa_eval
    msa_tree
    msa_align
    msa_core
    OpenMP::OpenMP_CXX
)

add_test(NAME unit_tests COMMAND msa_unit_tests)
