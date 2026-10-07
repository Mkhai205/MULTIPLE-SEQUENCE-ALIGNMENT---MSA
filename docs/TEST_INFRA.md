# TEST_INFRA.md — Multiple Sequence Alignment (MSA) Test Architecture & Infrastructure

## 1. Overview & Architecture

The Multiple Sequence Alignment (MSA) test infrastructure provides a comprehensive, 4-tier opaque-box end-to-end (E2E) testing framework designed in accordance with `ORIGINAL_REQUEST.md` and `PROJECT.md`. The framework is entirely self-contained, header-only (`tests/e2e/e2e_framework.hpp`), and requires zero external dependencies (e.g., GTest, Catch2). It compiles cleanly with C++17 on both Windows (MSVC 2019/2022) and Linux (GCC/Clang).

```
tests/
├── CMakeLists.txt              # Umbrella test configuration
└── e2e/
    ├── CMakeLists.txt          # Target 'msa_e2e_tests' build configuration
    ├── e2e_framework.hpp       # Test runner, assertion engine, oracles, datasets
    ├── main.cpp                # CLI test driver with filtering & formatted reports
    ├── test_tier1_features.cpp # Tier 1: 105 Feature Coverage tests (21 features x 5)
    ├── test_tier2_boundaries.cpp # Tier 2: 105 Boundary/Corner tests (21 features x 5)
    ├── test_tier3_combinations.cpp # Tier 3: 12 Cross-Feature combination tests
    └── test_tier4_scenarios.cpp # Tier 4: 12 Real-World Application scenarios
```

---

## 2. 4-Tier Testing Methodology

The test suite contains **234 test cases** divided across 4 distinct tiers:

| Tier | Name | Target Scope | Test Count | Description |
|:---:|:---|:---|:---:|:---|
| **Tier 1** | **Feature Coverage** | Features 1–21 (>= 5 tests/feat) | 105 | Happy-path verification of every feature in `PROJECT.md § Feature Inventory`. |
| **Tier 2** | **Boundary & Corner Cases** | Features 1–21 (>= 5 tests/feat) | 105 | Extreme inputs, empty sequences, single residues, disparate lengths (50 vs 1000 aa), ambiguous residues, zero distances, star topologies, memory limits. |
| **Tier 3** | **Cross-Feature Combinations** | Multi-feature pipelines | 12 | Pairwise coverage between interacting subsystems (e.g. Affine Hirschberg + Wavefront DP + ambiguous codes; UPGMA + Task OpenMP + Gap propagation). |
| **Tier 4** | **Real-World Application Scenarios** | End-to-end biological pipelines | 12 | Real biological datasets: Globin family, Kinase domain, Zinc Finger repeats, Cytochrome C, BAliBASE RV11, RV12, and RV20 subsets. |
| **Total** | | | **234** | **100% Comprehensive E2E Verification** |

---

## 3. Feature-to-Test Mapping Matrix

Each of the 21 features defined in `PROJECT.md` is covered by at least 5 Tier 1 tests and 5 Tier 2 tests:

| Feature # | Feature Name | Tier 1 Tests (Feature Coverage) | Tier 2 Tests (Boundaries & Corners) |
|:---:|:---|:---|:---|
| **1** | FASTA Sequence Parser & Validator | `T1_F1_01` – `T1_F1_05` (5 tests) | `T2_F1_01` – `T2_F1_05` (5 tests) |
| **2** | BLOSUM62 Scoring Matrix | `T1_F2_01` – `T1_F2_05` (5 tests) | `T2_F2_01` – `T2_F2_05` (5 tests) |
| **3** | Affine Gap Penalty Model | `T1_F3_01` – `T1_F3_05` (5 tests) | `T2_F3_01` – `T2_F3_05` (5 tests) |
| **4** | Needleman-Wunsch 3-Matrix Aligner | `T1_F4_01` – `T1_F4_05` (5 tests) | `T2_F4_01` – `T2_F4_05` (5 tests) |
| **5** | Hirschberg Forward/Backward DP Kernel | `T1_F5_01` – `T1_F5_05` (5 tests) | `T2_F5_01` – `T2_F5_05` (5 tests) |
| **6** | Myers-Miller Midpoint Recombination | `T1_F6_01` – `T1_F6_05` (5 tests) | `T2_F6_01` – `T2_F6_05` (5 tests) |
| **7** | Profile Data Structure & Sum-of-Pairs | `T1_F7_01` – `T1_F7_05` (5 tests) | `T2_F7_01` – `T2_F7_05` (5 tests) |
| **8** | Hirschberg Profile Aligner | `T1_F8_01` – `T1_F8_05` (5 tests) | `T2_F8_01` – `T2_F8_05` (5 tests) |
| **9** | All-Pairs Distance Matrix | `T1_F9_01` – `T1_F9_05` (5 tests) | `T2_F9_01` – `T2_F9_05` (5 tests) |
| **10** | UPGMA Hierarchical Clustering | `T1_F10_01` – `T1_F10_05` (5 tests) | `T2_F10_01` – `T2_F10_05` (5 tests) |
| **11** | Progressive Profile & Gap Propagation | `T1_F11_01` – `T1_F11_05` (5 tests) | `T2_F11_01` – `T2_F11_05` (5 tests) |
| **12** | FASTA Aligned Output Writer | `T1_F12_01` – `T1_F12_05` (5 tests) | `T2_F12_01` – `T2_F12_05` (5 tests) |
| **13** | OpenMP Task/Sections Tree Parallelism | `T1_F13_01` – `T1_F13_05` (5 tests) | `T2_F13_01` – `T2_F13_05` (5 tests) |
| **14** | OpenMP Anti-Diagonal Wavefront DP | `T1_F14_01` – `T1_F14_05` (5 tests) | `T2_F14_01` – `T2_F14_05` (5 tests) |
| **15** | All-Pairs Distance Parallelism | `T1_F15_01` – `T1_F15_05` (5 tests) | `T2_F15_01` – `T2_F15_05` (5 tests) |
| **16** | BAliBASE 3.0 Reference Parsers | `T1_F16_01` – `T1_F16_05` (5 tests) | `T2_F16_01` – `T2_F16_05` (5 tests) |
| **17** | SP (Sum-of-Pairs) Score Metric Engine | `T1_F17_01` – `T1_F17_05` (5 tests) | `T2_F17_01` – `T2_F17_05` (5 tests) |
| **18** | TC (Total Column) Score Metric Engine | `T1_F18_01` – `T1_F18_05` (5 tests) | `T2_F18_01` – `T2_F18_05` (5 tests) |
| **19** | Benchmark Harness & Memory Profiling | `T1_F19_01` – `T1_F19_05` (5 tests) | `T2_F19_01` – `T2_F19_05` (5 tests) |
| **20** | CLI Application & Options Parser | `T1_F20_01` – `T1_F20_05` (5 tests) | `T2_F20_01` – `T2_F20_05` (5 tests) |
| **21** | CMake Build System & Documentation | `T1_F21_01` – `T1_F21_05` (5 tests) | `T2_F21_01` – `T2_F21_05` (5 tests) |

