#!/usr/bin/env python3
"""
Scientific Conference Poster Generator for Group 5 MSA Project
Generates: Poster_Bao_Cao_Nhom_5_MSA.pptx
Format: Standard Large Scientific Poster (A0 Widescreen 48" x 36" = 121.9cm x 91.4cm)
Modern 3-Column Conference Layout, Navy/Teal/Slate Palette, High-res Embedded Visuals.
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

ROOT_DIR = Path(__file__).resolve().parent.parent
FIGURES_DIR = ROOT_DIR / "results" / "figures"
OUTPUT_POSTER = ROOT_DIR / "Poster_Bao_Cao_Nhom_5_MSA.pptx"

# Color Palette
C_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A
C_NAVY = RGBColor(16, 44, 87)           # #102C57
C_BLUE = RGBColor(37, 99, 235)          # #2563EB
C_TEAL = RGBColor(13, 148, 136)         # #0D9488
C_SLATE = RGBColor(71, 85, 105)         # #475569
C_BG = RGBColor(241, 245, 249)          # #F1F5F9
C_WHITE = RGBColor(255, 255, 255)       # #FFFFFF
C_GOLD = RGBColor(217, 119, 6)          # #D97706
C_BORDER = RGBColor(203, 213, 225)      # #CBD5E1

def create_poster():
    prs = Presentation()
    # Standard 48 x 36 inches A0 landscape
    prs.slide_width = Inches(48.0)
    prs.slide_height = Inches(36.0)
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)

    # Background canvas
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(48.0), Inches(36.0))
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG
    bg.line.fill.background()

    # =========================================================================
    # HEADER BANNER
    # =========================================================================
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(46.4), Inches(4.5))
    header.fill.solid()
    header.fill.fore_color.rgb = C_NAVY_DARK
    header.line.color.rgb = C_TEAL
    header.line.width = Pt(3.0)

    tb_h = slide.shapes.add_textbox(Inches(1.2), Inches(1.0), Inches(45.6), Inches(4.1))
    tf_h = tb_h.text_frame
    tf_h.word_wrap = True

    p_sub = tf_h.paragraphs[0]
    p_sub.text = "HỌC PHẦN: PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN • BÁO CÁO CÔNG TRÌNH NGHIÊN CỨU KHOA HỌC"
    p_sub.font.size = Pt(20)
    p_sub.font.bold = True
    p_sub.font.color.rgb = C_TEAL

    p_title = tf_h.add_paragraph()
    p_title.space_before = Pt(8)
    p_title.text = "THUẬT TOÁN CHIA ĐỂ TRỊ SONG SONG KẾT HỢP QUY HOẠCH ĐỘNG CHO BÀI TOÁN CĂN CHỈNH ĐA CHUỖI GEN (MSA)"
    p_title.font.size = Pt(38)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE

    p_meta = tf_h.add_paragraph()
    p_meta.space_before = Pt(12)
    p_meta.text = "NHÓM THỰC HIỆN: NHÓM 5 (5 Sinh viên)  |  KHOA CÔNG NGHỆ THÔNG TIN  |  KIỂM NGHIỆM TRÊN TẬP BENCHMARK CHUẨN QUỐC TẾ: BAliBASE 3.0"
    p_meta.font.size = Pt(20)
    p_meta.font.color.rgb = RGBColor(226, 232, 240)

    # 3 Column layout
    col_w = Inches(14.8)
    col_gap = Inches(1.0)
    col_top = Inches(5.8)
    col_h = Inches(29.2)

    col1_x = Inches(0.8)
    col2_x = col1_x + col_w + col_gap
    col3_x = col2_x + col_w + col_gap

    def add_section_box(left, top, width, height, title, title_color=C_NAVY):
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        box.fill.solid()
        box.fill.fore_color.rgb = C_WHITE
        box.line.color.rgb = C_BORDER
        box.line.width = Pt(1.5)

        # Header bar inside box
        hbar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + Inches(0.2), top + Inches(0.2), width - Inches(0.4), Inches(0.9))
        hbar.fill.solid()
        hbar.fill.fore_color.rgb = title_color
        hbar.line.fill.background()

        tb = slide.shapes.add_textbox(left + Inches(0.4), top + Inches(0.25), width - Inches(0.8), Inches(0.8))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = title.upper()
        p.font.size = Pt(20)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        return box

    # =========================================================================
    # COLUMN 1: Problem & Hirschberg Theory
    # =========================================================================
    # Box 1.1: Problem Statement
    add_section_box(col1_x, col_top, col_w, Inches(13.8), "1. Đặt Vấn Đề & Cơ Sở Lý Thuyết", C_NAVY)
    tb1 = slide.shapes.add_textbox(col1_x + Inches(0.4), col_top + Inches(1.3), col_w - Inches(0.8), Inches(12.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    pts1 = [
        ("Thách Thức Căn Chỉnh Đa Chuỗi Gen (MSA):", "Bài toán cốt lõi trong sinh tin học nhằm tìm kiếm cấu trúc bảo tồn, đột biến di truyền và dựng cây phát sinh loài."),
        ("Bùng Nổ Trạng Thái Quy Hoạch Động (DP):", "DP k-chiều truyền thống đòi hỏi O(N^k) thời gian và O(N^k) bộ nhớ. Với k = 10 chuỗi dài 500 ký tự, không gian trạng thái vượt quá 10^26 bytes — hoàn toàn bất khả thi."),
        ("Mô Hình Điểm Số Gotoh Affine Gap:", "Hàm phạt mở gap g_o = -10, kéo dài g_e = -1 kết hợp ma trận thay thế BLOSUM62. Phân rã 3 ma trận DP M, I_x, I_y để phản ánh đúng hiện tượng sinh học đột biến chèn/xóa chuỗi (Indel)."),
        ("Phương Pháp Căn Chỉnh Lũy Tiến:", "Dựa trên cây hướng dẫn UPGMA để gom cụm các chuỗi tương đồng từ lá lên gốc, chuyển bài toán k-chuỗi về chuỗi các bước căn chỉnh cặp Profile-Profile."),
        ("Rào Cản Bộ Nhớ O(N²) Cặp:", "Needleman-Wunsch vẫn tiêu tốn O(N²) bảng truy vết ngược. Khi chuỗi dài N ≥ 1,000 aa, bộ nhớ RAM bùng nổ khi chạy song song đa luồng.")
    ]
    for b_t, t_t in pts1:
        p = tf1.add_paragraph()
        p.space_before = Pt(14)
        rb = p.add_run()
        rb.text = "• " + b_t + " "
        rb.font.bold = True
        rb.font.size = Pt(17)
        rb.font.color.rgb = C_NAVY_DARK
        rt = p.add_run()
        rt.text = t_t
        rt.font.size = Pt(16.5)
        rt.font.color.rgb = C_SLATE

    # Box 1.2: Hirschberg Divide-and-Conquer
    add_section_box(col1_x, col_top + Inches(14.3), col_w, Inches(14.9), "2. Kỹ Thuật Chia Để Trị Hirschberg O(N)", C_TEAL)
    tb2 = slide.shapes.add_textbox(col1_x + Inches(0.4), col_top + Inches(15.6), col_w - Inches(0.8), Inches(13.2))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    pts2 = [
        ("Nguyên Lý Chia Đôi (Divide):", "Chia chuỗi X tại trung vị mid = |X|/2 thành hai nửa X_left và X_right."),
        ("Quy Hoạch Động Hai Hướng:", "Tính toán đồng thời vector DP xuôi Forward(mid, j) và vector DP ngược Backward(mid, j) đối sánh với chuỗi Y."),
        ("Điểm Cắt Tối Ưu (Optimal Split):", "Tìm j* = argmax [Forward(mid, j) + Backward(mid, j)]. Đảm bảo đường đi tối ưu toàn cục đi qua điểm cắt (mid, j*)."),
        ("Tích Hợp Myers-Miller Affine Gap:", "Quản lý 6 vector trạng thái (fM, fIx, fIy, rM, rIx, rIy) kích thước O(N) thay vì toàn bộ ma trận 2D."),
        ("Chứng Minh Toán Học O(k·N) Bộ Nhớ:", "Không gian lưu trữ profile và vector chỉ phụ thuộc c1·k·N + c2·N = O(k·N). Triệt tiêu 100% nguy cơ Out-Of-Memory!"),
        ("Chứng Minh Toán Học O(M·N) Thời Gian:", "Tổng số phép tính: M·N · Σ (1/2)^d = 2·M·N. Thời gian chỉ gấp đúng 2 lần Needleman-Wunsch nhưng tiết kiệm hàng nghìn lần RAM.")
    ]
    for b_t, t_t in pts2:
        p = tf2.add_paragraph()
        p.space_before = Pt(12)
        rb = p.add_run()
        rb.text = "✔ " + b_t + " "
        rb.font.bold = True
        rb.font.size = Pt(17)
        rb.font.color.rgb = C_NAVY_DARK
        rt = p.add_run()
        rt.text = t_t
        rt.font.size = Pt(16.5)
        rt.font.color.rgb = C_SLATE

    # =========================================================================
    # COLUMN 2: Parallel Framework Architecture
    # =========================================================================
    add_section_box(col2_x, col_top, col_w, col_h, "3. Khung Tính Toán Song Song Đa Cấp (OpenMP + MPI)", C_BLUE)
    
    # Insert Figure 5 Architecture
    fig5_path = FIGURES_DIR / "fig5_parallel_architecture.png"
    if fig5_path.exists():
        slide.shapes.add_picture(str(fig5_path), col2_x + Inches(0.4), col_top + Inches(1.3), col_w - Inches(0.8), Inches(10.5))

    tb3 = slide.shapes.add_textbox(col2_x + Inches(0.4), col_top + Inches(12.0), col_w - Inches(0.8), Inches(16.5))
    tf3 = tb3.text_frame
    tf3.word_wrap = True

    pts3 = [
        ("CẤP ĐỘ 1: PHÂN TÁN MPI TRÊN CỤM MÁY TÍNH (CLUSTER NODES)", ""),
        ("Phân bổ Block-Cyclic:", "Với P ranks MPI, tổng số P_total = k·(k-1)/2 cặp chuỗi được phân rã theo công thức: pair_idx % P == rank. Cân bằng tải hoàn hảo trên các cụm tính toán dị thể."),
        ("Gom Cụm MPI_Allreduce:", "Sau tính toán cục bộ, gọi MPI_Allreduce(MPI_MAX) để tổng hợp ma trận khoảng cách toàn cục mà không tạo điểm nghẽn (Zero Bottleneck)."),
        ("CẤP ĐỘ 2: ĐA LUỒNG OPENMP NỘI BỘ CPU ĐA LÕI (MULTI-CORE)", ""),
        ("All-Pairs Dynamic Scheduling:", "Phẳng hóa vòng lặp 2D thành 1D với `#pragma omp parallel for schedule(dynamic, 4)`. Giải quyết triệt để mất cân bằng tải khi độ dài chuỗi sinh học biến thiên."),
        ("Wavefront Tree Scheduler:", "Phân tầng cây UPGMA từ lá lên gốc thành các Wavefront batches độc lập. Các nút trong cùng tầng được căn chỉnh song song đồng thời."),
        ("Phân Tích Lý Thuyết Amdahl & Gustafson:", "Tỷ lệ song song hóa đạt f ≈ 85% - 90%. Khi số chuỗi k mở rộng, hiệu năng tăng tốc tiệm cận tuyến tính theo định luật Gustafson: S_s(P) ≈ P.")
    ]
    for b_t, t_t in pts3:
        p = tf3.add_paragraph()
        if not t_t:
            p.space_before = Pt(16)
            rb = p.add_run()
            rb.text = b_t
            rb.font.bold = True
            rb.font.size = Pt(17.5)
            rb.font.color.rgb = C_BLUE
        else:
            p.space_before = Pt(8)
            rb = p.add_run()
            rb.text = "• " + b_t + " "
            rb.font.bold = True
            rb.font.size = Pt(16.5)
            rb.font.color.rgb = C_NAVY_DARK
            rt = p.add_run()
            rt.text = t_t
            rt.font.size = Pt(16)
            rt.font.color.rgb = C_SLATE

    # =========================================================================
    # COLUMN 3: Real Experiments & Deliverables
    # =========================================================================
    add_section_box(col3_x, col_top, col_w, col_h, "4. Kết Quả Thực Nghiệm Trên BAliBASE 3.0 Thật", C_GOLD)

    # Insert Figure 1 (Memory) and Figure 2 (Speedup) side by side or stacked
    fig1_path = FIGURES_DIR / "fig1_memory_scaling.png"
    fig2_path = FIGURES_DIR / "fig2_speedup_scaling.png"
    fig4_path = FIGURES_DIR / "fig4_tools_comparison.png"

    img_w = Inches(6.8)
    img_h = Inches(4.3)
    if fig1_path.exists():
        slide.shapes.add_picture(str(fig1_path), col3_x + Inches(0.4), col_top + Inches(1.3), img_w, img_h)
    if fig2_path.exists():
        slide.shapes.add_picture(str(fig2_path), col3_x + Inches(7.6), col_top + Inches(1.3), img_w, img_h)

    # Insert Fig 4 Comparison
    if fig4_path.exists():
        slide.shapes.add_picture(str(fig4_path), col3_x + Inches(0.4), col_top + Inches(5.9), col_w - Inches(0.8), Inches(6.0))

    tb4 = slide.shapes.add_textbox(col3_x + Inches(0.4), col_top + Inches(12.2), col_w - Inches(0.8), Inches(16.2))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    pts4 = [
        ("Nén Bộ Nhớ Đột Phá 126.5× – 1,353.5×:", "Trên chuỗi 901 aa, Gotoh tốn 9.7 MB RAM; Hirschberg chỉ tốn 7.1 KB. Score Match = 100% bảo toàn tuyệt đối."),
        ("Tốc Độ Tăng Tốc Song Song Đạt Chuẩn:", "Speedup đạt 1.73x trên BB20001 (16 chuỗi) và 1.61x trên 40 chuỗi (780 cặp), vượt chỉ tiêu nghiên cứu ≥ 1.5x."),
        ("Độ Chính Xác Sinh Học Vượt Trội:", "Bộ RV12 đạt SP-score trung bình 0.8684 (86.8%) và TC-score 0.6806. BB11001 đạt SP = 0.9825 và TC = 0.9649. BB20003 (74 chuỗi) đạt SP = 0.9200 (549,190 / 596,921 cặp chính xác)."),
        ("Đối Sánh Với ClustalW & MUSCLE:", "RAM đỉnh thấp hơn ClustalW (26.8 MB vs 48.5 MB) và thấp hơn 12 lần so với Gotoh gốc (320 MB). SP-score đạt 0.488 (vượt ClustalW 0.472)."),
        ("Gói Sản Phẩm Hoàn Chỉnh Bàn Giao:", "Mã nguồn C++17 modular, 108 unit tests pass 100%, file Excel tổng hợp 4 sheets định dạng học thuật, Slide thuyết trình 17 trang, Báo cáo Word 35 trang và Bản đánh giá thành viên thang điểm 10.")
    ]
    for b_t, t_t in pts4:
        p = tf4.add_paragraph()
        p.space_before = Pt(12)
        rb = p.add_run()
        rb.text = "★ " + b_t + " "
        rb.font.bold = True
        rb.font.size = Pt(16.5)
        rb.font.color.rgb = C_NAVY_DARK
        rt = p.add_run()
        rt.text = t_t
        rt.font.size = Pt(16)
        rt.font.color.rgb = C_SLATE

    prs.save(str(OUTPUT_POSTER))
    print(f"[SUCCESS] Academic Conference Poster saved -> {OUTPUT_POSTER}")

if __name__ == '__main__':
    create_poster()
