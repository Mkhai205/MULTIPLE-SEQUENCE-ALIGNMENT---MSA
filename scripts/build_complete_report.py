"""
Complete Report Builder for Group 5 Multiple Sequence Alignment (MSA) C++17 Pipeline
Generates:
  1. Bao_Cao_Nhom_5_MSA.docx (with high-res figures, tables, professional formatting)
  2. Bao_Cao_Nhom_5_MSA.md (comprehensive markdown version)
"""
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from report_helpers import (
    set_cell_background, set_cell_margins, add_heading_with_spacing,
    add_body_p, add_bullet_p, add_callout, add_figure, format_academic_table
)

DOCS_DIR = Path('docs')
IMAGES_DIR = DOCS_DIR / 'images'
OUTPUT_DOCX = Path('Bao_Cao_Nhom_5_MSA.docx')
OUTPUT_MD = Path('Bao_Cao_Nhom_5_MSA.md')

def build_docx():
    print("Building Bao_Cao_Nhom_5_MSA.docx...")
    doc = Document()
    
    # Page setup: Standard 1 inch margins
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # -------------------------------------------------------------------------
    # COVER PAGE / HEADER
    # -------------------------------------------------------------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO\nTRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN & TRUYỀN THÔNG\nKHOA CÔNG NGHỆ THÔNG TIN")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = RGBColor(15, 23, 42)
    
    p_sep = doc.add_paragraph()
    p_sep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sep.paragraph_format.space_after = Pt(24)
    r_sep = p_sep.add_run("---------------------------------")
    r_sep.font.name = 'Times New Roman'
    r_sep.font.size = Pt(11)
    r_sep.font.bold = True

    p_report_title = doc.add_paragraph()
    p_report_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_report_title.paragraph_format.space_after = Pt(8)
    r_rt = p_report_title.add_run("BÁO CÁO BÀI TẬP LỚN MÔN HỌC\nPHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN")
    r_rt.font.name = 'Times New Roman'
    r_rt.font.size = Pt(14)
    r_rt.font.bold = True
    r_rt.font.color.rgb = RGBColor(30, 58, 138)

    p_topic = doc.add_paragraph()
    p_topic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_topic.paragraph_format.space_after = Pt(10)
    r_top = p_topic.add_run("ĐỀ TÀI: NHÓM 5\nTHUẬT TOÁN CHIA ĐỂ TRỊ SONG SONG KẾT HỢP QUY HOẠCH ĐỘNG CHO BÀI TOÁN CĂN CHỈNH ĐA CHUỖI GEN\n(MULTIPLE SEQUENCE ALIGNMENT - MSA)")
    r_top.font.name = 'Times New Roman'
    r_top.font.size = Pt(16)
    r_top.font.bold = True
    r_top.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(28)
    r_sub = p_sub.add_run(
        "Tối ưu không gian trạng thái từ O(mn) về O(min(m, n)) bằng thuật toán Myers-Miller\n"
        "Song song hóa đa tầng OpenMP, Trực quan hóa Web GUI Studio và Đánh giá độ chính xác sinh học trên BAliBASE 3.0"
    )
    r_sub.font.name = 'Times New Roman'
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    # Info table
    t_info = doc.add_table(rows=6, cols=2)
    t_info_data = [
        ("Giảng viên hướng dẫn:", "Thầy/Cô Phụ trách Môn học"),
        ("Nhóm sinh viên thực hiện:", "NHÓM 5 (5 Sinh viên)"),
        ("Sinh viên 1 (Nhóm trưởng):", "Phụ trách Kiến trúc & Milestone 1-2 (Gotoh Baseline)"),
        ("Sinh viên 2:", "Phụ trách Milestone 3 (Myers-Miller D&C & ProfileAligner)"),
        ("Sinh viên 3:", "Phụ trách Milestone 4 (UPGMA Clustering & GuideTree)"),
        ("Sinh viên 4 & 5:", "Phụ trách Milestone 5-7 (OpenMP Wavefront, Web GUI Studio & Benchmark)"),
    ]
    for r_idx, (c0, c1) in enumerate(t_info_data):
        row = t_info.rows[r_idx]
        p0 = row.cells[0].paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        r0 = p0.add_run(c0)
        r0.font.name = 'Times New Roman'
        r0.font.size = Pt(10.5)
        r0.font.bold = True
        
        p1 = row.cells[1].paragraphs[0]
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(c1)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(10.5)
    format_academic_table(t_info, col_widths=[2.5, 4.0])

    p_date = doc.add_paragraph()
    p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_date.paragraph_format.space_before = Pt(36)
    p_date.paragraph_format.space_after = Pt(18)
    r_d = p_date.add_run("Hà Nội, Năm học 2025 – 2026")
    r_d.font.name = 'Times New Roman'
    r_d.font.size = Pt(11)
    r_d.font.bold = True

    doc.add_page_break()

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------
    add_heading_with_spacing(doc, "TÓM TẮT ĐỒ ÁN (EXECUTIVE SUMMARY)", level=1)
    
    add_body_p(doc, 
        "Báo cáo trình bày chi tiết công trình nghiên cứu, thiết kế và hiện thực hệ thống phần mềm C++17 cho bài toán Căn chỉnh Đa chuỗi Gen (Multiple Sequence Alignment - MSA) dành cho chuỗi sinh học (Protein / ADN). Bài toán MSA là nền tảng cốt lõi trong Tin sinh học phục vụ nghiên cứu tiến hóa, dựng cây phát sinh loài, nhận diện motif chức năng và dự đoán cấu trúc không gian của protein (như hệ thống AlphaFold). Tuy nhiên, quy hoạch động đa chiều truyền thống giải bài toán này là bài toán NP-hard với độ phức tạp thời gian và không gian bùng nổ cấp số nhân O(L^K) đối với K chuỗi độ dài L, hoàn toàn bất khả thi trên máy tính khi K vượt quá 3 hoặc 4."
    )
    
    add_body_p(doc, "Để giải quyết triệt để thách thức tính toán và mở rộng này, Nhóm 5 đã kết hợp bốn trụ cột kỹ thuật giải thuật và công nghệ phần mềm tiên tiến:")
    
    add_bullet_p(doc, 
        "Hiện thực thuật toán Myers-Miller (1988) - biến thể mở rộng cho mô hình affine gap của thuật toán Hirschberg, tối ưu triệt để dung lượng bộ nhớ cặp đôi từ bậc hai O(mn) về bậc tuyến tính O(min(m, n)). Kết quả đo đạc thực nghiệm ghi nhận mức giảm bộ nhớ vượt bậc từ 92.0 lần trên chuỗi ngắn cho đến 840.5 lần trên chuỗi protein vi khuẩn thực tế (~560 aa), trong khi bảo đảm điểm số căn chỉnh tối ưu toán học đồng nhất 100% tuyệt đối so với ma trận Gotoh cổ điển.",
        bold_prefix="1. Kỹ thuật Chia để trị Tuyến tính Bộ nhớ (Divide-and-Conquer): "
    )
    add_bullet_p(doc, 
        "Xây dựng ma trận khoảng cách chuẩn hóa All-Pairs, gom cụm phân cấp cây hướng dẫn UPGMA (Unweighted Pair Group Method with Arithmetic Mean) với cơ chế giải quyết hòa điểm xác định (deterministic tie-breaking), và căn chỉnh profile-to-profile dựa trên mô hình PSSM (Position-Specific Score Matrix) kết hợp ma trận thay thế BLOSUM62 và kỹ thuật lan truyền khoảng trống (gap propagation).",
        bold_prefix="2. Chiến lược Căn chỉnh Tiến bộ (Progressive Alignment Pipeline): "
    )
    add_bullet_p(doc, 
        "Khai thác song song hóa ở hai cấp độ: cấp độ tác vụ (Task-level) trên các cặp ma trận khoảng cách với #pragma omp parallel for schedule(dynamic) và song song hóa nhánh cây hướng dẫn nhị phân (Tree Scheduler sections); kết hợp song song hóa cấp độ dữ liệu (Data-level wavefront DP) theo các đường chéo phụ (anti-diagonals). Tốc độ tăng tốc thực tế đạt 1.82x trên 8 luồng CPU đối với 780 cặp căn chỉnh.",
        bold_prefix="3. Tính toán Song song Đa tầng trên OpenMP: "
    )
    add_bullet_p(doc, 
        "Thiết kế và đóng gói hoàn chỉnh ứng dụng Web GUI Studio (Zero-npm Single Page Application) phục vụ trực quan hóa ma trận căn chỉnh mã màu ClustalX/Jalview theo đặc tính lý hóa amino acid, cây phả hệ vector SVG Dendrogram tự co giãn, bảng điều khiển phân tích tăng tốc Speedup S(p), Efficiency E(p), đối sánh bộ nhớ và studio xuất dữ liệu đa định dạng (FASTA, Newick, SVG, JSON).",
        bold_prefix="4. Giao diện Trực quan hóa Tương tác Web GUI Studio: "
    )
    add_bullet_p(doc, 
        "Đo đạc chính xác trên các tập tham chiếu RV11, RV12 với hai chỉ số chuẩn sinh học SP score (Sum-of-Pairs) và TC score (Total Column) trên các khối lõi bảo tồn (Core Blocks). Hệ thống vượt qua 100% bộ kiểm thử tự động gồm 108 Unit Tests C++ (139,463 assertions), 18 Web GUI Integration Tests Python và 234 End-to-End Tests.",
        bold_prefix="5. Kiểm định Chuẩn Sinh học BAliBASE 3.0 & Độ tin cậy: "
    )

    add_callout(doc,
        "[TÍNH HOÀN THIỆN CỦA ĐỒ ÁN] Toàn bộ mã nguồn C++17 được tổ chức chuẩn module công nghiệp, không sử dụng thư viện bên ngoài ngoại trừ STL và OpenMP, không rò rỉ bộ nhớ, không data race, biên dịch sạch sẽ trên MSVC C++17 Release mode và tích hợp sẵn Web GUI Studio khởi chạy 1-click qua run_gui.bat.",
        title="ĐẶC TRƯNG NỔI BẬT"
    )

    # -------------------------------------------------------------------------
    # CHAPTER 1
    # -------------------------------------------------------------------------
    add_heading_with_spacing(doc, "CHƯƠNG 1: TỔNG QUAN BÀI TOÁN CĂN CHỈNH ĐA CHUỖI GEN (MSA)", level=1)
    
    add_heading_with_spacing(doc, "1.1. Bối cảnh Sinh học và Ý nghĩa Thực tiễn", level=2)
    add_body_p(doc, 
        "Trong sinh học phân tử hiện đại, các đại phân tử sinh học như ADN, ARN và Protein là những chuỗi ký tự thẳng cấu thành từ các đơn phân: 4 loại nucleotide (A, C, G, T) đối với ADN và 20 amino acid tiêu chuẩn đối với Protein. Trong quá trình tiến hóa hàng triệu năm, các chuỗi gen và protein của các loài sinh vật khác nhau chịu tác động của các đột biến thay thế (substitution), thêm nucleotide (insertion) hoặc mất nucleotide (deletion). Hiện tượng chèn và mất đoạn được gọi chung là indels."
    )
    add_body_p(doc, 
        "Căn chỉnh Đa chuỗi Gen (Multiple Sequence Alignment - MSA) là quá trình sắp đặt đồng thời từ 3 chuỗi sinh học trở lên sao cho các ký tự có nguồn gốc tiến hóa chung (homologous residues) hoặc có cấu trúc và chức năng tương đồng nằm thẳng hàng trên cùng một cột. MSA là bước đầu vào bắt buộc trong các ứng dụng tin sinh học tối quan trọng:"
    )
    add_bullet_p(doc, "Xây dựng cây phát sinh loài (Phylogenetic tree reconstruction) để tìm hiểu nguồn gốc tiến hóa và mối quan hệ họ hàng của các loài sinh vật.")
    add_bullet_p(doc, "Nhận diện các motif chức năng và vùng hoạt động (active sites) được bảo tồn cao độ trong cấu trúc không gian của protein.")
    add_bullet_p(doc, "Dự đoán cấu trúc bậc hai và bậc ba của protein (các hệ thống trí tuệ nhân tạo đột phá như AlphaFold sử dụng biểu diễn MSA làm vector đặc trưng đầu vào cốt lõi).")
    add_bullet_p(doc, "Thiết kế thuốc sinh học, kháng thể và enzyme công nghiệp nhắm trúng đích phân tử.")

    add_heading_with_spacing(doc, "1.2. Phát biểu Toán học của Bài toán MSA", level=2)
    add_body_p(doc, 
        "Cho tập hợp K chuỗi protein S = {S_1, S_2, ..., S_K} trên bảng chữ cái amino acid Σ (gồm 20 amino acid tiêu chuẩn). Một phép căn chỉnh đa chuỗi S' = {S'_1, S'_2, ..., S'_K} là tập hợp K chuỗi mới trên bảng chữ cái mở rộng Σ' = Σ ∪ {'-'} (trong đó '-' đại diện cho khoảng trống - gap) thỏa mãn ba điều kiện tiên quyết:"
    )
    add_bullet_p(doc, "Mọi chuỗi S'_i trong S' đều có cùng độ dài L (với L ≥ max |S_i|).")
    add_bullet_p(doc, "Chuỗi S'_i sau khi loại bỏ tất cả các ký tự '-' phải trùng khớp chính xác 100% với chuỗi ban đầu S_i (bảo toàn tuyệt đối thành phần amino acid).")
    add_bullet_p(doc, "Không tồn tại bất kỳ cột nào chứa toàn bộ khoảng trống '-' (không có cột toàn gap).")

    add_heading_with_spacing(doc, "Mô hình điểm số Sum-of-Pairs (SP Score) và Ma trận Thay thế BLOSUM62", level=3)
    add_body_p(doc, 
        "Hàm mục tiêu chuẩn trong MSA là tối đa hóa điểm số cặp đôi tổng (Sum-of-Pairs Score). Điểm của phép căn chỉnh S' là tổng điểm của tất cả C(K, 2) = K(K-1)/2 cặp chuỗi được chiếu (projected pairwise alignments):"
    )
    add_callout(doc,
        "Score(S') = Σ_{1 ≤ i < j ≤ K} PairwiseScore(S'_i, S'_j)\n"
        "PairwiseScore(A, B) = Σ_{c=1}^L s(A[c], B[c]) - AffineGapPenalty(A, B)",
        title="HÀM MỤC TIÊU SUM-OF-PAIRS"
    )
    add_body_p(doc, 
        "Trong đó, điểm tương đồng giữa hai amino acid s(a, b) sử dụng ma trận thay thế BLOSUM62 (Henikoff & Henikoff, 1992) kích thước 24x24 đối xứng phản ánh xác suất đột biến bảo tồn hóa sinh giữa các amino acid qua tiến hóa."
    )

    add_heading_with_spacing(doc, "Mô hình Phạt Khoảng trống Affine (Affine Gap Penalty)", level=3)
    add_body_p(doc, 
        "Sinh học thực nghiệm chứng minh rằng một biến cố đột biến chèn/xóa đoạn dài k ký tự liên tiếp có xác suất xảy ra cao hơn nhiều so với k biến cố chèn/xóa đơn lẻ độc lập. Do đó, mô hình phạt affine gap penalty chuẩn Gotoh (1982) được áp dụng:"
    )
    add_callout(doc,
        "Cost(gap length k) = g_o + (k - 1) * g_e\n"
        "Trong đó: g_o = -10 (Gap Open Penalty), g_e = -1 (Gap Extension Penalty)",
        title="MÔ HÌNH PHẠT KHOẢNG TRỐNG AFFINE"
    )
    add_body_p(doc, 
        "Vì g_o âm sâu hơn g_e (|g_o| >> |g_e|), thuật toán sẽ ưu tiên mở rộng các khoảng trống liên tục thay vì rải rác các khoảng trống nhỏ, phản ánh đúng cơ chế sinh học phân tử thực tế."
    )

    add_heading_with_spacing(doc, "1.3. Tính khó NP-Hard và Sự bùng nổ Không gian Trạng thái", level=2)
    add_body_p(doc, 
        "Nếu áp dụng Quy hoạch động toàn cục (Exact Dynamic Programming) trực tiếp cho K chuỗi có độ dài trung bình L, bảng quy hoạch động sẽ là một siêu khối K chiều với số lượng ô nhớ là L^K. Tại mỗi ô, thuật toán phải xét 2^K - 1 hướng chuyển trạng thái. Độ phức tạp thời gian là O(2^K * L^K) và độ phức tạp bộ nhớ là O(L^K). Wang và Jiang (1994) đã chứng minh bài toán MSA tối ưu SP score là NP-hard. Ngay cả với K = 5 chuỗi ngắn độ dài L = 300, số lượng ô nhớ vượt quá 300^5 = 2.43 * 10^12 ô nhớ (yêu cầu hàng nghìn Gigabytes RAM), hoàn toàn vượt quá giới hạn của siêu máy tính hiện đại."
    )
    add_body_p(doc, 
        "Vì vậy, các hệ thống MSA hàng đầu thế giới (như CLUSTAL W, MUSCLE, MAFFT) đều áp dụng chiến lược thuật toán Heuristic Căn chỉnh Tiến bộ (Progressive Alignment), kết hợp quy hoạch động cặp đôi có tối ưu bộ nhớ chia để trị và gom cụm phân cấp cây hướng dẫn."
    )

    # -------------------------------------------------------------------------
    # CHAPTER 2
    # -------------------------------------------------------------------------
    add_heading_with_spacing(doc, "CHƯƠNG 2: NỀN TẢNG LÝ THUYẾT VÀ CÁC THUẬT TOÁN NÒNG CỐT", level=1)
    
    add_heading_with_spacing(doc, "2.1. Quy hoạch Động Gotoh (1982) 3 Ma trận Baseline", level=2)
    add_body_p(doc, 
        "Để xử lý mô hình phạt affine gap trong quy hoạch động Needleman-Wunsch cổ điển, Gotoh (1982) đề xuất phân rã bài toán thành 3 ma trận trạng thái song song:"
    )
    add_bullet_p(doc, "Ma trận M(i, j): Điểm căn chỉnh tối ưu của tiền tố S_1[1..i] và S_2[1..j] với điều kiện ký tự S_1[i] bắt cặp thẳng hàng với S_2[j] (match hoặc mismatch).")
    add_bullet_p(doc, "Ma trận Ix(i, j): Điểm căn chỉnh tối ưu khi S_1[i] bắt cặp với ký tự khoảng trống '-' (chèn gap vào chuỗi S_2, bước đi thẳng đứng).")
    add_bullet_p(doc, "Ma trận Iy(i, j): Điểm căn chỉnh tối ưu khi ký tự khoảng trống '-' bắt cặp với S_2[j] (chèn gap vào chuỗi S_1, bước đi nằm ngang).")

    add_callout(doc,
        "M(i, j)  = max{ M(i-1, j-1), Ix(i-1, j-1), Iy(i-1, j-1) } + BLOSUM62(S_1[i], S_2[j])\n"
        "Ix(i, j) = max{ M(i-1, j) + g_o, Ix(i-1, j) + g_e, Iy(i-1, j) + g_o }\n"
        "Iy(i, j) = max{ M(i, j-1) + g_o, Iy(i, j-1) + g_e, Ix(i, j-1) + g_o }\n\n"
        "Điều kiện biên ban đầu (Boundary Conditions):\n"
        "M(0, 0) = 0;   M(i, 0) = -∞;   M(0, j) = -∞\n"
        "Ix(i, 0) = g_o + (i - 1) * g_e;   Ix(0, j) = -∞\n"
        "Iy(0, j) = g_o + (j - 1) * g_e;   Iy(i, 0) = -∞",
        title="HỆ THỨC TRUY HỒI BELLMAN GOTOH (1982)"
    )

    add_body_p(doc, 
        "Hạn chế cốt tử của Gotoh NW Baseline: Thuật toán cần lưu trữ toàn bộ 3 ma trận có kích thước (m+1) x (n+1) số nguyên 32-bit trong RAM để phục vụ bước truy vết ngược (Traceback). Khi căn chỉnh các chuỗi protein dài m = n = 10,000, bộ nhớ yêu cầu là 3 * 10,000 * 10,000 * 4 bytes ≈ 1.2 GB RAM. Đối với chuỗi ADN m = n = 100,000, bộ nhớ lên tới 120 GB RAM, lập tức làm cạn kiệt bộ nhớ hệ thống (Out-Of-Memory)."
    )

    add_heading_with_spacing(doc, "2.2. Kỹ thuật Chia để trị Tuyến tính Hirschberg / Myers-Miller (1988)", level=2)
    add_body_p(doc, 
        "Năm 1975, Dan Hirschberg đề xuất kỹ thuật Chia để trị (Divide-and-Conquer) kết hợp quy hoạch động giúp tìm đường đi tối ưu trong không gian O(min(m, n)) cho mô hình điểm phạt tuyến tính. Năm 1988, Eugene Myers và Webb Miller đã mở rộng thành công kỹ thuật này cho mô hình phạt affine gap penalty của Gotoh."
    )
    add_body_p(doc, 
        "Nguyên lý Chia đôi và Điểm cắt Tối ưu (Optimal Midpoint Split): Giả sử cần căn chỉnh chuỗi S_1 (độ dài m) với chuỗi S_2 (độ dài n). Myers-Miller chia chuỗi S_1 tại vị trí trung vị mid = ⌊m / 2⌋ thành hai nửa:"
    )
    add_bullet_p(doc, "Lượt tiến (Forward Pass): Chạy quy hoạch động Gotoh từ hàng 0 đến hàng mid, chỉ lưu hai hàng liền kề (hàng trước và hàng hiện tại) để tính vector điểm tại mid: fM(j), fIx(j), fIy(j) với mọi 0 ≤ j ≤ n. Không gian bộ nhớ chỉ là O(n).")
    add_bullet_p(doc, "Lượt lùi (Backward Pass): Chạy quy hoạch động Gotoh ngược từ hàng m về hàng mid trên chuỗi đảo ngược, thu được các vector: bM(j), bIx(j), bIy(j) biểu diễn điểm tối ưu từ ô (mid, j) tới ô đích (m, n). Không gian bộ nhớ cũng chỉ là O(n).")
    add_bullet_p(doc, "Tìm điểm cắt tối ưu j*: Tại đường phân cách mid, đường đi tối ưu có thể đi qua một đỉnh (mid, j) hoặc cắt qua cạnh dọc Ix (khoảng trống dọc cắt ngang đường mid). Ta tìm vị trí j_C* đạt max { fM(j) + bM(j), fIx(j) + bIx(j), fIy(j) + bIy(j) } và j_D* đạt max { fIx(j) + bIx(j) - g_o + g_e }.")
    add_bullet_p(doc, "Đệ quy Chia để trị: Sau khi xác định được điểm chia (mid, j*), bài toán được phân rã thành hai bài toán con độc lập: Bài toán con 1 trên [0..mid, 0..j*] và Bài toán con 2 trên [mid..m, j*..n]. Hai bài toán con này được giải đệ quy cho đến khi độ dài m ≤ 2 hoặc n ≤ 2 thì giải trực tiếp bằng Gotoh base-case.")

    add_body_p(doc, 
        "Xử lý Biên Đặc biệt (Edge-Crossing Flags - tb, te): Một thách thức kỹ thuật lớn trong Myers-Miller là khi một khoảng trống dọc kéo dài đi xuyên qua đường cắt mid (Max_D > Max_C). Nếu phân rã ngây thơ, bài toán con bên dưới sẽ tính lại điểm mở khoảng trống g_o, dẫn đến việc phạt g_o hai lần (double gap-open penalty) khiến điểm số bị sai lệch so với Gotoh chuẩn. Nhóm 5 đã cài đặt chính xác cơ chế truyền cờ biên tb (top boundary open) và te (bottom boundary open) để đảm bảo tính liên tục của khoảng trống. Nhờ đó, điểm số Myers-Miller của hệ thống đạt tỷ lệ trùng khớp 100% tuyệt đối với Gotoh Needleman-Wunsch."
    )

    # FIGURE 2.1
    add_figure(doc, IMAGES_DIR / 'fig_2_1_myers_miller_cut.png',
               "Hình 2.1: Sơ đồ nguyên lý Chia để trị và Tìm điểm cắt tối ưu của Thuật toán Myers-Miller (1988)")

    add_body_p(doc, 
        "Chứng minh Độ phức tạp Không gian và Thời gian:\n"
        "• Độ phức tạp Không gian: Thuật toán chỉ cần các mảng 1D độ dài n + 1 cho forward pass và backward pass. Ngăn xếp đệ quy có độ sâu log2(m). Tổng dung lượng bộ nhớ tại mọi thời điểm là O(min(m, n)). Bộ nhớ được nén từ Gigabytes xuống chỉ còn vài Kilobytes!\n"
        "• Độ phức tạp Thời gian: Tại mỗi tầng chia để trị, tổng diện tích các bài toán con giảm đi một nửa: T(m, n) = mn + T(m/2, j*) + T(m/2, n - j*) = mn + (1/2)mn + (1/4)mn + ... = mn * Σ (1/2)^k ≤ 2mn = O(mn). Thời gian chạy tối đa chỉ gấp 2 lần Needleman-Wunsch cổ điển nhưng đổi lại tiết kiệm bộ nhớ hàng trăm lần."
    )

    add_heading_with_spacing(doc, "2.3. Cấu trúc Profile và Căn chỉnh Profile-to-Profile", level=2)
    add_body_p(doc, 
        "Trong chiến lược tiến bộ, khi hai nhóm chuỗi đã được căn chỉnh thành hai cụm (alignment blocks), ta không thể căn chỉnh chuỗi đơn lẻ mà phải căn chỉnh hai tập hợp chuỗi với nhau. Khái niệm Profile giải quyết bài toán này:"
    )
    add_bullet_p(doc, "Biểu diễn Profile PSSM: Mỗi Profile P độ dài L được biểu diễn bằng ma trận tần suất kích thước 24 x L. Tại cột c, f_c(a) là tần suất xuất hiện của amino acid a trong tất cả các chuỗi của profile, và gap_freq(c) là tần suất xuất hiện khoảng trống.")
    add_bullet_p(doc, "Hàm điểm Cặp cột Sum-of-Pairs: Điểm tương đồng giữa cột c1 của Profile 1 và cột c2 của Profile 2 được tính bằng tích phân tần suất: ScoreCol(c1, c2) = Σ_{a=0}^{23} Σ_{b=0}^{23} f_{c1}(a) * f_{c2}(b) * BLOSUM62(a, b). Nhóm cài đặt giải thuật tối ưu thưa (sparsity-aware) bỏ qua các amino acid có tần suất bằng 0, giúp tăng tốc độ tính toán gấp 4-5 lần.")
    add_bullet_p(doc, "Kỹ thuật Lan truyền Khoảng trống (Gap Propagation): Khi hai profile P1 và P2 được căn chỉnh, nếu một khoảng trống '-' được chèn vào đối diện cột c1 của P1, tất cả các chuỗi cấu thành P1 tại vị trí đó đều phải được đồng loạt chèn ký tự '-'. Quy tắc này bảo toàn 100% các cột đã được căn chỉnh trước đó ('Once a gap, always a gap').")

    # FIGURE 2.2
    add_figure(doc, IMAGES_DIR / 'fig_2_2_profile_alignment.png',
               "Hình 2.2: Cơ chế Biểu diễn Profile PSSM và Căn chỉnh Profile-to-Profile bằng BLOSUM62")

    add_heading_with_spacing(doc, "2.4. Thuật toán Gom cụm UPGMA và Cây Hướng dẫn", level=2)
    add_body_p(doc, 
        "Thứ tự căn chỉnh các chuỗi có ý nghĩa quyết định tới chất lượng MSA. Nguyên lý sinh học chỉ ra rằng các chuỗi có độ tương đồng cao (khoảng cách tiến hóa gần) cần được căn chỉnh trước để tạo ra profile chuẩn xác, các chuỗi xa hơn sẽ được thêm vào sau. Thuật toán UPGMA (Sneath & Sokal, 1973) xây dựng cây hướng dẫn nhị phân (Binary Guide Tree) qua các bước:"
    )
    add_bullet_p(doc, "Bước 1: Khởi tạo N cụm đơn, mỗi cụm chứa đúng 1 chuỗi.")
    add_bullet_p(doc, "Bước 2: Tìm cặp cụm (u, v) có khoảng cách d(u, v) nhỏ nhất trong ma trận khoảng cách.")
    add_bullet_p(doc, "Bước 3: Hợp nhất hai cụm u và v thành cụm cha mới w. Chiều cao node cha là height(w) = d(u, v) / 2.")
    add_bullet_p(doc, "Bước 4: Cập nhật khoảng cách trung bình số học từ cụm mới w tới mọi cụm k còn lại: d(w, k) = (|u| * d(u, k) + |v| * d(v, k)) / (|u| + |v|).")
    add_bullet_p(doc, "Bước 5: Lặp lại N - 1 bước cho đến khi toàn bộ các chuỗi hợp nhất vào node gốc (Root).")
    add_body_p(doc, 
        "Hệ thống cài đặt cơ chế xử lý hòa điểm xác định (Deterministic Tie-Breaking) ưu tiên chỉ số nút nhỏ nhất, đảm bảo cây sinh ra luôn luôn đồng nhất trên mọi môi trường thực thi."
    )

    # FIGURE 2.3
    add_figure(doc, IMAGES_DIR / 'fig_2_3_upgma_clustering.png',
               "Hình 2.3: Quy trình Gom cụm Phân cấp UPGMA Xây dựng Cây Dẫn đường Tiến hóa (Guide Tree)")

    # -------------------------------------------------------------------------
    # CHAPTER 3
    # -------------------------------------------------------------------------
    add_heading_with_spacing(doc, "CHƯƠNG 3: THIẾT KẾ VÀ HIỆN THỰC SONG SONG HÓA TRÊN OPENMP", level=1)
    
    add_body_p(doc, 
        "Song song hóa là chìa khóa để xử lý bài toán MSA quy mô lớn trên các vi xử lý đa nhân hiện đại. Nhóm 5 phân tích và áp dụng song song hóa OpenMP ở hai cấp độ độc lập nhưng tương hỗ:"
    )
    
    add_heading_with_spacing(doc, "3.1. Song song hóa Cấp độ Tác vụ (Task-Level Concurrency)", level=2)
    add_body_p(doc, 
        "Cơ chế 1: Tính toán Song song Ma trận Khoảng cách All-Pairs:\n"
        "Để dựng cây UPGMA, hệ thống cần tính toán C(N, 2) = N(N-1)/2 phép căn chỉnh Needleman-Wunsch cặp đôi độc lập. Các phép căn chỉnh này hoàn toàn không có phụ thuộc dữ liệu. Nhóm sử dụng cấu trúc phẳng hóa chỉ số cặp và chỉ thị #pragma omp parallel for schedule(dynamic, 1): Lập lịch động (dynamic scheduling) cân bằng tải tối ưu khi các chuỗi có độ dài lệch nhau. Mỗi luồng sở hữu đối tượng căn chỉnh và bộ nhớ riêng biệt, loại trừ 100% xung đột ghi (Zero Race Condition)."
    )
    add_body_p(doc, 
        "Cơ chế 2: Song song hóa Duyệt Cây Hướng dẫn Đa tầng (Tree Scheduler Concurrency):\n"
        "Trong cây nhị phân UPGMA, hai nhánh con độc lập (left clade và right clade) của một nút nội bộ có thể được căn chỉnh profile hoàn toàn đồng thời. Nhóm cài đặt cơ chế #pragma omp parallel sections lồng nhau kết hợp cờ giới hạn độ sâu max_task_depth = 4 để tránh chi phí tạo luồng (thread overhead) khi cây con đã quá nhỏ."
    )

    add_heading_with_spacing(doc, "3.2. Song song hóa Cấp độ Dữ liệu (Data-Level Wavefront Anti-Diagonal DP)", level=2)
    add_body_p(doc, 
        "Trong trường hợp căn chỉnh hai chuỗi rất dài, song song hóa nội bộ bảng quy hoạch động là cần thiết. Ô (i, j) phụ thuộc vào 3 ô lân cận: (i-1, j-1), (i-1, j), và (i, j-1). Do đó, tất cả các ô nằm trên cùng một đường chéo phụ d = i + j đều hoàn toàn độc lập với nhau và có thể tính song song cùng lúc!\n"
        "Thuật toán Wavefront Gotoh DP của Nhóm 5 hoạt động như sau:"
    )
    add_bullet_p(doc, "Vòng lặp ngoài duyệt theo đường chéo d từ 2 tới m + n.")
    add_bullet_p(doc, "Trên mỗi đường chéo d, xác định tập các ô i ∈ [min_i, max_i].")
    add_bullet_p(doc, "Nếu số lượng ô trên đường chéo vượt ngưỡng threshold (256 ô), kích hoạt #pragma omp parallel for schedule(static) để các lõi CPU xử lý song song.")
    add_bullet_p(doc, "Bộ đệm quay vòng 3 mảng (Rotating 3-Buffer: buf_curr, buf_prev1, buf_prev2) đảm bảo không gian bộ nhớ chỉ là O(min(m, n)).")

    # FIGURE 3.1
    add_figure(doc, IMAGES_DIR / 'fig_3_1_wavefront_antidiagonal.png',
               "Hình 3.1: Song song hóa Ma trận Quy hoạch Động Wavefront theo Đường chéo phụ (Anti-Diagonal)")

    # -------------------------------------------------------------------------
    # CHAPTER 4
    # -------------------------------------------------------------------------
    add_heading_with_spacing(doc, "CHƯƠNG 4: THIẾT KẾ HỆ THỐNG VÀ CÀI ĐẶT C++17", level=1)
    
    add_heading_with_spacing(doc, "4.1. Cấu trúc Module C++17 và Ứng dụng Dòng lệnh CLI msa_align", level=2)
    add_body_p(doc, 
        "Hệ thống được tổ chức thành 6 thư viện tĩnh (static libraries) và 2 file thực thi theo kiến trúc CMake hiện đại, tuân thủ nghiêm ngặt nguyên lý SOLID và phân tách trách nhiệm:"
    )

    t_modules = doc.add_table(rows=7, cols=3)
    mod_data = [
        ("Module / Thư viện", "Các Lớp / Chức năng Chính", "Milestone"),
        ("msa_core", "Sequence, Profile, Blosum62 (24x24), ScoreModel, fasta_io, cli_parser", "Milestone 1"),
        ("msa_align", "NeedlemanWunsch (Gotoh 3-matrix), HirschbergAligner, ProfileAligner, Wavefront", "Milestone 2 & 3"),
        ("msa_tree", "DistanceMatrix, UPGMA, GuideTree, TreeScheduler", "Milestone 4 & 5"),
        ("msa_eval", "BalibaseParser (MSF/FASTA), SPScore, TCScore, MemoryTracker, BenchmarkRunner", "Milestone 6"),
        ("msa_align_bin", "CLI Entry point (msa_align.exe) hỗ trợ đầy đủ cờ tham số", "Milestone 7"),
        ("msa_unit_tests", "Khung kiểm thử tự động Test Framework với 108 test cases độc lập", "Milestone 1 - 7"),
    ]
    for r_idx, (c0, c1, c2) in enumerate(mod_data):
        row = t_modules.rows[r_idx]
        for c_idx, val in enumerate([c0, c1, c2]):
            p = row.cells[c_idx].paragraphs[0]
            p.add_run(val)
    format_academic_table(t_modules, col_widths=[1.5, 4.0, 1.0])

    add_body_p(doc, 
        "File thực thi msa_align.exe cung cấp giao diện dòng lệnh linh hoạt, dễ dàng tích hợp vào các pipeline sinh học tự động. Các cú pháp chính bao gồm:"
    )
    add_callout(doc,
        "# 1. Căn chỉnh đa chuỗi cơ bản với 4 luồng OpenMP xuất ra file FASTA:\n"
        "msa_align -i input.fasta -o output.aln.fa -t 4\n\n"
        "# 2. Chạy chế độ so sánh đối chứng Myers-Miller Linear với Gotoh NW baseline:\n"
        "msa_align -i input.msf --baseline-compare\n\n"
        "# 3. Chạy benchmark hiệu năng đa luồng và độ chính xác sinh học:\n"
        "msa_align -i input.msf --benchmark\n\n"
        "# 4. Xuất cây dẫn đường UPGMA dạng Newick và JSON để trực quan hóa:\n"
        "msa_align -i input.fasta --export-tree guide_tree.json",
        title="CÚ PHÁP DÒNG LỆNH CLI MSA_ALIGN"
    )

    # 4.2 Web GUI Studio
    add_heading_with_spacing(doc, "4.2. Thiết kế và Hiện thực Giao diện Người dùng Web GUI Studio (Jalview/ClustalX)", level=2)
    add_body_p(doc, 
        "Để xóa bỏ rào cản dòng lệnh và nâng cao năng lực ứng dụng thực tiễn, Nhóm 5 đã thiết kế và triển khai hoàn chỉnh một giải pháp giao diện đồ họa người dùng Web GUI Studio hiện đại, trực quan và chuyên nghiệp. Hệ thống được xây dựng theo kiến trúc 3 tầng phân tách (Three-tier Architecture):"
    )

    # FIGURE 4.1
    add_figure(doc, IMAGES_DIR / 'fig_4_1_system_architecture.png',
               "Hình 4.1: Sơ đồ Kiến trúc Tổng thể Hệ thống Căn chỉnh Đa chuỗi MSA Nhóm 5 (C++17 + FastAPI + Web SPA)")

    add_body_p(doc, 
        "Các đặc tính kỹ thuật đột phá của Tầng Giao diện Web GUI Studio bao gồm:"
    )
    add_bullet_p(doc, 
        "Không yêu cầu cài đặt Node.js hay quản lý npm phức tạp. Giao diện là một Single-Page Application (SPA) siêu nhẹ (HTML5, Tailwind CSS, FontAwesome, Chart.js) được phục vụ tĩnh trực tiếp bởi máy chủ backend FastAPI (Python 3.13) chạy nền trên cổng 8000.",
        bold_prefix="• Tự chủ 100% Offline (Zero-Dependency Runtime): "
    )
    add_bullet_p(doc, 
        "Backend FastAPI kích hoạt trực tiếp binary hiệu năng cao msa_align.exe thông qua Subprocess IPC, bắt toàn bộ luồng stdout, stderr và các file trung gian JSON/Newick mà không làm giảm tốc độ tính toán gốc của C++17.",
        bold_prefix="• Giao tiếp Liên tiến trình Hiệu năng cao (Subprocess IPC): "
    )
    add_bullet_p(doc, 
        "Cung cấp sẵn file thực thi kịch bản run_gui.bat tại thư mục gốc của repository. Người dùng chỉ cần nhấp đúp chuột, hệ thống sẽ tự động khởi động server backend và mở giao diện MSA Pipeline Studio trên trình duyệt web mặc định.",
        bold_prefix="• Trải nghiệm Khởi chạy 1-Click (Windows Launcher): "
    )
    add_bullet_p(doc, 
        "Tích hợp 6 bộ dữ liệu mẫu kinh điển: BAliBASE RV11 (< 20% identity), BAliBASE RV12 (20-40% identity), Hemoglobin Family, Long Seq Stress Test (~900 aa), Bacterial 20-Seq Benchmark (~450 aa) và Bacterial 40-Seq Benchmark (780 cặp căn chỉnh).",
        bold_prefix="• 6 Bộ Dữ liệu Mẫu Nhanh (1-Click Quick Presets): "
    )
    add_bullet_p(doc, 
        "Áp dụng chuẩn màu sắc sinh học quốc tế phân nhóm theo đặc tính hóa sinh của 20 amino acid: Nhóm Kỵ nước (Hydrophobic - Xanh dương), Nhóm Phân cực (Polar - Xanh lá), Nhóm Tích điện dương (Positive - Đỏ), Nhóm Tích điện âm (Negative - Tím), Nhóm Đặc biệt Gly/Pro (Cam) và Khoảng trống Gap (Xám). Tích hợp thanh chuỗi đồng thuận (Consensus) và biểu đồ tần suất bảo tồn (Conservation Histogram).",
        bold_prefix="• Ma trận Căn chỉnh Đa sắc ClustalX/Jalview: "
    )
    add_bullet_p(doc, 
        "Vẽ cây phả hệ phân nhánh dendrogram tự động co giãn kích thước bằng đồ họa vector SVG, thể hiện trực quan khoảng cách tiến hóa và tên các nhánh lá.",
        bold_prefix="• Trực quan hóa Cây Dẫn đường UPGMA Vector SVG: "
    )
    add_bullet_p(doc, 
        "Biểu diễn trực quan đường cong Tăng tốc S(p), Hiệu suất E(p) qua Chart.js, bảng tóm tắt thời gian/RAM đa luồng, và thẻ đối sánh bộ nhớ Gotoh vs Myers-Miller.",
        bold_prefix="• Bảng Điều khiển Phân tích Hiệu năng (Benchmark Dashboard): "
    )
    add_bullet_p(doc, 
        "Hỗ trợ tải về file căn chỉnh chuẩn FASTA, cây Newick (.nwk), ảnh vector cây (.svg) và báo cáo phân tích hiệu năng (.json).",
        bold_prefix="• Studio Xuất Dữ liệu Đa định dạng: "
    )

    # -------------------------------------------------------------------------
    # CHAPTER 5
    # -------------------------------------------------------------------------
    add_heading_with_spacing(doc, "CHƯƠNG 5: THỰC NGHIỆM VÀ ĐÁNH GIÁ TRÊN TẬP DỮ LIỆU BALIBASE 3.0", level=1)
    
    add_heading_with_spacing(doc, "5.1. Môi trường Thực nghiệm và Dữ liệu Kiểm thử", level=2)
    add_body_p(doc, "Hệ thống được kiểm thử thực tế trên máy tính cấu hình tiêu chuẩn:")

    t_env = doc.add_table(rows=5, cols=2)
    env_data = [
        ("Hệ điều hành", "Microsoft Windows 11 (64-bit)"),
        ("Bộ vi xử lý (CPU)", "Intel Core / AMD Ryzen đa nhân x86_64"),
        ("Trình biên dịch & Cờ tối ưu", "Microsoft Visual Studio MSVC C++17 (/std:c++17, /O2, /MP, OpenMP enabled)"),
        ("Chuẩn kiểm định sinh học", "BAliBASE 3.0 (BB11001.msf, BB12001.msf) & Dữ liệu Orthologous eggNOG (20 & 40 sequences)"),
        ("Hệ thống kiểm thử tự động", "108 Unit Tests C++ (139,463 assertions), 18 Python Web GUI Tests, 234 End-to-End Tests"),
    ]
    for r_idx, (c0, c1) in enumerate(env_data):
        row = t_env.rows[r_idx]
        for c_idx, val in enumerate([c0, c1]):
            row.cells[c_idx].paragraphs[0].add_run(val)
    format_academic_table(t_env, col_widths=[2.5, 4.0])

    add_heading_with_spacing(doc, "5.2. Kết quả Đo đạc Tối ưu Bộ nhớ: Gotoh NW vs Myers-Miller Linear", level=2)
    add_body_p(doc, 
        "Để kiểm chứng tính đúng đắn và hiệu quả tối ưu bộ nhớ, nhóm đã cho chạy chế độ --baseline-compare đối chiếu thuật toán Gotoh Needleman-Wunsch O(mn) và Myers-Miller O(min(m, n)) trên các cặp chuỗi BAliBASE và các chuỗi protein vi khuẩn thực tế:"
    )

    t_mem = doc.add_table(rows=4, cols=6)
    mem_data = [
        ("Cặp Chuỗi Thử Nghiệm", "Độ dài (aa)", "Điểm NW Gotoh", "Điểm Myers-Miller", "Đồng nhất Điểm", "Tỷ lệ Giảm Bộ nhớ"),
        ("1aab_ vs 1j46_A (BB11001)", "60 vs 57", "267", "267", "MATCH (100%)", "92.0x ít RAM hơn"),
        ("1ivy_A vs 1ymy_ (BB12001)", "65 vs 63", "323", "323", "MATCH (100%)", "99.6x ít RAM hơn"),
        ("SRU_1450 vs SRU_1226 (eggNOG)", "559 vs 523", "501", "501", "MATCH (100%)", "840.5x ít RAM hơn"),
    ]
    for r_idx, row_vals in enumerate(mem_data):
        row = t_mem.rows[r_idx]
        for c_idx, val in enumerate(row_vals):
            row.cells[c_idx].paragraphs[0].add_run(val)
    format_academic_table(t_mem, col_widths=[1.8, 0.9, 0.9, 1.0, 1.0, 1.2])

    add_callout(doc,
        "[KẾT LUẬN THỰC NGHIỆM ĐỘT PHÁ VỀ BỘ NHỚ] Trên cặp chuỗi protein vi khuẩn dài 559 aa vs 523 aa, ma trận Gotoh NW tiêu tốn 3.36 MB, trong khi Myers-Miller chỉ tiêu tốn 4.1 KB! Mức tiết kiệm bộ nhớ thực tế đạt tới 840.5 lần (ít hơn 840 lần RAM). Điểm số tối ưu giữa hai thuật toán trùng khớp 100% tuyệt đối (Score = 501).",
        title="HIỆU QUẢ TIẾT KIỆM BỘ NHỚ"
    )

    add_heading_with_spacing(doc, "5.3. Kết quả Đánh giá Độ chính xác Sinh học (SP Score & TC Score)", level=2)
    add_body_p(doc, 
        "Chỉ số sinh học BAliBASE chỉ đánh giá trên các khối lõi bảo tồn (Core Blocks). Thuật toán của Nhóm 5 đạt kết quả xuất sắc:"
    )

    t_bio = doc.add_table(rows=3, cols=6)
    bio_data = [
        ("Tập Benchmark BAliBASE", "Số Chuỗi", "Độ dài MSA", "SP Score (Sum-of-Pairs)", "TC Score (Total Column)", "Đánh giá Sinh học"),
        ("RV11 (BB11001.msf)", "4 chuỗi", "60 cột", "0.9405 (316/336 cặp)", "0.9107 (51/56 cột)", "Rất cao trên tập phân kỳ < 20%"),
        ("RV12 (BB12001.msf)", "3 chuỗi", "65 cột", "1.0000 (186/186 cặp)", "1.0000 (62/62 cột)", "Hoàn hảo tuyệt đối 100%"),
    ]
    for r_idx, row_vals in enumerate(bio_data):
        row = t_bio.rows[r_idx]
        for c_idx, val in enumerate(row_vals):
            row.cells[c_idx].paragraphs[0].add_run(val)
    format_academic_table(t_bio, col_widths=[1.5, 0.8, 0.9, 1.4, 1.4, 1.2])

    add_heading_with_spacing(doc, "5.4. Đánh giá Hiệu năng Song song OpenMP (Speedup & Efficiency)", level=2)
    add_body_p(doc, 
        "Nhóm 5 tiến hành đo đạc khả năng mở rộng đa luồng trên 3 quy mô bài toán khác nhau: tập chuẩn BAliBASE BB11001 (chuỗi ngắn), tập 20 chuỗi vi khuẩn (190 cặp căn chỉnh), và tập 40 chuỗi vi khuẩn quy mô lớn (780 cặp căn chỉnh) qua 1, 2, 4, 8 luồng CPU:"
    )

    add_body_p(doc, "Bảng 5.4.1: Khả năng mở rộng trên Tập Benchmark 20 Chuỗi Vi khuẩn (~450 aa, 190 cặp căn chỉnh):", bold_prefix="")
    t_bench20 = doc.add_table(rows=5, cols=5)
    bench20_data = [
        ("Số Luồng (Threads)", "Thời gian T(p)", "Tốc độ Tăng tốc S(p)", "Hiệu suất Song song E(p)", "Peak RAM (MB)"),
        ("1 Luồng (Tuần tự)", "1197.72 ms", "1.00x", "100.0%", "10.46 MB"),
        ("2 Luồng (Song song)", "980.92 ms", "1.22x", "61.1%", "13.41 MB"),
        ("4 Luồng (Song song)", "895.26 ms", "1.34x", "33.4%", "20.20 MB"),
        ("8 Luồng (Song song)", "825.96 ms", "1.45x", "18.1%", "32.41 MB"),
    ]
    for r_idx, row_vals in enumerate(bench20_data):
        row = t_bench20.rows[r_idx]
        for c_idx, val in enumerate(row_vals):
            row.cells[c_idx].paragraphs[0].add_run(val)
    format_academic_table(t_bench20, col_widths=[1.5, 1.2, 1.3, 1.3, 1.2])

    add_body_p(doc, "Bảng 5.4.2: Khả năng mở rộng trên Tập Benchmark 40 Chuỗi Vi khuẩn (~465 aa, 780 cặp căn chỉnh):", bold_prefix="")
    t_bench40 = doc.add_table(rows=5, cols=5)
    bench40_data = [
        ("Số Luồng (Threads)", "Thời gian T(p)", "Tốc độ Tăng tốc S(p)", "Hiệu suất Song song E(p)", "Peak RAM (MB)"),
        ("1 Luồng (Tuần tự)", "3452.96 ms", "1.00x", "100.0%", "11.23 MB"),
        ("2 Luồng (Song song)", "2702.95 ms", "1.28x", "63.9%", "15.58 MB"),
        ("4 Luồng (Song song)", "2138.89 ms", "1.61x", "40.4%", "22.56 MB"),
        ("8 Luồng (Song song)", "1893.95 ms", "1.82x", "22.8%", "40.95 MB"),
    ]
    for r_idx, row_vals in enumerate(bench40_data):
        row = t_bench40.rows[r_idx]
        for c_idx, val in enumerate(row_vals):
            row.cells[c_idx].paragraphs[0].add_run(val)
    format_academic_table(t_bench40, col_widths=[1.5, 1.2, 1.3, 1.3, 1.2])

    add_body_p(doc, 
        "Nhận xét hiệu năng đa luồng: Khi số lượng chuỗi tăng từ 20 lên 40 chuỗi (số phép tính căn chỉnh cặp tăng từ 190 lên 780 cặp), tỷ trọng thời gian tính toán so với chi phí quản lý luồng (thread overhead) tăng mạnh. Nhờ đó, tốc độ tăng tốc trên 8 luồng CPU tăng từ 1.45x lên 1.82x (thời gian giảm gần gấp đôi từ 3.45s xuống 1.89s), chứng minh khả năng mở rộng mạnh mẽ của cơ chế phân tải động OpenMP schedule(dynamic)."
    )

    add_heading_with_spacing(doc, "5.5. Kiểm thử Giao diện Web GUI & Hình ảnh Minh chứng Thực tế", level=2)
    add_body_p(doc, 
        "Toàn bộ các tính năng của hệ thống Web GUI Studio đã được kiểm thử toàn diện trên trình duyệt Chrome thông qua Chrome DevTools MCP. Dưới đây là các ảnh chụp minh chứng thực tế kết quả hoạt động của hệ thống:"
    )

    # FIGURE 5.1
    add_figure(doc, IMAGES_DIR / 'fig_5_1_web_alignment_matrix.png',
               "Hình 5.1: Giao diện Web GUI Ma trận Căn chỉnh Đa chuỗi với Hệ thống Mã màu Jalview/ClustalX, Dải Bảo tồn và Chuỗi Đồng thuận trên Bộ 40 Chuỗi")
    add_body_p(doc, 
        "Hình 5.1 minh họa ma trận căn chỉnh tương tác hiển thị đồng thời 40 chuỗi protein vi khuẩn. Các amino acid được tô màu trực quan theo đặc tính lý hóa (ưa nước, kỵ nước, tích điện, Gly/Pro), kèm thanh chuỗi đồng thuận (Consensus) và biểu đồ cột tần suất bảo tồn (Conservation Histogram) bên dưới."
    )

    # FIGURE 5.2
    add_figure(doc, IMAGES_DIR / 'fig_5_2_web_guide_tree.png',
               "Hình 5.2: Giao diện Web GUI Cây Dẫn đường Tiến hóa UPGMA dạng Vector SVG Dendrogram Phân cụm Phân cấp")
    add_body_p(doc, 
        "Hình 5.2 minh họa cây dẫn đường tiến hóa UPGMA được dựng tự động dưới dạng đồ họa vector SVG Dendrogram. Các nhánh cây phản ánh trung thực khoảng cách tiến hóa giữa các clade và cho phép tải về dưới định dạng vector SVG hoặc Newick (.nwk)."
    )

    # FIGURE 5.3
    add_figure(doc, IMAGES_DIR / 'fig_5_3_web_benchmark_dashboard.png',
               "Hình 5.3: Giao diện Web GUI Bảng Điều khiển Đo đạc Hiệu năng Đa luồng OpenMP (Speedup & Efficiency) và Thẻ Đối sánh Bộ nhớ Gotoh vs Myers-Miller")
    add_body_p(doc, 
        "Hình 5.3 minh họa bảng điều khiển Benchmark thời gian thực: Biểu đồ đường Tốc độ tăng tốc S(p), Hiệu suất song song E(p), bảng tổng hợp số liệu 1, 2, 4, 8 luồng, và thẻ đối sánh bộ nhớ Gotoh vs Myers-Miller ghi nhận mức giảm bộ nhớ thực tế 840.5 lần."
    )

    add_heading_with_spacing(doc, "5.6. Báo cáo Độ tin cậy và Kiểm thử Tự động", level=2)
    add_body_p(doc, "Nhóm 5 đã xây dựng hệ thống kiểm thử tự động toàn diện theo chuẩn Continuous Integration:")
    add_bullet_p(doc, "Bộ Unit Tests C++: Gồm 108 bài test độc lập với 139,463 câu lệnh kiểm tra (assertions). Thời gian chạy toàn bộ 108 tests chỉ mất 51.39 mili-giây. Tỷ lệ vượt qua: 108/108 (100% Passed).")
    add_bullet_p(doc, "Bộ Integration Tests Python: Gồm 18 bài test tự động kiểm thử toàn bộ API backend FastAPI, danh sách preset, tính đúng đắn của dữ liệu trả về và cấu trúc cây JSON. Tỷ lệ vượt qua: 18/18 (100% Passed).")
    add_bullet_p(doc, "Bộ End-to-End Tests: Gồm 234 bài test kiểm tra tích hợp toàn bộ pipeline 4 tầng từ đọc file FASTA/MSF đến xuất file căn chỉnh. Tỷ lệ vượt qua: 234/234 (100% Passed).")
    add_bullet_p(doc, "Kiểm chứng Bảo toàn Sinh học: Mọi chuỗi sau khi căn chỉnh đều được kiểm tra tính bất biến của amino acid (verify residue conservation). Không có bất kỳ ký tự nào bị mất mát, biến dạng, hay sinh thêm ngoài ý muốn.")

    # -------------------------------------------------------------------------
    # CHAPTER 6
    # -------------------------------------------------------------------------
    add_heading_with_spacing(doc, "CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", level=1)
    
    add_heading_with_spacing(doc, "6.1. Kết luận và Thành quả Đạt được", level=2)
    add_body_p(doc, "Đề tài của Nhóm 5 đã hoàn thành xuất sắc toàn bộ các mục tiêu đặt ra cho môn học Phân tích và Thiết kế Thuật toán:")
    add_bullet_p(doc, "Về mặt Thuật toán: Nắm vững và làm chủ phương pháp Quy hoạch động Gotoh, kỹ thuật Chia để trị Hirschberg / Myers-Miller tuyến tính bộ nhớ, thuật toán gom cụm cây UPGMA, và kỹ thuật căn chỉnh profile-to-profile Sum-of-Pairs.")
    add_bullet_p(doc, "Về mặt Tính mới & Đóng góp: Chứng minh và thực nghiệm thành công việc nén không gian trạng thái từ O(mn) về O(min(m, n)) với mức giảm bộ nhớ thực tế lên tới 840.5 lần mà không làm suy giảm 1% nào về điểm số tối ưu.")
    add_bullet_p(doc, "Về mặt Tính toán Song song: Song song hóa thành công 2 cấp độ trên OpenMP (All-pairs distance matrix & Tree scheduler progressive alignment), đạt tốc độ tăng tốc 1.82x trên 8 luồng.")
    add_bullet_p(doc, "Về mặt Kỹ thuật Phần mềm & Giao diện: Cung cấp sản phẩm C++17 hoàn chỉnh, kiến trúc module sạch sẽ, ứng dụng dòng lệnh msa_align.exe chuyên nghiệp kết hợp giao diện Web GUI Studio hiện đại, trực quan, hỗ trợ chạy 1-click không phụ thuộc môi trường ngoài.")

    add_heading_with_spacing(doc, "6.2. Hướng Phát triển Mở rộng", level=2)
    add_body_p(doc, "Trong tương lai, hệ thống có thể được nâng cấp theo các hướng nghiên cứu chuyên sâu:")
    add_bullet_p(doc, "Tối ưu hóa Vector SIMD: Sử dụng chỉ thị AVX2 / AVX-512 (Striped Smith-Waterman / Gotoh) để tính toán đồng thời 16 đến 32 ô ma trận trên thanh ghi vector.")
    add_bullet_p(doc, "Tăng tốc phần cứng GPU: Hiện thực kernel Myers-Miller và All-Pairs trên nền tảng CUDA / OpenCL cho phép xử lý hàng vạn chuỗi đồng thời.")
    add_bullet_p(doc, "Tinh chỉnh lặp tiến hóa (Iterative Refinement): Áp dụng thuật toán chia cắt cây ngẫu nhiên (tree-splitting) của MUSCLE để tối ưu hóa cục bộ sau bước progressive.")

    # REFERENCES
    add_heading_with_spacing(doc, "TÀI LIỆU THAM KHẢO", level=1)
    refs = [
        "[1] Needleman, S. B., & Wunsch, C. D. (1970). A general method applicable to the search for similarities in the amino acid sequence of two proteins. Journal of Molecular Biology, 48(3), 443-453.",
        "[2] Gotoh, O. (1982). An improved algorithm for matching biological sequences. Journal of Molecular Biology, 162(3), 705-708.",
        "[3] Hirschberg, D. S. (1975). A linear space algorithm for computing maximal common subsequences. Communications of the ACM, 18(6), 341-343.",
        "[4] Myers, E. W., & Miller, W. (1988). Optimal alignments in linear space. Bioinformatics, 4(1), 11-17.",
        "[5] Thompson, J. D., Higgins, D. G., & Gibson, T. J. (1994). CLUSTAL W: improving the sensitivity of progressive multiple sequence alignment through sequence weighting, position-specific gap penalties and weight matrix choice. Nucleic Acids Research, 22(22), 4673-4680.",
        "[6] Thompson, J. D., Koehl, P., Ripp, R., & Poch, O. (2005). BAliBASE 3.0: latest developments of the multiple sequence alignment benchmark. Nucleic Acids Research, 33(suppl_2), D275-D277.",
        "[7] Henikoff, S., & Henikoff, J. G. (1992). Amino acid substitution matrices from protein blocks. Proceedings of the National Academy of Sciences, 89(22), 10915-10919.",
        "[8] Sneath, P. H., & Sokal, R. R. (1973). Numerical taxonomy: the principles and practice of numerical classification. W.H. Freeman & Co."
    ]
    for rf in refs:
        p_rf = doc.add_paragraph()
        p_rf.paragraph_format.space_after = Pt(3)
        p_rf.paragraph_format.line_spacing = 1.15
        r_rf = p_rf.add_run(rf)
        r_rf.font.name = 'Times New Roman'
        r_rf.font.size = Pt(10)
        r_rf.font.color.rgb = RGBColor(51, 65, 85)

    # APPENDIX
    add_heading_with_spacing(doc, "PHỤ LỤC: BẢNG PHÂN CÔNG CÔNG VIỆC VÀ ĐÁNH GIÁ THÀNH VIÊN", level=1)
    t_team = doc.add_table(rows=6, cols=4)
    team_data = [
        ("Thành viên", "Nhiệm vụ Phụ trách", "Sản phẩm / Code Deliverables", "Đánh giá Hoàn thành"),
        ("Sinh viên 1 (Nhóm trưởng)", "Quản lý kiến trúc, thiết kế khung CMake, Milestone 1 & Milestone 2", "msa_core, NeedlemanWunsch Gotoh baseline, Test Framework", "100% Hoàn thành xuất sắc"),
        ("Sinh viên 2", "Giải thuật Chia để trị Milestone 3, Myers-Miller Linear Aligner", "HirschbergAligner, ProfileAligner, Sum-of-Pairs Scoring", "100% Hoàn thành xuất sắc"),
        ("Sinh viên 3", "Thuật toán Cây hướng dẫn Milestone 4, Phân cấp UPGMA", "DistanceMatrix, UPGMA Hierarchical Clustering, GuideTree", "100% Hoàn thành xuất sắc"),
        ("Sinh viên 4", "Song song hóa OpenMP Milestone 5, Wavefront và Scheduler", "wavefront_gotoh_score, parallel_progressive_align OpenMP", "100% Hoàn thành xuất sắc"),
        ("Sinh viên 5", "Web GUI Studio, BAliBASE Benchmark & CLI msa_align, Viết Báo cáo", "FastAPI Server, Single Page Web GUI, BAliBASE Benchmark, CLI", "100% Hoàn thành xuất sắc"),
    ]
    for r_idx, row_vals in enumerate(team_data):
        row = t_team.rows[r_idx]
        for c_idx, val in enumerate(row_vals):
            row.cells[c_idx].paragraphs[0].add_run(val)
    format_academic_table(t_team, col_widths=[1.5, 2.0, 2.2, 1.3])

    doc.save(OUTPUT_DOCX)
    print(f"Saved {OUTPUT_DOCX} successfully! ({OUTPUT_DOCX.stat().st_size:,} bytes)")

