#include "test_framework.hpp"

int main(int argc, char* argv[]) {
    return ::msa::test::TestRegistry::instance().run_all(argc, argv);
}
