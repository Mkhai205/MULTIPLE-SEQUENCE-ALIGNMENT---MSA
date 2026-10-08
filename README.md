# Multiple Sequence Alignment (MSA) C++17 System
## Nhóm 5: Thuật toán Chia để trị Song song kết hợp Quy hoạch động cho Căn chỉnh Đa chuỗi Protein/ADN

> **Môn học**: Phân tích và Thiết kế Thuật toán  
> **Nền tảng lý thuyết**: Quy hoạch động (Dynamic Programming), Chia để trị (Divide & Conquer), Tính toán song song (Parallel Computing OpenMP).  
> **Tính mới & Đóng góp khoa học**: Tối ưu không gian bộ nhớ từ $O(mn)$ xuống $O(\min(m, n))$ bằng thuật toán Myers-Miller (Hirschberg affine gap), kết hợp song song hóa đa tầng trên OpenMP, đánh giá độ chính xác sinh học trên tập chuẩn chuẩn quốc tế BAliBASE 3.0 (SP score và TC score).

---

## 1. Kiến trúc Hệ thống (System Architecture)

Hệ thống được tổ chức theo kiến trúc modular hướng module C++17 hiện đại, tuân thủ nguyên tắc Clean Code và Separation of Concerns:

```
MSA/
├── include/msa/
│   ├── core/           # Sequence, Profile (Sum-of-Pairs), Blosum62, ScoreModel
│   ├── align/          # Needleman-Wunsch Gotoh DP, Myers-Miller Linear-Space, ProfileAligner
│   ├── tree/           # DistanceMatrix, UPGMA Hierarchical Clustering, GuideTree
│   ├── parallel/       # Wavefront Anti-Diagonal OpenMP DP, TreeScheduler Concurrency
│   ├── eval/           # BAliBASE MSF/FASTA Parser, SP Score, TC Score, MemoryTracker, Benchmark
│   └── io/             # FASTA I/O (Parser/Writer, Stream/File), CLI Parser
├── src/                # Implementation files tương ứng
├── tests/
│   ├── unit/           # 107 unit tests (139,446 assertions)
│   └── e2e/            # 234 end-to-end integration tests
└── data/balibase/      # Tập dữ liệu benchmark chuẩn BAliBASE (RV11, RV12, RV20)
```

---

## 2. Pipeline Xử lý Căn chỉnh Đa chuỗi (MSA Progressive Pipeline)

Quy trình căn chỉnh tuần tự tiến bộ (Progressive Alignment) gồm 4 giai đoạn chính:

```
[Input Sequences (FASTA/MSF)]
             │
             ▼
┌─────────────────────────┐
│   All-Pairs Distance    │ ◄── Song song hóa OpenMP: N*(N-1)/2 cặp độc lập
│    d(A, B) Matrix       │     d(A, B) = 1.0 - S(A, B) / max(S(A, A), S(B, B))
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   UPGMA Clustering      │ ◄── Cây hướng dẫn phân cấp nhị phân (Guide Tree)
│    Binary Guide Tree    │     Gom cụm tuần tự theo khoảng cách trung bình
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Progressive Profile     │ ◄── Song song hóa OpenMP Task/Sections trên các nhánh độc lập
│       Alignment         │     Căn chỉnh Profile-to-Profile bằng Myers-Miller Linear Space
└────────────┬────────────┘     Điểm Sum-of-Pairs + Bảo tồn vị trí khoảng trống (Gap Propagation)
             │
             ▼
[Aligned Multiple Sequences (FASTA) + BAliBASE SP/TC Evaluation]
```

---

## 3. Phân tích Độ phức tạp Thuật toán (Complexity Analysis)

