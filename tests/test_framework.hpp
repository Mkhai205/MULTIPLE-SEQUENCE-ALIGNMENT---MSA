#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <functional>
#include <chrono>
#include <cmath>
#include <sstream>
#include <exception>
#include <iomanip>
#include <algorithm>

namespace msa::test {

struct AssertionFailure {
    std::string file;
    int line;
    std::string expression;
    std::string details;
};

class TestAbortException : public std::exception {
public:
    const char* what() const noexcept override {
        return "Test assertion failed (REQUIRE)";
    }
};

class TestCaseContext {
public:
    std::string current_test_name;
    size_t assertions_passed = 0;
    size_t assertions_failed = 0;
    std::vector<AssertionFailure> failures;
    bool current_test_passed = true;

    void record_pass() {
        assertions_passed++;
    }

    void record_fail(const std::string& file, int line, const std::string& expr, const std::string& details = "") {
        assertions_failed++;
        current_test_passed = false;
        failures.push_back({file, line, expr, details});
    }

    void reset_for_test(const std::string& name) {
        current_test_name = name;
        current_test_passed = true;
    }
};

inline TestCaseContext& get_context() {
    static TestCaseContext ctx;
    return ctx;
}

struct TestCase {
    std::string name;
    std::function<void()> func;
};

class TestRegistry {
public:
    static TestRegistry& instance() {
        static TestRegistry reg;
        return reg;
    }

    void register_test(const std::string& name, std::function<void()> func) {
        tests_.push_back({name, func});
    }

    const std::vector<TestCase>& tests() const {
        return tests_;
    }

    int run_all(int argc, char* argv[]) {
        std::string filter = "";
        bool list_only = false;

        for (int i = 1; i < argc; ++i) {
            std::string arg = argv[i];
            if ((arg == "-f" || arg == "--filter") && i + 1 < argc) {
                filter = argv[++i];
            } else if (arg == "-l" || arg == "--list") {
                list_only = true;
            } else if (arg == "-h" || arg == "--help") {
                std::cout << "Usage: msa_unit_tests [options]\n"
                          << "Options:\n"
                          << "  -f, --filter <str>  Only run tests containing <str>\n"
                          << "  -l, --list          List registered tests\n"
                          << "  -h, --help          Show help message\n";
                return 0;
            }
        }

        if (list_only) {
            std::cout << "Registered test cases (" << tests_.size() << "):\n";
            for (const auto& t : tests_) {
                std::cout << "  - " << t.name << "\n";
            }
            return 0;
        }

        std::cout << "======================================================\n";
        std::cout << "           MSA C++17 Unit Test Runner                 \n";
        std::cout << "======================================================\n";

        size_t total_tests = 0;
        size_t passed_tests = 0;
        size_t failed_tests = 0;

        auto total_start = std::chrono::high_resolution_clock::now();

        for (const auto& test : tests_) {
            if (!filter.empty() && test.name.find(filter) == std::string::npos) {
                continue;
            }

            total_tests++;
            auto& ctx = get_context();
            ctx.reset_for_test(test.name);

            std::cout << "[ RUN      ] " << test.name << "\n";
            auto start_time = std::chrono::high_resolution_clock::now();

            try {
                test.func();
            } catch (const TestAbortException&) {
                // Aborted cleanly by REQUIRE failure
            } catch (const std::exception& e) {
                ctx.record_fail(__FILE__, __LINE__, "Uncaught std::exception", e.what());
            } catch (...) {
                ctx.record_fail(__FILE__, __LINE__, "Uncaught unknown exception", "Non-std::exception thrown");
            }

            auto end_time = std::chrono::high_resolution_clock::now();
            double duration_ms = std::chrono::duration<double, std::milli>(end_time - start_time).count();

            if (ctx.current_test_passed) {
                passed_tests++;
                std::cout << "[       OK ] " << test.name << " (" << std::fixed << std::setprecision(2) << duration_ms << " ms)\n";
            } else {
                failed_tests++;
                std::cout << "[  FAILED  ] " << test.name << " (" << std::fixed << std::setprecision(2) << duration_ms << " ms)\n";
                for (const auto& fail : ctx.failures) {
                    std::cout << "  " << fail.file << ":" << fail.line << ": FAILURE\n";
                    std::cout << "    Condition: " << fail.expression << "\n";
                    if (!fail.details.empty()) {
                        std::cout << "    Details:   " << fail.details << "\n";
                    }
                }
                ctx.failures.clear();
            }
        }

        auto total_end = std::chrono::high_resolution_clock::now();
        double total_duration_ms = std::chrono::duration<double, std::milli>(total_end - total_start).count();

        std::cout << "======================================================\n";
        std::cout << "Test Summary: " << total_tests << " run, "
                  << passed_tests << " passed, "
                  << failed_tests << " failed ("
                  << std::fixed << std::setprecision(2) << total_duration_ms << " ms total)\n";
        std::cout << "Assertions:   " << get_context().assertions_passed << " passed, "
                  << get_context().assertions_failed << " failed\n";
        std::cout << "======================================================\n";

        return (failed_tests == 0) ? 0 : 1;
    }

private:
    std::vector<TestCase> tests_;
};

struct AutoRegistrar {
    AutoRegistrar(const std::string& name, std::function<void()> func) {
        TestRegistry::instance().register_test(name, func);
    }
};

template<typename T>
std::string to_string_repr(const T& val) {
    std::ostringstream oss;
    oss << val;
    return oss.str();
}

inline std::string to_string_repr(const std::string& val) {
    return "\"" + val + "\"";
}

inline std::string to_string_repr(const char* val) {
    return val ? ("\"" + std::string(val) + "\"") : "nullptr";
}

inline std::string to_string_repr(char val) {
    return std::string("'") + val + "'";
}

inline std::string to_string_repr(bool val) {
    return val ? "true" : "false";
}

} // namespace msa::test