---

## 4. Expected Output Derivation & Authoritative Sources

All assertions in the test suite are derived from explicit authoritative sources:
1. **BLOSUM62 Scoring Oracle**: Hardcoded 24x24 reference matrix (`Henikoff & Henikoff, 1992`) matching NCBI BLAST standard values.
2. **Gotoh 3-Matrix Dynamic Programming Reference**: Authoritative reference Gotoh NW implementation in `e2e_framework.hpp` (`ReferenceGotohAlign`) computing optimal $M, I_x, I_y$ states, global score, and deterministic traceback.
3. **Normalized Distance & UPGMA Formulations**: Exact formulas:
   $$d(A, B) = 1.0 - \frac{S(A, B)}{\max(S(A, A), S(B, B))}$$
   Clamped strictly to $[0.0, 2.0]$.
4. **BAliBASE 3.0 Standard Evaluation**: Reference SP and TC evaluation functions (`ReferenceComputeSP`, `ReferenceComputeTC`) utilizing $O(1)$ inverse residue-to-column lookup tables against reference core blocks (`Thompson et al., 2005`).
5. **Sequence Invariant Conservation**: Mathematical invariants:
   - Non-gap character conservation: $\text{strip\_gaps}(S_{aligned}) == S_{raw}$.
   - Uniform alignment length: $|S^{(i)}_{aligned}| == |S^{(j)}_{aligned}|$ for all $i, j$.
   - Memory linearity: Peak memory $\le 5 \times \min(m, n) \times \text{sizeof}(int)$.

---

## 5. Embedded Biological Datasets

To ensure zero-network, 100% offline reproducibility across air-gapped CI environments, the test framework embeds curated standard datasets:
- **Globin Family**: 5 sequences (HBA_HUMAN, HBB_HUMAN, MYG_HUMAN, LGB1_SOYBN, NGB_HUMAN).
- **Kinase Domain**: 4 sequences (KAPCA_HUMAN, CDK2_HUMAN, MK01_HUMAN, SRC_HUMAN).
- **Zinc Finger Repeats**: 3 C2H2 sequences (ZF1, ZF2, ZF3).
- **Cytochrome C**: 4 evolutionary sequences across eukaryotic kingdoms (Human, Chick, Drosophila, Yeast).
- **BAliBASE RV11**: BB11001 reference alignment and core block coordinates (< 20% identity).
- **BAliBASE RV12**: BB12001 reference alignment and core block coordinates (20–40% identity).
- **BAliBASE RV20**: BB20001 reference alignment and core block coordinates (large family with core).

---

## 6. How to Build and Execute the Tests

### 6.1 Building via CMake (Windows MSVC)
```powershell
# From project root
cmake -S . -B build -G "Visual Studio 16 2019" -A x64
cmake --build build --config Release --target msa_e2e_tests
```

### 6.2 Running the Full Suite
```powershell
.\build\Release\msa_e2e_tests.exe
```

### 6.3 Filtering by Tier or Feature
```powershell
# Run only Tier 1 (Feature Coverage)
.\build\Release\msa_e2e_tests.exe --tier 1

# Run only Tier 2 (Boundaries & Corners)
.\build\Release\msa_e2e_tests.exe --tier 2

# Run only Tier 3 (Cross-Feature Combinations)
.\build\Release\msa_e2e_tests.exe --tier 3

# Run only Tier 4 (Real-World Application Scenarios)
.\build\Release\msa_e2e_tests.exe --tier 4

# Filter by Feature (e.g. Feature 4 Needleman-Wunsch)
.\build\Release\msa_e2e_tests.exe --feature F4

# Filter by Substring with Verbose Output
.\build\Release\msa_e2e_tests.exe --filter Globin --verbose
```

### 6.4 Running via CTest
```powershell
ctest --test-dir build -C Release --output-on-failure
```