| Giai đoạn / Thuật toán | Độ phức tạp Thời gian | Độ phức tạp Bộ nhớ | Ghi chú & Đóng góp |
| :--- | :---: | :---: | :--- |
| **Gotoh Needleman-Wunsch Baseline** | $O(mn)$ | $O(mn)$ | Bùng nổ không gian trạng thái khi $m, n \ge 10^4$ |
| **Myers-Miller / Hirschberg (Đề xuất)** | $O(mn)$ | $O(\min(m, n))$ | **Giảm bộ nhớ $> 90\times - 250\times$**, điểm số đồng nhất 100% với NW |
| **Wavefront Anti-Diagonal DP** | $O\left(\frac{mn}{p}\right)$ | $O(\min(m, n))$ | Song song hóa đường chéo phụ theo wavefront OpenMP |
| **Tính Ma trận Khoảng cách** | $O\left(\frac{N^2 \cdot L^2}{p}\right)$ | $O(N^2)$ | Phân bổ song song $N(N-1)/2$ cặp trên $p$ luồng |
| **Cây Hướng dẫn UPGMA** | $O(N^2)$ | $O(N^2)$ | Gom cụm phân cấp xác định (deterministic tie-breaking) |
| **Tiến trình Progressive Tree** | $O\left(\frac{N \cdot L^2}{p}\right)$ | $O(N \cdot L)$ | Duyệt cây dưới lên, song song nhánh độc lập |

---

## 4. Hướng dẫn Biên dịch (Build Instructions)

### Yêu cầu hệ thống:
- C++17 Compiler (MSVC 2019+, GCC 9+, hoặc Clang 10+)
- CMake 3.16 trở lên
- Hỗ trợ OpenMP (`OpenMP::OpenMP_CXX`)

### Lệnh biên dịch trên Windows (Visual Studio / MSVC):
```powershell
# Tạo thư mục build và cấu hình
cmake -B build -DCMAKE_BUILD_TYPE=Release

# Biên dịch toàn bộ thư viện, CLI và test suites
cmake --build build --config Release
```

Các file thực thi sinh ra tại `build/Release/`:
- `msa_align.exe`: Ứng dụng dòng lệnh chính.
- `msa_unit_tests.exe`: Bộ kiểm thử đơn vị tự động (107 tests).

---

## 5. Web GUI Dashboard & Trực quan hóa

Hệ thống tích hợp giao diện Single-Page Application (SPA) hiện đại (HTML5, Tailwind CSS, Chart.js, D3/SVG) kết nối với backend Python FastAPI thông qua Subprocess IPC tới `msa_align.exe`.

### Khởi chạy nhanh Web GUI:
- **Trên Windows Command Prompt / PowerShell**:
  ```cmd
  run_gui.bat
  ```
  *(hoặc trong PowerShell: `.\run_gui.bat`)*
- **Trên Git Bash / MinGW / WSL / Linux**:
  ```bash
  ./run_gui.sh
  # hoặc:
  bash run_gui.sh
  ```
- **Khởi chạy trực tiếp bằng Python**:
  ```bash
  python web/server.py
  ```
Script sẽ tự động khởi động máy chủ FastAPI tại `http://localhost:8000` và mở trình duyệt mặc định.

### Các module chức năng trên giao diện Web:
1. **Input & Control Panel**:
   - 4 Demo Presets có sẵn: BAliBASE RV11 (`BB11001.msf`), BAliBASE RV12 (`BB12001.msf`), Gia đình Hemoglobin, và Test kiểm tra bộ nhớ chuỗi dài (~900 aa).
   - Hỗ trợ Kéo & thả file (.fasta, .fa, .msf) và dán trực tiếp sequence.
   - Thanh trượt tùy chỉnh số luồng OpenMP (1, 2, 4, 8), Gap Open (-10), Gap Extend (-1).
   - Tùy chọn chế độ: Standard Alignment, Baseline Comparison, Multi-threaded Benchmark.
2. **Interactive Color-Coded MSA Matrix (Jalview / ClustalX style)**:
   - Mã màu hóa học các amino acid (Kỵ nước: Xanh lam, Phân cực: Xanh lá, Điện tích dương: Đỏ, Điện tích âm: Tím, Gly/Pro: Cam, Khoảng trống: Xám).
   - Thanh thước đo vị trí (1, 10, 20...), cuộn ngang mượt mà, hàng Consensus sequence và Biểu đồ cột mức độ bảo tồn (Conservation Histogram).
3. **UPGMA Guide Tree Visualizer**:
   - Cây phát sinh loài UPGMA tương tác dạng SVG Dendrogram, hiển thị khoảng cách tiến hóa trên từng nhánh, nhãn sequence lá và phóng to/thu nhỏ/pan.