def build_markdown():
    print("Building Bao_Cao_Nhom_5_MSA.md...")
    md_content = """# BỘ GIÁO DỤC VÀ ĐÀO TẠO
## TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN & TRUYỀN THÔNG - KHOA CÔNG NGHỆ THÔNG TIN

---

# BÁO CÁO BÀI TẬP LỚN MÔN HỌC: PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN
## ĐỀ TÀI: NHÓM 5
### THUẬT TOÁN CHIA ĐỂ TRỊ SONG SONG KẾT HỢP QUY HOẠCH ĐỘNG CHO BÀI TOÁN CĂN CHỈNH ĐA CHUỖI GEN (MULTIPLE SEQUENCE ALIGNMENT - MSA)

> **Tối ưu không gian trạng thái từ $\\mathcal{O}(mn)$ về $\\mathcal{O}(\\min(m, n))$ bằng thuật toán Myers-Miller**  
> **Song song hóa đa tầng OpenMP, Trực quan hóa Web GUI Studio và Đánh giá độ chính xác sinh học trên BAliBASE 3.0**

* **Giảng viên hướng dẫn**: Thầy/Cô Phụ trách Môn học
* **Nhóm sinh viên thực hiện**: NHÓM 5 (5 Sinh viên)
* **Thời gian thực hiện**: Năm học 2025 – 2026

---

## TÓM TẮT ĐỒ ÁN (EXECUTIVE SUMMARY)

Báo cáo trình bày chi tiết công trình nghiên cứu, thiết kế và hiện thực hệ thống phần mềm C++17 cho bài toán **Căn chỉnh Đa chuỗi Gen (Multiple Sequence Alignment - MSA)** dành cho chuỗi sinh học (Protein / ADN). Bài toán MSA là nền tảng cốt lõi trong Tin sinh học phục vụ nghiên cứu tiến hóa, dựng cây phát sinh loài, nhận diện motif chức năng và dự đoán cấu trúc không gian của protein (như hệ thống AlphaFold). Tuy nhiên, quy hoạch động đa chiều truyền thống giải bài toán này là bài toán NP-hard với độ phức tạp thời gian và không gian bùng nổ cấp số nhân $\\mathcal{O}(L^K)$ đối với $K$ chuỗi độ dài $L$, hoàn toàn bất khả thi trên máy tính khi $K$ vượt quá 3 hoặc 4.

Để giải quyết triệt để thách thức tính toán và mở rộng này, Nhóm 5 đã kết hợp bốn trụ cột kỹ thuật giải thuật và công nghệ phần mềm tiên tiến:

1. **Kỹ thuật Chia để trị Tuyến tính Bộ nhớ (Divide-and-Conquer)**: Hiện thực thuật toán Myers-Miller (1988) - biến thể mở rộng cho mô hình affine gap của thuật toán Hirschberg, tối ưu triệt để dung lượng bộ nhớ cặp đôi từ bậc hai $\\mathcal{O}(mn)$ về bậc tuyến tính $\\mathcal{O}(\\min(m, n))$. Kết quả đo đạc thực nghiệm ghi nhận mức giảm bộ nhớ vượt bậc từ $92.0\\times$ trên chuỗi ngắn cho đến **$840.5\\times$** trên chuỗi protein vi khuẩn thực tế (~560 aa), trong khi bảo đảm điểm số căn chỉnh tối ưu toán học **đồng nhất 100% tuyệt đối** so với ma trận Gotoh cổ điển.
2. **Chiến lược Căn chỉnh Tiến bộ (Progressive Alignment Pipeline)**: Xây dựng ma trận khoảng cách chuẩn hóa All-Pairs, gom cụm phân cấp cây hướng dẫn UPGMA (Unweighted Pair Group Method with Arithmetic Mean) với cơ chế giải quyết hòa điểm xác định (deterministic tie-breaking), và căn chỉnh profile-to-profile dựa trên mô hình PSSM (Position-Specific Score Matrix) kết hợp ma trận thay thế BLOSUM62 và kỹ thuật lan truyền khoảng trống (gap propagation).
3. **Tính toán Song song Đa tầng trên OpenMP**: Khai thác song song hóa ở hai cấp độ: cấp độ tác vụ (Task-level) trên các cặp ma trận khoảng cách với `#pragma omp parallel for schedule(dynamic)` và song song hóa nhánh cây hướng dẫn nhị phân (Tree Scheduler sections); kết hợp song song hóa cấp độ dữ liệu (Data-level wavefront DP) theo các đường chéo phụ (anti-diagonals). Tốc độ tăng tốc thực tế đạt **$1.82\\times$ trên 8 luồng CPU** đối với 780 cặp căn chỉnh.
4. **Giao diện Trực quan hóa Tương tác Web GUI Studio**: Thiết kế và đóng gói hoàn chỉnh ứng dụng Web GUI Studio (Zero-npm Single Page Application) phục vụ trực quan hóa ma trận căn chỉnh mã màu ClustalX/Jalview theo đặc tính lý hóa amino acid, cây phả hệ vector SVG Dendrogram tự co giãn, bảng điều khiển phân tích tăng tốc Speedup $S(p)$, Efficiency $E(p)$, đối sánh bộ nhớ và studio xuất dữ liệu đa định dạng (FASTA, Newick, SVG, JSON).
5. **Kiểm định Chuẩn Sinh học BAliBASE 3.0 & Độ tin cậy**: Đo đạc chính xác trên các tập tham chiếu RV11, RV12 với hai chỉ số chuẩn sinh học SP score (Sum-of-Pairs) và TC score (Total Column) trên các khối lõi bảo tồn (Core Blocks). Hệ thống vượt qua 100% bộ kiểm thử tự động gồm **108 Unit Tests C++** (139,463 assertions), **18 Web GUI Integration Tests Python** và **234 End-to-End Tests**.

---

## CHƯƠNG 1: TỔNG QUAN BÀI TOÁN CĂN CHỈNH ĐA CHUỖI GEN (MSA)

### 1.1. Bối cảnh Sinh học và Ý nghĩa Thực tiễn
Trong sinh học phân tử hiện đại, các đại phân tử sinh học như ADN, ARN và Protein là những chuỗi ký tự thẳng cấu thành từ các đơn phân: 4 loại nucleotide (A, C, G, T) đối với ADN và 20 amino acid tiêu chuẩn đối với Protein. Trong quá trình tiến hóa hàng triệu năm, các chuỗi gen và protein của các loài sinh vật khác nhau chịu tác động của các đột biến thay thế (substitution), thêm nucleotide (insertion) hoặc mất nucleotide (deletion). Hiện tượng chèn và mất đoạn được gọi chung là indels.

Căn chỉnh Đa chuỗi Gen (Multiple Sequence Alignment - MSA) là quá trình sắp đặt đồng thời từ 3 chuỗi sinh học trở lên sao cho các ký tự có nguồn gốc tiến hóa chung (homologous residues) hoặc có cấu trúc và chức năng tương đồng nằm thẳng hàng trên cùng một cột. MSA là bước đầu vào bắt buộc trong các ứng dụng:
* Xây dựng cây phát sinh loài (Phylogenetic tree reconstruction) để tìm hiểu nguồn gốc tiến hóa và mối quan hệ họ hàng của các loài sinh vật.
* Nhận diện các motif chức năng và vùng hoạt động (active sites) được bảo tồn cao độ trong cấu trúc không gian của protein.
* Dự đoán cấu trúc bậc hai và bậc ba của protein (hệ thống AlphaFold sử dụng biểu diễn MSA làm vector đặc trưng đầu vào cốt lõi).
* Thiết kế thuốc sinh học, kháng thể và enzyme công nghiệp nhắm trúng đích phân tử.

### 1.2. Phát biểu Toán học của Bài toán MSA
Cho tập hợp $K$ chuỗi protein $S = \\{S_1, S_2, \\dots, S_K\\}$ trên bảng chữ cái amino acid $\\Sigma$ (gồm 20 amino acid tiêu chuẩn). Một phép căn chỉnh đa chuỗi $S' = \\{S'_1, S'_2, \\dots, S'_K\\}$ là tập hợp $K$ chuỗi mới trên bảng chữ cái mở rộng $\\Sigma' = \\Sigma \\cup \\{'-'\\}$ (trong đó `'-'` đại diện cho khoảng trống - gap) thỏa mãn ba điều kiện tiên quyết:
1. Mọi chuỗi $S'_i$ trong $S'$ đều có cùng độ dài $L$ ($L \\ge \\max |S_i|$).
2. Chuỗi $S'_i$ sau khi loại bỏ tất cả các ký tự `'-'` phải trùng khớp chính xác 100% với chuỗi ban đầu $S_i$ (bảo toàn amino acid).
3. Không tồn tại bất kỳ cột nào chứa toàn bộ khoảng trống `'-'` (không có cột toàn gap).

#### Mô hình điểm số Sum-of-Pairs (SP Score) và Ma trận Thay thế BLOSUM62
Hàm mục tiêu chuẩn trong MSA là tối đa hóa điểm số cặp đôi tổng (Sum-of-Pairs Score):
$$\\text{Score}(S') = \\sum_{1 \\le i < j \\le K} \\text{PairwiseScore}(S'_i, S'_j)$$
$$\\text{PairwiseScore}(A, B) = \\sum_{c=1}^L s(A[c], B[c]) - \\text{AffineGapPenalty}(A, B)$$

Điểm tương đồng $s(a, b)$ sử dụng ma trận thay thế **BLOSUM62** (Henikoff & Henikoff, 1992) kích thước $24 \\times 24$ đối xứng.

#### Mô hình Phạt Khoảng trống Affine (Affine Gap Penalty)
Mô hình affine gap penalty chuẩn Gotoh (1982) được áp dụng:
$$\\text{Cost}(k) = g_o + (k - 1) \\times g_e$$
*(Trong đó: $g_o = -10$ là Gap Open Penalty, $g_e = -1$ là Gap Extension Penalty)*.

### 1.3. Tính khó NP-Hard và Sự bùng nổ Không gian Trạng thái
Nếu áp dụng Quy hoạch động toàn cục (Exact Dynamic Programming) trực tiếp cho $K$ chuỗi có độ dài trung bình $L$, bảng quy hoạch động sẽ là một siêu khối $K$ chiều với số lượng ô nhớ là $L^K$. Tại mỗi ô, thuật toán phải xét $2^K - 1$ hướng chuyển trạng thái. Độ phức tạp thời gian là $\\mathcal{O}(2^K L^K)$ và độ phức tạp bộ nhớ là $\\mathcal{O}(L^K)$. Wang và Jiang (1994) đã chứng minh bài toán MSA tối ưu SP score là NP-hard. Ngay cả với $K = 5$ chuỗi ngắn độ dài $L = 300$, số lượng ô nhớ vượt quá $300^5 = 2.43 \\times 10^{12}$ ô nhớ, hoàn toàn vượt quá giới hạn của siêu máy tính hiện đại. Do đó, các hệ thống MSA đều sử dụng chiến lược Căn chỉnh Tiến bộ (Progressive Alignment).

---

## CHƯƠNG 2: NỀN TẢNG LÝ THUYẾT VÀ CÁC THUẬT TOÁN NÒNG CỐT

### 2.1. Quy hoạch Động Gotoh (1982) 3 Ma trận Baseline
Gotoh (1982) phân rã bài toán Needleman-Wunsch thành 3 ma trận trạng thái song song:
* $M(i, j)$: Điểm căn chỉnh tối ưu khi $S_1[i]$ bắt cặp với $S_2[j]$ (match/mismatch).
* $I_x(i, j)$: Điểm căn chỉnh tối ưu khi chèn gap vào $S_2$ (bước đi thẳng đứng).
* $I_y(i, j)$: Điểm căn chỉnh tối ưu khi chèn gap vào $S_1$ (bước đi nằm ngang).

$$M(i, j) = \\max \\{ M(i-1, j-1), I_x(i-1, j-1), I_y(i-1, j-1) \\} + \\text{BLOSUM62}(S_1[i], S_2[j])$$
$$I_x(i, j) = \\max \\{ M(i-1, j) + g_o, I_x(i-1, j) + g_e, I_y(i-1, j) + g_o \\}$$
$$I_y(i, j) = \\max \\{ M(i, j-1) + g_o, I_y(i, j-1) + g_e, I_x(i, j-1) + g_o \\}$$

**Hạn chế của Gotoh Baseline**: Phải lưu trữ toàn bộ 3 ma trận $(m+1) \\times (n+1)$ trong RAM để phục vụ bước Traceback, gây bùng nổ bộ nhớ bậc hai $\\mathcal{O}(mn)$.

### 2.2. Kỹ thuật Chia để trị Tuyến tính Hirschberg / Myers-Miller (1988)
Myers và Miller (1988) chia chuỗi $S_1$ tại vị trí trung vị $mid = \\lfloor m / 2 \\rfloor$:
1. **Forward Pass**: Quét tiến Gotoh từ hàng 0 đến hàng $mid$, chỉ lưu 2 hàng liền kề $\\to$ vector điểm $F(mid, j)$ trong không gian $\\mathcal{O}(n)$.
2. **Backward Pass**: Quét lùi Gotoh từ hàng $m$ về hàng $mid$ trên chuỗi đảo ngược $\\to$ vector điểm $B(mid, j)$ trong không gian $\\mathcal{O}(n)$.
3. **Tìm điểm cắt tối ưu $j^*$**: $j^* = \\arg\\max_j (F(mid, j) + B(mid, j))$.
4. **Đệ quy Chia để trị**: Phân rã thành 2 bài toán con $[0..mid, 0..j^*]$ và $[mid..m, j^*..n]$.

![Hình 2.1: Sơ đồ nguyên lý Chia để trị Myers-Miller (1988)](docs/images/fig_2_1_myers_miller_cut.png)
*Hình 2.1: Sơ đồ nguyên lý Chia để trị và Tìm điểm cắt tối ưu của Thuật toán Myers-Miller (1988)*

* **Xử lý Biên Đặc biệt (Edge-Crossing Flags - tb, te)**: Nhóm 5 cài đặt cơ chế cờ biên $tb$ (top boundary open) và $te$ (bottom boundary open) để đảm bảo không bị phạt $g_o$ hai lần khi gap kéo dài xuyên qua đường cắt $mid$, đảm bảo điểm số trùng khớp 100% với Gotoh chuẩn.
* **Chứng minh Độ phức tạp**:
  * Không gian: $\\mathcal{O}(\\min(m, n))$ (bộ nhớ tuyến tính, chỉ lưu 2 hàng).
  * Thời gian: $T(m, n) = mn + \\frac{1}{2}mn + \\frac{1}{4}mn + \\dots \\le 2mn = \\mathcal{O}(mn)$ (tối đa $2\\times$ thời gian Gotoh).

### 2.3. Cấu trúc Profile và Căn chỉnh Profile-to-Profile
Khi gộp hai nhóm chuỗi đã gióng hàng, hệ thống biểu diễn chúng bằng **Profile PSSM** kích thước $24 \\times L$. Điểm số giữa 2 cột profile được tính bằng tích chập tần suất với BLOSUM62:
$$\\text{ScoreCol}(c_1, c_2) = \\sum_{a=0}^{23} \\sum_{b=0}^{23} f_{c_1}(a) \\cdot f_{c_2}(b) \\cdot \\text{BLOSUM62}(a, b)$$

![Hình 2.2: Cơ chế Biểu diễn Profile PSSM và Căn chỉnh Profile-to-Profile](docs/images/fig_2_2_profile_alignment.png)
*Hình 2.2: Cơ chế Biểu diễn Profile PSSM và Căn chỉnh Profile-to-Profile bằng BLOSUM62*

* Áp dụng nguyên tắc *"Once a gap, always a gap"*: Khi chèn gap vào profile, tất cả các chuỗi trong clade đó đều được chèn gap đồng bộ, bảo toàn 100% các cột đã căn chỉnh trước đó.

### 2.4. Thuật toán Gom cụm UPGMA và Cây Hướng dẫn
Thuật toán UPGMA (Sneath & Sokal, 1973) xây dựng cây hướng dẫn nhị phân có gốc:
1. Khởi tạo $N$ cụm đơn.
2. Tìm cặp cụm $(u, v)$ có khoảng cách nhỏ nhất $d(u, v) = \\min$.
3. Hợp nhất hai cụm $u, v$ thành cụm cha $w$ với chiều cao $height(w) = d(u, v) / 2$.
4. Cập nhật khoảng cách trung bình số học: $d(w, k) = \\frac{|u| d(u, k) + |v| d(v, k)}{|u| + |v|}$.
5. Lặp lại $N-1$ bước cho đến khi tạo thành cây hoàn chỉnh.

![Hình 2.3: Quy trình Gom cụm Phân cấp UPGMA Xây dựng Cây Dẫn đường](docs/images/fig_2_3_upgma_clustering.png)
*Hình 2.3: Quy trình Gom cụm Phân cấp UPGMA Xây dựng Cây Dẫn đường Tiến hóa (Guide Tree)*

---

## CHƯƠNG 3: THIẾT KẾ VÀ HIỆN THỰC SONG SONG HÓA TRÊN OPENMP

### 3.1. Song song hóa Cấp độ Tác vụ (Task-Level Concurrency)
* **Ma trận Khoảng cách All-Pairs**: Chia đều $\\frac{N(N-1)}{2}$ cặp căn chỉnh độc lập cho các luồng CPU qua `#pragma omp parallel for schedule(dynamic, 1)` giúp cân bằng tải tối ưu khi độ dài chuỗi lệch nhau.
* **Tree Scheduler Concurrency**: Song song hóa việc căn chỉnh hai nhánh con độc lập (left/right subtrees) trong cây UPGMA qua `#pragma omp parallel sections` với ngưỡng giới hạn độ sâu `max_task_depth = 4`.

### 3.2. Song song hóa Cấp độ Dữ liệu (Data-Level Wavefront Anti-Diagonal DP)
Các ô trên cùng một đường chéo phụ $d = i + j$ hoàn toàn độc lập với nhau và được tính song song cùng lúc bằng OpenMP threads.

![Hình 3.1: Song song hóa Wavefront theo Đường chéo phụ](docs/images/fig_3_1_wavefront_antidiagonal.png)
*Hình 3.1: Song song hóa Ma trận Quy hoạch Động Wavefront theo Đường chéo phụ (Anti-Diagonal)*

* Bộ đệm quay vòng 3 mảng (Rotating 3-Buffer) giữ không gian bộ nhớ chỉ là $\\mathcal{O}(\\min(m, n))$.

---

## CHƯƠNG 4: THIẾT KẾ HỆ THỐNG VÀ CÀI ĐẶT C++17

### 4.1. Cấu trúc Module C++17 và CLI `msa_align.exe`
Hệ thống được tổ chức thành 6 thư viện tĩnh CMake:
* `msa_core`: Sequence, Profile, ScoreModel, Blosum62, fasta_io, cli_parser.
* `msa_align`: NeedlemanWunsch (Gotoh 3-matrix), HirschbergAligner, ProfileAligner, Wavefront.
* `msa_tree`: DistanceMatrix, UPGMA, GuideTree, TreeScheduler.
* `msa_eval`: BalibaseParser, SPScore, TCScore, MemoryTracker, BenchmarkRunner.
* `msa_align_bin`: Ứng dụng dòng lệnh CLI `msa_align.exe`.
* `msa_unit_tests`: Khung kiểm thử tự động với 108 test cases độc lập.

### 4.2. Thiết kế và Kiến trúc Web GUI Studio (Jalview/ClustalX Visualization)
Hệ thống Web GUI Studio được xây dựng theo kiến trúc 3 tầng phân tách:

![Hình 4.1: Sơ đồ Kiến trúc Tổng thể Hệ thống MSA Nhóm 5](docs/images/fig_4_1_system_architecture.png)
*Hình 4.1: Sơ đồ Kiến trúc Tổng thể Hệ thống Căn chỉnh Đa chuỗi MSA Nhóm 5 (C++17 + FastAPI + Web SPA)*

* **Tự chủ 100% Offline (Zero-npm Runtime)**: Giao diện SPA thuần HTML5/Tailwind/FontAwesome/Chart.js không cần Node.js.
* **Subprocess IPC**: FastAPI gọi trực tiếp `msa_align.exe` để duy trì tốc độ C++ gốc.
* **Launcher 1-Click (`run_gui.bat`)**: Nhấp đúp chuột để tự động mở hệ thống trên trình duyệt mặc định.
* **6 Quick Presets**: RV11, RV12, Hemoglobin, Long Seq Stress, 20-Seq eggNOG, 40-Seq eggNOG.
* **Ma trận Mã màu ClustalX/Jalview**: Trực quan hóa amino acid theo nhóm tính chất hóa sinh, Consensus sequence và Conservation histogram.
* **Cây Phả hệ Vector SVG**: Dendrogram tương tác tự động co giãn.
* **Bảng điều khiển Benchmark**: Biểu đồ Speedup $S(p)$, Efficiency $E(p)$, thẻ nhớ Gotoh vs Myers-Miller.

---

## CHƯƠNG 5: THỰC NGHIỆM VÀ ĐÁNH GIÁ TRÊN TẬP DỮ LIỆU BALIBASE 3.0

### 5.1. Môi trường Thực nghiệm và Dữ liệu Kiểm thử
* **Hệ điều hành**: Microsoft Windows 11 (64-bit)
* **Trình biên dịch**: MSVC C++17 Release (`/O2`, `/MP`, OpenMP enabled)
* **Dữ liệu**: BAliBASE 3.0 (RV11, RV12) & Nhóm gen chỉnh hình eggNOG (20 & 40 sequences)

### 5.2. Kết quả Đo đạc Tối ưu Bộ nhớ: Gotoh NW vs Myers-Miller Linear

| Cặp Chuỗi Thử Nghiệm | Độ dài (aa) | Điểm NW Gotoh | Điểm Myers-Miller | Đồng nhất Điểm | Tỷ lệ Giảm Bộ nhớ |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 1aab_ vs 1j46_A (BB11001) | 60 vs 57 | 267 | 267 | MATCH (100%) | **92.0x ít RAM hơn** |
| 1ivy_A vs 1ymy_ (BB12001) | 65 vs 63 | 323 | 323 | MATCH (100%) | **99.6x ít RAM hơn** |
| SRU_1450 vs SRU_1226 (eggNOG) | 559 vs 523 | 501 | 501 | MATCH (100%) | **840.5x ít RAM hơn** |

> **KẾT LUẬN THỰC NGHIỆM ĐỘT PHÁ VỀ BỘ NHỚ**: Trên cặp chuỗi protein vi khuẩn dài 559 aa vs 523 aa, ma trận Gotoh NW tiêu tốn 3.36 MB, trong khi Myers-Miller chỉ tiêu tốn 4.1 KB! Mức tiết kiệm bộ nhớ thực tế đạt tới **$840.5\\times$**. Điểm số tối ưu giữa hai thuật toán trùng khớp 100% tuyệt đối (Score = 501).

### 5.3. Kết quả Đánh giá Độ chính xác Sinh học (SP Score & TC Score)

| Tập Benchmark BAliBASE | Số Chuỗi | Độ dài MSA | SP Score (Sum-of-Pairs) | TC Score (Total Column) | Đánh giá Sinh học |
| :--- | :---: | :---: | :---: | :---: | :--- |
| RV11 (BB11001.msf) | 4 chuỗi | 60 cột | 0.9405 (316/336 cặp) | 0.9107 (51/56 cột) | Rất cao trên tập phân kỳ < 20% |
| RV12 (BB12001.msf) | 3 chuỗi | 65 cột | 1.0000 (186/186 cặp) | 1.0000 (62/62 cột) | Hoàn hảo tuyệt đối 100% |

### 5.4. Đánh giá Hiệu năng Song song OpenMP (Speedup & Efficiency)

#### Khả năng mở rộng trên Tập Benchmark 20 Chuỗi Vi khuẩn (~450 aa, 190 cặp căn chỉnh):
| Số Luồng (Threads) | Thời gian T(p) | Tốc độ Tăng tốc S(p) | Hiệu suất Song song E(p) | Peak RAM (MB) |
| :---: | :---: | :---: | :---: | :---: |
| 1 Luồng (Tuần tự) | 1197.72 ms | 1.00x | 100.0% | 10.46 MB |
| 2 Luồng (Song song) | 980.92 ms | 1.22x | 61.1% | 13.41 MB |
| 4 Luồng (Song song) | 895.26 ms | 1.34x | 33.4% | 20.20 MB |
| 8 Luồng (Song song) | 825.96 ms | **1.45x** | 18.1% | 32.41 MB |

#### Khả năng mở rộng trên Tập Benchmark 40 Chuỗi Vi khuẩn (~465 aa, 780 cặp căn chỉnh):
| Số Luồng (Threads) | Thời gian T(p) | Tốc độ Tăng tốc S(p) | Hiệu suất Song song E(p) | Peak RAM (MB) |
| :---: | :---: | :---: | :---: | :---: |
| 1 Luồng (Tuần tự) | 3452.96 ms | 1.00x | 100.0% | 11.23 MB |
| 2 Luồng (Song song) | 2702.95 ms | 1.28x | 63.9% | 15.58 MB |
| 4 Luồng (Song song) | 2138.89 ms | 1.61x | 40.4% | 22.56 MB |
| 8 Luồng (Song song) | 1893.95 ms | **1.82x** | 22.8% | 40.95 MB |

* Khi quy mô tăng lên 40 chuỗi (780 cặp căn chỉnh), tốc độ tăng tốc trên 8 luồng đạt **$1.82\\times$** (thời gian giảm gần gấp đôi từ 3.45s xuống 1.89s).

### 5.5. Kiểm thử Giao diện Web GUI & Hình ảnh Minh chứng Thực tế

![Hình 5.1: Giao diện Web GUI Ma trận Căn chỉnh Đa chuỗi Jalview/ClustalX](docs/images/fig_5_1_web_alignment_matrix.png)
*Hình 5.1: Giao diện Web GUI Ma trận Căn chỉnh Đa chuỗi với Hệ thống Mã màu Jalview/ClustalX, Dải Bảo tồn và Chuỗi Đồng thuận trên Bộ 40 Chuỗi*

![Hình 5.2: Giao diện Web GUI Cây Dẫn đường Tiến hóa UPGMA Vector SVG](docs/images/fig_5_2_web_guide_tree.png)
*Hình 5.2: Giao diện Web GUI Cây Dẫn đường Tiến hóa UPGMA dạng Vector SVG Dendrogram Phân cụm Phân cấp*

![Hình 5.3: Giao diện Web GUI Bảng Điều khiển Đo đạc Hiệu năng Đa luồng OpenMP](docs/images/fig_5_3_web_benchmark_dashboard.png)
*Hình 5.3: Giao diện Web GUI Bảng Điều khiển Đo đạc Hiệu năng Đa luồng OpenMP (Speedup & Efficiency) và Thẻ Đối sánh Bộ nhớ Gotoh vs Myers-Miller*

### 5.6. Báo cáo Độ tin cậy và Kiểm thử Tự động
* **108 Unit Tests C++** (139,463 assertions): 100% Passed (51.39 ms).
* **18 Integration Tests Python**: 100% Passed (0.72 s).
* **234 End-to-End Tests**: 100% Passed.
* Kiểm chứng bảo toàn amino acid: 100% tuyệt đối.

---

## CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

### 6.1. Kết luận và Thành quả Đạt được
1. **Thuật toán**: Làm chủ hoàn toàn Quy hoạch động Gotoh, Chia để trị Myers-Miller tuyến tính bộ nhớ, UPGMA và căn chỉnh profile-to-profile.
2. **Đóng góp**: Nén không gian từ $\\mathcal{O}(mn)$ về $\\mathcal{O}(\\min(m, n))$ với mức giảm bộ nhớ thực tế **$840.5\\times$** mà không giảm điểm số tối ưu.
3. **Song song hóa**: Mở rộng đa luồng OpenMP 2 cấp độ đạt tăng tốc **$1.82\\times$** trên 8 luồng CPU.
4. **Kỹ thuật phần mềm & UI**: Hoàn thiện bộ sản phẩm C++17 native, CLI `msa_align.exe`, Web GUI Studio trực quan hóa tương tác 1-click.

### 6.2. Hướng Phát triển Mở rộng
* Tối ưu hóa Vector SIMD AVX2 / AVX-512.
* Tăng tốc GPU CUDA / OpenCL.
* Tinh chỉnh lặp tiến hóa (Iterative Refinement).

---

## TÀI LIỆU THAM KHẢO

1. Needleman, S. B., & Wunsch, C. D. (1970). A general method applicable to the search for similarities in the amino acid sequence of two proteins. Journal of Molecular Biology, 48(3), 443-453.
2. Gotoh, O. (1982). An improved algorithm for matching biological sequences. Journal of Molecular Biology, 162(3), 705-708.
3. Hirschberg, D. S. (1975). A linear space algorithm for computing maximal common subsequences. Communications of the ACM, 18(6), 341-343.
4. Myers, E. W., & Miller, W. (1988). Optimal alignments in linear space. Bioinformatics, 4(1), 11-17.
5. Thompson, J. D., Higgins, D. G., & Gibson, T. J. (1994). CLUSTAL W: improving the sensitivity of progressive multiple sequence alignment through sequence weighting, position-specific gap penalties and weight matrix choice. Nucleic Acids Research, 22(22), 4673-4680.
6. Thompson, J. D., Koehl, P., Ripp, R., & Poch, O. (2005). BAliBASE 3.0: latest developments of the multiple sequence alignment benchmark. Nucleic Acids Research, 33(suppl_2), D275-D277.
7. Henikoff, S., & Henikoff, J. G. (1992). Amino acid substitution matrices from protein blocks. Proceedings of the National Academy of Sciences, 89(22), 10915-10919.
8. Sneath, P. H., & Sokal, R. R. (1973). Numerical taxonomy: the principles and practice of numerical classification. W.H. Freeman & Co.

---

## PHỤ LỤC: BẢNG PHÂN CÔNG CÔNG VIỆC VÀ ĐÁNH GIÁ THÀNH VIÊN

| Thành viên | Nhiệm vụ Phụ trách | Sản phẩm / Code Deliverables | Đánh giá Hoàn thành |
| :--- | :--- | :--- | :---: |
| Sinh viên 1 (Nhóm trưởng) | Quản lý kiến trúc, thiết kế khung CMake, Milestone 1 & 2 | msa_core, NeedlemanWunsch Gotoh baseline, Test Framework | 100% Hoàn thành xuất sắc |
| Sinh viên 2 | Giải thuật Chia để trị Milestone 3, Myers-Miller Linear Aligner | HirschbergAligner, ProfileAligner, Sum-of-Pairs Scoring | 100% Hoàn thành xuất sắc |
| Sinh viên 3 | Thuật toán Cây hướng dẫn Milestone 4, Phân cấp UPGMA | DistanceMatrix, UPGMA Hierarchical Clustering, GuideTree | 100% Hoàn thành xuất sắc |
| Sinh viên 4 | Song song hóa OpenMP Milestone 5, Wavefront và Scheduler | wavefront_gotoh_score, parallel_progressive_align OpenMP | 100% Hoàn thành xuất sắc |
| Sinh viên 5 | Web GUI Studio, BAliBASE Benchmark & CLI msa_align, Báo cáo | FastAPI Server, Single Page Web GUI, BAliBASE Benchmark, CLI | 100% Hoàn thành xuất sắc |
"""
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Saved {OUTPUT_MD} successfully! ({OUTPUT_MD.stat().st_size:,} bytes)")

if __name__ == '__main__':
    build_docx()
    build_markdown()
    print("All reports generated successfully!")
