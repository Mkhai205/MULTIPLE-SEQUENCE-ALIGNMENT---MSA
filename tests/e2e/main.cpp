#include "e2e_framework.hpp"
#include <iostream>
#include <iomanip>
#include <string>
#include <vector>
#include <chrono>

int main(int argc, char* argv[]) {
    int target_tier = 0; // 0 means all tiers
    std::string feature_filter;
    std::string name_filter;
    bool verbose = false;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if ((arg == "--tier" || arg == "-t") && i + 1 < argc) {
            target_tier = std::stoi(argv[++i]);
        } else if ((arg == "--feature" || arg == "-f") && i + 1 < argc) {
            feature_filter = argv[++i];
        } else if (arg == "--filter" && i + 1 < argc) {
            name_filter = argv[++i];
        } else if (arg == "--verbose" || arg == "-v") {
            verbose = true;
        } else if (arg == "--help" || arg == "-h") {
            std::cout << "MSA End-to-End (E2E) Test Suite Runner\n"
                      << "Usage: " << argv[0] << " [options]\n"
                      << "Options:\n"
                      << "  --tier <1-4>      Run only tests in the specified Tier\n"
                      << "  --feature <ID>    Filter tests by feature ID (e.g. F1, F4, COMB, SCEN)\n"
                      << "  --filter <str>    Filter tests by name substring\n"
                      << "  --verbose, -v     Enable verbose test output\n"
                      << "  --help, -h        Display this help message\n";
            return 0;
        }
    }

    const auto& all_tests = ::msa::e2e::TestRegistry::Instance().GetAllTests();

    std::cout << "======================================================================\n";
    std::cout << "     Multiple Sequence Alignment (MSA) - 4-Tier E2E Test Suite        \n";
    std::cout << "======================================================================\n";
    std::cout << "Registered Tests: " << all_tests.size() << "\n";
    if (target_tier > 0) std::cout << "Filtering by Tier: " << target_tier << "\n";
    if (!feature_filter.empty()) std::cout << "Filtering by Feature: " << feature_filter << "\n";
    if (!name_filter.empty()) std::cout << "Filtering by Substring: " << name_filter << "\n";
    std::cout << "----------------------------------------------------------------------\n";

    size_t passed = 0;
    size_t failed = 0;
    size_t skipped = 0;

    auto start_all = std::chrono::high_resolution_clock::now();

    for (const auto& test : all_tests) {
        if (target_tier > 0 && test.tier != target_tier) {
            skipped++;
            continue;
        }
        if (!feature_filter.empty() && test.feature_id != feature_filter) {
            skipped++;
            continue;
        }
        if (!name_filter.empty() && test.test_id.find(name_filter) == std::string::npos) {
            skipped++;
            continue;
        }

        if (verbose) {
            std::cout << "[RUN ] Tier " << test.tier << " [" << test.feature_id << "] " 
                      << test.test_id << " - " << test.description << "\n";
        }

        auto t1 = std::chrono::high_resolution_clock::now();
        bool test_passed = false;
        try {
            test.func();
            test_passed = true;
            passed++;
        } catch (const ::msa::e2e::TestException& ex) {
            failed++;
            std::cerr << "[FAIL] Tier " << test.tier << " [" << test.feature_id << "] " 
                      << test.test_id << "\n       Error: " << ex.what() << "\n";
        } catch (const std::exception& ex) {
            failed++;
            std::cerr << "[FAIL] Tier " << test.tier << " [" << test.feature_id << "] " 
                      << test.test_id << "\n       StdException: " << ex.what() << "\n";
        } catch (...) {
            failed++;
            std::cerr << "[FAIL] Tier " << test.tier << " [" << test.feature_id << "] " 
                      << test.test_id << "\n       Unknown exception caught.\n";
        }

        auto t2 = std::chrono::high_resolution_clock::now();
        double ms = std::chrono::duration<double, std::milli>(t2 - t1).count();

        if (verbose && test_passed) {
            std::cout << "[PASS] " << test.test_id << " (" << std::fixed << std::setprecision(2) << ms << " ms)\n";
        }
    }

    auto end_all = std::chrono::high_resolution_clock::now();
    double total_sec = std::chrono::duration<double>(end_all - start_all).count();

    std::cout << "======================================================================\n";
    std::cout << "                         E2E TEST SUMMARY                             \n";
    std::cout << "======================================================================\n";
    std::cout << "  Total Executed : " << (passed + failed) << "\n";
    std::cout << "  Passed         : " << passed << " (" 
              << (passed + failed > 0 ? (100.0 * passed / (passed + failed)) : 0.0) << "%)\n";
    std::cout << "  Failed         : " << failed << "\n";
    std::cout << "  Skipped        : " << skipped << "\n";
    std::cout << "  Total Duration : " << std::fixed << std::setprecision(3) << total_sec << " seconds\n";
    std::cout << "======================================================================\n";

    if (failed > 0) {
        std::cerr << "OVERALL STATUS: FAILURE (" << failed << " tests failed)\n";
        return 1;
    } else {
        std::cout << "OVERALL STATUS: SUCCESS (All executed tests passed)\n";
        return 0;
    }
}