4. **Benchmark & Analytics Dashboard**:
   - Đồ thị Tăng tốc Speedup $S(p)$ và Hiệu suất $E(p)$ tương tác (Chart.js) trên 1, 2, 4, 8 luồng.
   - Thẻ so sánh bộ nhớ: Gotoh $O(mn)$ vs Myers-Miller $O(\min(m, n))$ (tiết kiệm hơn 1.350x bộ nhớ).
   - Thẻ đánh giá độ chính xác sinh học BAliBASE (SP Score & TC Score).
5. **Export Studio**:
   - Xuất file FASTA đã căn chỉnh, file Newick (`.nwk`), ảnh vector SVG cây chỉ dẫn, và báo cáo JSON benchmark.

---

## 6. Hướng dẫn Sử dụng CLI (`msa_align`)

### Các tùy chọn tham số:
```text
Cú pháp: msa_align [OPTIONS] --input <FILE>

Tùy chọn:
  -i, --input <FILE>           Đường dẫn file đầu vào (.fa, .fasta, .msf) [BẮT BUỘC]
  -o, --output <FILE>          Đường dẫn file FASTA kết quả căn chỉnh
      --export-tree <FILE>     Xuất cây UPGMA sang Newick (.nwk) hoặc JSON (.json)
  -t, --threads <NUM>          Số luồng OpenMP xử lý song song [mặc định: 1]
      --gap-open <NUM>         Điểm phạt mở khoảng trống (affine gap open) [mặc định: -10]
      --gap-extend <NUM>       Điểm phạt mở rộng khoảng trống (gap extend) [mặc định: -1]
      --benchmark              Bật chế độ đo đạc hiệu năng song song (Speedup, Efficiency)
      --baseline-compare       So sánh trực tiếp Myers-Miller với Gotoh NW baseline
  -v, --verbose                In chi tiết các bước xử lý
  -h, --help                   Hiển thị thông tin trợ giúp
      --version                Hiển thị phiên bản
```

### Ví dụ sử dụng:

1. **Căn chỉnh đa chuỗi cơ bản**:
   ```powershell
   .\build\Release\msa_align.exe -i data/balibase/BB11001.msf -o aligned.fa -t 4
   ```

2. **So sánh kiểm chứng thuật toán tuyến tính với Gotoh NW**:
   ```powershell
   .\build\Release\msa_align.exe -i data/balibase/BB11001.msf --baseline-compare
   ```
   *Kết quả thực tế*:
   ```text
   Pair: 1aab_ (60 aa) vs 1j46_A (57 aa)
     Gotoh NW Score:       267 (Time: 0.059 ms, Peak Mem: 42,710 B)
     Myers-Miller Score:   267 (Time: 0.127 ms, Peak Mem: 464 B)
     Score Identity:       MATCH (100% IDENTICAL)
     Memory Reduction:     92.0x less memory
   ```

3. **Chạy Benchmark hiệu năng và độ chính xác sinh học**:
   ```powershell
   .\build\Release\msa_align.exe -i data/balibase/BB11001.msf --benchmark
   ```
   *Báo cáo kết quả*:
   ```markdown
   | Threads | Time (ms) | Speedup S(p) | Efficiency E(p) | Peak Mem (MB) | SP Score | TC Score |
   |:-------:|:---------:|:--------------:|:-----------------:|:-------------:|:--------:|:--------:|
   |       1 |      1.88 |           1.00x |           100.0% |          4.69 |   0.9405 |   0.9107 |
   |       2 |      3.33 |           0.56x |            28.2% |          5.09 |   0.9405 |   0.9107 |
   |       4 |      4.87 |           0.39x |             9.6% |          5.38 |   0.9405 |   0.9107 |
   ```

---

## 6. Kiểm thử và Độ tin cậy Hệ thống

- **Unit Tests**: 107/107 test cases vượt qua (139,446 assertions) kiểm tra từ tính toàn vẹn cấu trúc chuỗi, ma trận BLOSUM62 đối xứng, 25 cặp chuỗi ngẫu nhiên đối chiếu NW vs Hirschberg, đến OpenMP Wavefront và BAliBASE evaluation.
- **E2E Tests**: 234/234 test cases vượt qua trên toàn bộ pipeline 4 tầng.
- **Độ tin cậy toán học**: Đảm bảo 100% bảo tồn amino acid ban đầu (không suy biến ký tự, không rơi rụng hay sinh thêm amino acid sai lệch).