#define MSA_TEST_CONCAT_IMPL(a, b) a##b
#define MSA_TEST_CONCAT(a, b) MSA_TEST_CONCAT_IMPL(a, b)

#define TEST_CASE(name) \
    static void MSA_TEST_CONCAT(msa_test_func_, __LINE__)(); \
    static ::msa::test::AutoRegistrar MSA_TEST_CONCAT(msa_test_reg_, __LINE__)(name, &MSA_TEST_CONCAT(msa_test_func_, __LINE__)); \
    static void MSA_TEST_CONCAT(msa_test_func_, __LINE__)()

#define CHECK(cond) \
    do { \
        if (cond) { \
            ::msa::test::get_context().record_pass(); \
        } else { \
            ::msa::test::get_context().record_fail(__FILE__, __LINE__, #cond); \
        } \
    } while (false)

#define REQUIRE(cond) \
    do { \
        if (cond) { \
            ::msa::test::get_context().record_pass(); \
        } else { \
            ::msa::test::get_context().record_fail(__FILE__, __LINE__, #cond); \
            throw ::msa::test::TestAbortException(); \
        } \
    } while (false)

#define CHECK_EQ(a, b) \
    do { \
        auto _val_a = (a); \
        auto _val_b = (b); \
        if (_val_a == _val_b) { \
            ::msa::test::get_context().record_pass(); \
        } else { \
            std::string _detail = "Expected: " + ::msa::test::to_string_repr(_val_b) + ", Actual: " + ::msa::test::to_string_repr(_val_a); \
            ::msa::test::get_context().record_fail(__FILE__, __LINE__, #a " == " #b, _detail); \
        } \
    } while (false)

#define REQUIRE_EQ(a, b) \
    do { \
        auto _val_a = (a); \
        auto _val_b = (b); \
        if (_val_a == _val_b) { \
            ::msa::test::get_context().record_pass(); \
        } else { \
            std::string _detail = "Expected: " + ::msa::test::to_string_repr(_val_b) + ", Actual: " + ::msa::test::to_string_repr(_val_a); \
            ::msa::test::get_context().record_fail(__FILE__, __LINE__, #a " == " #b, _detail); \
            throw ::msa::test::TestAbortException(); \
        } \
    } while (false)

#define CHECK_NE(a, b) \
    do { \
        auto _val_a = (a); \
        auto _val_b = (b); \
        if (_val_a != _val_b) { \
            ::msa::test::get_context().record_pass(); \
        } else { \
            std::string _detail = "Both values equal: " + ::msa::test::to_string_repr(_val_a); \
            ::msa::test::get_context().record_fail(__FILE__, __LINE__, #a " != " #b, _detail); \
        } \
    } while (false)

#define CHECK_NEAR(a, b, eps) \
    do { \
        auto _val_a = (a); \
        auto _val_b = (b); \
        auto _eps = (eps); \
        if (std::abs(_val_a - _val_b) <= _eps) { \
            ::msa::test::get_context().record_pass(); \
        } else { \
            std::string _detail = "Diff: " + std::to_string(std::abs(_val_a - _val_b)) + " > eps: " + std::to_string(_eps); \
            ::msa::test::get_context().record_fail(__FILE__, __LINE__, "|" #a " - " #b "| <= " #eps, _detail); \
        } \
    } while (false)

#define CHECK_THROWS(...) \
    do { \
        bool _threw = false; \
        try { \
            (void)(__VA_ARGS__); \
        } catch (...) { \
            _threw = true; \
        } \
        if (_threw) { \
            ::msa::test::get_context().record_pass(); \
        } else { \
            ::msa::test::get_context().record_fail(__FILE__, __LINE__, #__VA_ARGS__ " throws", "Expected exception not thrown"); \
        } \
    } while (false)

#define CHECK_THROWS_AS(expr, exc_type) \
    do { \
        bool _threw_expected = false; \
        bool _threw_other = false; \
        try { \
            (void)(expr); \
        } catch (const exc_type&) { \
            _threw_expected = true; \
        } catch (...) { \
            _threw_other = true; \
        } \
        if (_threw_expected) { \
            ::msa::test::get_context().record_pass(); \
        } else if (_threw_other) { \
            ::msa::test::get_context().record_fail(__FILE__, __LINE__, #expr " throws " #exc_type, "Different exception type thrown"); \
        } else { \
            ::msa::test::get_context().record_fail(__FILE__, __LINE__, #expr " throws " #exc_type, "No exception thrown"); \
        } \
    } while (false)

#define CHECK_NOTHROW(...) \
    do { \
        bool _threw = false; \
        std::string _what; \
        try { \
            (void)(__VA_ARGS__); \
        } catch (const std::exception& _e) { \
            _threw = true; \
            _what = _e.what(); \
        } catch (...) { \
            _threw = true; \
            _what = "unknown non-std exception"; \
        } \
        if (!_threw) { \
            ::msa::test::get_context().record_pass(); \
        } else { \
            ::msa::test::get_context().record_fail(__FILE__, __LINE__, #__VA_ARGS__ " does not throw", "Unexpected exception: " + _what); \
        } \
    } while (false)
