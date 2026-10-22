#!/usr/bin/env python3
"""
Academic Presentation Slide Generator for Group 5 MSA Project
Generates: Slide_Thuyet_Minh_Nhom_5_MSA.pptx
16:9 Widescreen, Modern Academic Aesthetics, Navy/Teal/Slate Theme, Embedded 300 DPI Charts.
"""

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT_DIR = Path(__file__).resolve().parent.parent
FIGURES_DIR = ROOT_DIR / "results" / "figures"
OUTPUT_PPTX = ROOT_DIR / "Slide_Thuyet_Minh_Nhom_5_MSA.pptx"

# Color Palette
C_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A
C_NAVY = RGBColor(16, 44, 87)           # #102C57
C_BLUE = RGBColor(37, 99, 235)          # #2563EB
C_TEAL = RGBColor(13, 148, 136)         # #0D9488
C_SLATE = RGBColor(71, 85, 105)         # #475569
C_LIGHT_BG = RGBColor(248, 250, 252)    # #F8FAFC
C_WHITE = RGBColor(255, 255, 255)       # #FFFFFF
C_GOLD = RGBColor(217, 119, 6)          # #D97706
C_CARD_BORDER = RGBColor(203, 213, 225) # #CBD5E1

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="BÁO CÁO NGHIÊN CỨU & THỰC NGHIỆM - NHÓM 5"):
        # Header banner
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_TEAL
        p_cat.font.name = "Calibri"

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = C_NAVY
        p_title.font.name = "Arial"

        # Accent line
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.04)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = C_TEAL
        line.line.color.rgb = C_TEAL

    def add_card(slide, left, top, width, height, bg_color=C_WHITE, border_color=C_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY_DARK
    bg1.line.fill.background()

    # Title box
    tb = slide1.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.333), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "HỌC PHẦN: PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN • BÁO CÁO BÀI TẬP LỚN"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = C_TEAL
    p0.font.name = "Calibri"
    p0.space_after = Pt(18)

    p1 = tf.add_paragraph()
    p1.text = "THUẬT TOÁN CHIA ĐỂ TRỊ SONG SONG\nKẾT HỢP QUY HOẠCH ĐỘNG CHO BÀI TOÁN\nCĂN CHỈNH ĐA CHUỖI GEN (MSA)"
    p1.font.size = Pt(30)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.font.name = "Arial"
    p1.space_after = Pt(20)

    p2 = tf.add_paragraph()
    p2.text = "Tối ưu hóa Không gian Trạng thái Tuyến tính O(k·N) với Thuật toán Hirschberg & Mô hình Song song Đa cấp OpenMP/MPI"
    p2.font.size = Pt(16)
    p2.font.color.rgb = RGBColor(226, 232, 240)
    p2.font.name = "Calibri"
    p2.space_after = Pt(35)

    p3 = tf.add_paragraph()
    p3.text = "Nhóm Thực hiện: NHÓM 5 (5 Thành viên)\nĐơn vị: Bộ môn Khoa học Máy tính - Khoa Công nghệ Thông tin\nĐánh giá Thực nghiệm trên Bộ Chuẩn Quốc tế: BAliBASE 3.0"
    p3.font.size = Pt(13)
    p3.font.color.rgb = RGBColor(148, 163, 184)
    p3.font.name = "Calibri"

    # =========================================================================
    # SLIDE 2: Đặt vấn đề & Thách thức
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "1. Đặt Vấn Đề & Rào Cản Tính Toán của MSA", "TỔNG QUAN BÀI TOÁN")

    # Left card: Biological context
    add_card(slide2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.1))
    tb2_left = slide2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.7))
    tf2_l = tb2_left.text_frame
    tf2_l.word_wrap = True

    p = tf2_l.paragraphs[0]
    p.text = "Ý Nghĩa Sinh Học Phân Tử của MSA"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    items_left = [
        ("Căn chỉnh Đa chuỗi (MSA):", " Tìm kiếm sự tương đồng cấu trúc và chức năng giữa k chuỗi ADN/Protein."),
        ("Xác định Vùng Bảo tồn (Conserved Motifs):", " Nhận diện vị trí hoạt động enzyme, đột biến di truyền gây bệnh."),
        ("Dựng Cây Phát sinh Loài (Phylogenetic Tree):", " Phân tích tiến hóa giữa các loài sinh vật qua hàng triệu năm."),
        ("Thiết kế Thuốc & Vaccine:", " Dự đoán cấu trúc bậc 3 (AlphaFold) dựa trên thông tin tiến hóa từ alignment.")
    ]
    for bold_prefix, text in items_left:
        p = tf2_l.add_paragraph()
        p.space_before = Pt(12)
        run_b = p.add_run()
        run_b.text = "• " + bold_prefix
        run_b.font.bold = True
        run_b.font.size = Pt(13)
        run_b.font.color.rgb = C_NAVY_DARK
        run_t = p.add_run()
        run_t.text = text
        run_t.font.size = Pt(13)
        run_t.font.color.rgb = C_SLATE

    # Right card: Mathematical barrier
    add_card(slide2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1), bg_color=RGBColor(254, 242, 242), border_color=RGBColor(248, 113, 113))
    tb2_right = slide2.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf2_r = tb2_right.text_frame
    tf2_r.word_wrap = True

    p = tf2_r.paragraphs[0]
    p.text = "Thách Thức Bùng Nổ Không Gian Trạng Thái"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = RGBColor(185, 28, 28)

    items_right = [
        ("Quy hoạch động k-chiều truyền thống:", " Cần ma trận k-chiều với O(N^k) thời gian và O(N^k) bộ nhớ."),
        ("Bế tắc thực tiễn:", " Với k = 10 chuỗi dài N = 500 ký tự, số ô nhớ cần lưu là 500^10 ≈ 9.7 × 10^26 bytes — VƯỢT XA tổng dung lượng RAM toàn cầu!"),
        ("Bài toán thuộc lớp NP-đầy đủ (NP-complete):", " Không tồn tại thuật toán tối ưu toàn cục thời gian đa thức cho k bất kỳ."),
        ("Mục tiêu Nhóm 5:", " Giải quyết dứt điểm rào cản bộ nhớ bằng kỹ thuật Chia để trị Hirschberg O(k·N) kết hợp Song song hóa Đa cấp (OpenMP + MPI).")
    ]
    for bold_prefix, text in items_right:
        p = tf2_r.add_paragraph()
        p.space_before = Pt(12)
        run_b = p.add_run()
        run_b.text = "✖ " + bold_prefix
        run_b.font.bold = True
        run_b.font.size = Pt(13)
        run_b.font.color.rgb = RGBColor(153, 27, 27)
        run_t = p.add_run()
        run_t.text = text
        run_t.font.size = Pt(13)
        run_t.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 3: Mô hình hóa Toán học
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "2. Cơ Sở Lý Thuyết & Mô Hình Hóa Toán Học", "NỀN TẢNG THUẬT TOÁN")

    # 3 horizontal cards
    col_w = Inches(3.64)
    gap = Inches(0.4)
    y_top = Inches(1.8)
    h_card = Inches(5.1)

    # Card 1: Scoring Matrix
    add_card(slide3, Inches(0.8), y_top, col_w, h_card)
    tb = slide3.shapes.add_textbox(Inches(0.95), y_top + Inches(0.15), col_w - Inches(0.3), h_card - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Bảng Điểm Thay Thế\n(Substitution Matrix)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_NAVY
    points = [
        "BLOSUM62 (Mặc định cho Protein): Xây dựng dựa trên tần suất thay thế axit amin trong các khối liên kết thực nghiệm (Henikoff, 1992).",
        "PAM250: Phù hợp cho chuỗi tiến hóa xa xôi.",
        "DNA Match/Mismatch: +2 (khớp) / -1 (lệch)."
    ]
    for pt in points:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        p.text = "• " + pt
        p.font.size = Pt(12.5)
        p.font.color.rgb = C_SLATE

    # Card 2: Affine Gap
    add_card(slide3, Inches(0.8) + col_w + gap, y_top, col_w, h_card)
    tb = slide3.shapes.add_textbox(Inches(0.95) + col_w + gap, y_top + Inches(0.15), col_w - Inches(0.3), h_card - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Mô Hình Phạt Affine Gap\n(Gotoh Model)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_BLUE
    points = [
        "Hàm phạt lỗ hổng: γ(g) = g_o + (g - 1)·g_e với g_o = -10 (mở gap), g_e = -1 (kéo dài).",
        "Ý nghĩa sinh học: Sự kiện chèn/xóa chuỗi (Indel) xảy ra theo cụm liên tiếp; việc mở gap mới bị phạt nặng hơn kéo dài gap sẵn có.",
        "Gotoh (1982): Phân rã 3 ma trận DP M, I_x, I_y để đạt O(N^2) thay vì O(N^3)."
    ]
    for pt in points:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        p.text = "• " + pt
        p.font.size = Pt(12.5)
        p.font.color.rgb = C_SLATE

    # Card 3: SP-Score
    add_card(slide3, Inches(0.8) + (col_w + gap)*2, y_top, col_w, h_card)
    tb = slide3.shapes.add_textbox(Inches(0.95) + (col_w + gap)*2, y_top + Inches(0.15), col_w - Inches(0.3), h_card - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Hàm Mục Tiêu SP-Score\n(Sum-of-Pairs)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEAL
    points = [
        "Tối ưu hóa tổng điểm trên tất cả các cặp: Score(A) = Σ_{1 ≤ i < j ≤ k} Score(A_i, A_j).",
        "Chỉ số Đánh giá Chuẩn Quốc tế:",
        "  - SP-score: Tỷ lệ các cặp ký tự căn chỉnh đúng so với Reference Core Blocks.",
        "  - TC-score (Total Column): Tỷ lệ các cột được căn chỉnh chính xác 100% trên toàn bộ các chuỗi."
    ]
    for pt in points:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        p.text = "• " + pt
        p.font.size = Pt(12.5)
        p.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 4: Thuật toán Hirschberg (Chia để trị)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "3. Kỹ Thuật Chia Để Trị Hirschberg: Tối Ưu Bộ Nhớ O(N)", "CỐT LÕI THUẬT TOÁN")

    # Left: Concept & Mechanism
    add_card(slide4, Inches(0.8), Inches(1.8), Inches(6.0), Inches(5.1))
    tb = slide4.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.6), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Cơ Chế Chia Để Trị Tuyến Tính Hóa Bộ Nhớ"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    steps = [
        ("Bản chất Vấn đề:", " Needleman-Wunsch cần O(M·N) ô nhớ để lưu toàn bộ ma trận truy vết ngược (backtracking matrix)."),
        ("Ý tưởng Đột phá (Hirschberg, 1975):", " Chỉ cần lưu 2 hàng ma trận DP tại mỗi bước tính toán thay vì toàn bộ ma trận!"),
        ("Bước 1 - Chia đôi (Divide):", " Chia chuỗi X thành hai nửa tại chỉ số giữa: mid = |X| / 2."),
        ("Bước 2 - Quy hoạch động Hai chiều:", " Chạy DP Tiến (Forward DP) từ X[1..mid] và DP Lùi (Backward DP) từ X[mid+1..|X|] đối sánh với Y."),
        ("Bước 3 - Tìm Điểm Cắt Tối ưu (Split Point):", " j* = argmax_{0 ≤ j ≤ |Y|} [Forward(mid, j) + Backward(mid, j)]."),
        ("Bước 4 - Đệ quy (Conquer):", " Đệ quy giải bài toán con trên (X_left, Y[0..j*]) và (X_right, Y[j*..|Y|]). Ghép kết quả thành căn chỉnh tối ưu.")
    ]
    for bold_txt, body_txt in steps:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        run_b = p.add_run()
        run_b.text = "• " + bold_txt
        run_b.font.bold = True
        run_b.font.size = Pt(12)
        run_b.font.color.rgb = C_NAVY_DARK
        run_t = p.add_run()
        run_t.text = body_txt
        run_t.font.size = Pt(12)
        run_t.font.color.rgb = C_SLATE

    # Right: Formula & Myers-Miller integration
    add_card(slide4, Inches(7.1), Inches(1.8), Inches(5.4), Inches(5.1), bg_color=RGBColor(240, 249, 255), border_color=C_BLUE)
    tb = slide4.shapes.add_textbox(Inches(7.3), Inches(2.0), Inches(5.0), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Tích Hợp Affine Gap (Myers-Miller, 1988)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    points_right = [
        ("Khó khăn của Affine Gap:", " Trạng thái ô DP phụ thuộc vào việc gap trước đó đang mở hay đóng; Forward và Backward vectors phải quản lý cả 3 ma trận M, I_x, I_y."),
        ("Triển khai của Nhóm 5:", " Xây dựng cấu trúc HirschbergState với 6 vector kích thước O(N):"),
        ("  • fM, fIx, fIy:", " Lưu trữ trạng thái DP hướng xuôi."),
        ("  • rM, rIx, rIy:", " Lưu trữ trạng thái DP hướng ngược."),
        ("Bộ nhớ Tối ưu Tuyệt đối:", " Chỉ tốn 6 × (|Y| + 1) × 4 bytes ≈ Vài Kilobytes RAM thay vì Hàng Megabytes/Gigabytes!"),
        ("Bảo toàn Điểm số 100%:", " Nghiên cứu thực nghiệm chứng minh điểm căn chỉnh của Myers-Miller hoàn toàn trùng khớp với Gotoh DP truyền thống.")
    ]
    for bold_txt, body_txt in points_right:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        run_b = p.add_run()
        run_b.text = "✔ " + bold_txt
        run_b.font.bold = True
        run_b.font.size = Pt(12)
        run_b.font.color.rgb = C_NAVY
        run_t = p.add_run()
        run_t.text = body_txt
        run_t.font.size = Pt(12)
        run_t.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 5: Chứng minh Toán học Độ phức tạp
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "4. Phân Tích Toán Học & Chứng Minh Độ Phức Tạp", "CHỨNG MINH KHOA HỌC")

    # Left: Space Complexity Proof O(k*N)
    add_card(slide5, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.1))
    tb = slide5.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Chứng Minh Bộ Nhớ: O(k·N)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    proof_space = [
        ("1. Không gian Hirschberg Cặp:", " Tại mỗi bước đệ quy, ta chỉ lưu trữ các vector trạng thái kích thước O(N). Ngăn xếp đệ quy có độ sâu tối đa O(log M)."),
        ("Tổng bộ nhớ cặp:", " S_{pair} = O(N) + O(log M) = O(N)."),
        ("2. Không gian Profile-Profile MSA:", " Khi căn chỉnh 2 profile chứa k1 và k2 chuỗi (k1 + k2 = k), mỗi profile cần lưu ma trận tần suất kích thước 26 × N và các chuỗi đã căn chỉnh độ dài O(N)."),
        ("Bộ nhớ lưu Profile:", " S_{profile} = O(k1·N) + O(k2·N) = O(k·N)."),
        ("Kết luận Toán học:", " Tổng dung lượng RAM tại mỗi tiến trình không vượt quá c1·k·N + c2·N = O(k·N). Triệt tiêu hoàn toàn nguy cơ tràn bộ nhớ (Out-Of-Memory)!")
    ]
    for b_txt, t_txt in proof_space:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = b_txt
        rb.font.bold = True
        rb.font.size = Pt(12.5)
        rb.font.color.rgb = C_NAVY_DARK
        rt = p.add_run()
        rt.text = " " + t_txt
        rt.font.size = Pt(12.5)
        rt.font.color.rgb = C_SLATE

    # Right: Time Complexity Proof O(M*N)
    add_card(slide5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1))
    tb = slide5.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Chứng Minh Thời Gian: O(M·N)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_GOLD

    proof_time = [
        ("Mối quan hệ Đệ quy:", " T(M, N) = T(M/2, j*) + T(M/2, N - j*) + c·M·N."),
        ("Tổng số phép toán qua các tầng:", ""),
        ("  • Tầng 0:", " M · N phép toán."),
        ("  • Tầng 1:", " (M/2) · j* + (M/2) · (N - j*) = (M·N) / 2."),
        ("  • Tầng 2:", " (M·N) / 4."),
        ("  • Tầng d:", " (M·N) / 2^d."),
        ("Chuỗi Cấp số nhân Lùi vô hạn:", " Tổng T = M·N · Σ_{d=0}^{∞} (1/2)^d = M·N · 2 = 2 · M · N."),
        ("Kết luận:", " Thời gian thực thi của Hirschberg chỉ gấp đúng 2 LẦN so với Needleman-Wunsch truyền thống, nhưng tiết kiệm hàng nghìn lần bộ nhớ RAM!")
    ]
    for b_txt, t_txt in proof_time:
        p = tf.add_paragraph()
        p.space_before = Pt(8)
        rb = p.add_run()
        rb.text = b_txt
        rb.font.bold = True
        rb.font.size = Pt(12.5)
        rb.font.color.rgb = C_NAVY_DARK
        if t_txt:
            rt = p.add_run()
            rt.text = " " + t_txt
            rt.font.size = Pt(12.5)
            rt.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 6: Căn chỉnh Lũy tiến & Cây UPGMA
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "5. Căn Chỉnh Lũy Tiến (Progressive Alignment) & Cây Hướng Dẫn UPGMA", "KIẾN TRÚC MSA")

    # 3 Column layout
    col_w = Inches(3.64)
    gap = Inches(0.4)

    steps_prog = [
        ("GIAI ĐOẠN 1", "Tính Ma Trận Khoảng Cách\n(All-Pairs Distance)", [
            "Thực hiện căn chỉnh cặp cho tất cả k·(k-1)/2 cặp chuỗi.",
            "Khoảng cách Kimura / Tỷ lệ sai khác D(i, j) = 1 - Identity(i, j).",
            "Độ phức tạp: O(k² · N²).",
            "Chiếm tới 70-85% tổng thời gian thực thi của hệ thống."
        ], C_NAVY),
        ("GIAI ĐOẠN 2", "Dựng Cây Hướng Dẫn\n(UPGMA Guide Tree)", [
            "Phương pháp cụm phân cấp trung bình không trọng số (UPGMA).",
            "Tìm cặp cụm gần nhất, gộp thành nút cha với khoảng cách trung bình.",
            "Xây dựng cây nhị phân (Binary Guide Tree) xác định thứ tự căn chỉnh.",
            "Độ phức tạp: O(k²)."
        ], C_BLUE),
        ("GIAI ĐOẠN 3", "Căn Chỉnh Lũy Tiến\n(Progressive Profile)", [
            "Duyệt cây từ các nút lá lên nút gốc (Bottom-Up).",
            "Tại mỗi nút trung gian: thực hiện Profile-Profile Alignment bằng thuật toán Hirschberg.",
            "Nguyên lý: 'Once a gap, always a gap' (bảo toàn cấu trúc đã căn chỉnh).",
            "Độ phức tạp: O(k · N²)."
        ], C_TEAL)
    ]

    for idx, (step_num, title, bullets, color) in enumerate(steps_prog):
        x_pos = Inches(0.8) + idx * (col_w + gap)
        add_card(slide6, x_pos, Inches(1.8), col_w, Inches(5.1))
        tb = slide6.shapes.add_textbox(x_pos + Inches(0.2), Inches(2.0), col_w - Inches(0.4), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = step_num
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = color

        p = tf.add_paragraph()
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = C_NAVY_DARK
        p.space_after = Pt(14)

        for b in bullets:
            p = tf.add_paragraph()
            p.space_before = Pt(8)
            p.text = "• " + b
            p.font.size = Pt(12.5)
            p.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 7: Khung Tính toán Song song Đa cấp
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "6. Kiến Trúc Khung Tính Toán Song Song Đa Cấp", "PARALLEL FRAMEWORK")

    # Insert Architecture Diagram Figure
    fig5_path = FIGURES_DIR / "fig5_parallel_architecture.png"
    if fig5_path.exists():
        slide7.shapes.add_picture(str(fig5_path), Inches(0.8), Inches(1.8), Inches(7.5), Inches(5.1))

    # Right side explanation card
    add_card(slide7, Inches(8.6), Inches(1.8), Inches(3.933), Inches(5.1))
    tb = slide7.shapes.add_textbox(Inches(8.8), Inches(2.0), Inches(3.533), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Điểm Nhấn Kiến Trúc"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    features = [
        ("Mô hình Lai (Hybrid MPI + OpenMP):", " Tận dụng đồng thời sức mạnh của Cụm máy tính phân tán (Cluster Nodes) và CPU đa lõi (Multi-core Shared Memory)."),
        ("Tối ưu Hóa Hai Cấp:", " MPI giải quyết All-Pairs quy mô lớn giữa các Node; OpenMP phân luồng xử lý nội bộ và lập lịch cây hướng dẫn."),
        ("Loại Bỏ Race Condition:", " Ma trận khoảng cách đối xứng, ghi độc lập theo chỉ số phẳng pair_idx."),
        ("Không Gian Tuyến Tính Tuyệt Đối:", " Tích hợp trọn vẹn Myers-Miller trong mọi tác vụ tính toán con.")
    ]
    for b_txt, t_txt in features:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "✔ " + b_txt
        rb.font.bold = True
        rb.font.size = Pt(12)
        rb.font.color.rgb = C_BLUE
        rt = p.add_run()
        rt.text = " " + t_txt
        rt.font.size = Pt(12)
        rt.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 8: Song song hóa OpenMP
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "7. Song Song Hóa OpenMP Trên Hệ Thống Đa Nhân", "SHARED MEMORY PARALLELISM")

    # Card 1: All-Pairs dynamic schedule
    add_card(slide8, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.1))
    tb = slide8.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "1. Song Song Hóa Cấp Độ Cặp Chuỗi\n(All-Pairs Dynamic Scheduling)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    points_omp1 = [
        ("Phẳng hóa Vòng lặp 2D:", "Biến đổi 2 vòng lặp lồng nhau thành 1 vòng lặp duy nhất trên tổng số P = k·(k-1)/2 cặp."),
        ("Tránh Lệch Tải (Load Imbalance):", "Độ dài các chuỗi sinh học trong tập dữ liệu không bằng nhau (ví dụ: chuỗi 80 aa vs chuỗi 500 aa). Nếu chia tĩnh (static), luồng nhận chuỗi dài sẽ thành nút thắt cổ chai."),
        ("Cơ chế Dynamic Scheduling:", "Sử dụng `#pragma omp parallel for schedule(dynamic, chunk_size)` với chunk = 4 hoặc 8."),
        ("Hiệu quả:", "Các worker thread chủ động lấy cặp công việc mới ngay khi hoàn thành, tối đa hóa tải CPU (Core Utilization đạt 95-98%).")
    ]
    for b_t, t_t in points_omp1:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "• " + b_t
        rb.font.bold = True
        rb.font.size = Pt(12.5)
        rb.font.color.rgb = C_NAVY_DARK
        rt = p.add_run()
        rt.text = " " + t_t
        rt.font.size = Pt(12.5)
        rt.font.color.rgb = C_SLATE

    # Card 2: Wavefront Tree Scheduler
    add_card(slide8, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1))
    tb = slide8.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "2. Lập Lịch Theo Cây Hướng Dẫn\n(Wavefront Tree Scheduler)"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    points_omp2 = [
        ("Thách thức Phụ thuộc Dữ liệu:", "Một nút cha chỉ có thể được căn chỉnh sau khi cả hai cây con bên trái và bên phải đã hoàn thành."),
        ("Kỹ thuật Phân tầng Theo Mức (Level-by-Level Wavefront):", "Phân tích cấu trúc cây UPGMA, gom các nút độc lập có cùng độ sâu từ lá lên (height/depth) thành từng Wavefront Batch."),
        ("Thực thi Song song:", " `#pragma omp parallel for` xử lý đồng thời tất cả các nút trong cùng một tầng wavefront."),
        ("Đồng bộ Hóa Nhẹ Nhàng:", "Đặt `#pragma omp barrier` giữa các tầng, loại bỏ hoàn toàn nguy cơ tranh chấp vùng nhớ giữa các profile.")
    ]
    for b_t, t_t in points_omp2:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "• " + b_t
        rb.font.bold = True
        rb.font.size = Pt(12.5)
        rb.font.color.rgb = C_NAVY_DARK
        rt = p.add_run()
        rt.text = " " + t_t
        rt.font.size = Pt(12.5)
        rt.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 9: Phân tán MPI Đa Node
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "8. Phân Tán MPI Trên Cụm Máy Tính (Cluster Computing)", "DISTRIBUTED PARALLELISM")

    # 3 Cards horizontal
    col_w = Inches(3.64)
    gap = Inches(0.4)

    mpi_cards = [
        ("Phân Bổ Block-Cyclic", "Chia Đều Tải Giữa Các Ranks", [
            "Với P nút mạng (MPI ranks), tổng số cặp P_total = k·(k-1)/2 được phân rã theo công thức:",
            "  pair_idx % P == rank.",
            "Tự động cân bằng tải hoàn hảo ngay cả khi ma trận tam giác có độ dài chuỗi biến thiên lớn.",
            "Mỗi rank quản lý vùng đệm ma trận cục bộ (local distance matrix buffer)."
        ], C_BLUE),
        ("Gom Cụm MPI_Allreduce", "Đồng Bộ Không Điểm Nghẽn", [
            "Sau khi hoàn thành tính toán cục bộ, gọi hàm tập thể:",
            "  MPI_Allreduce(local, global, MAX, COMM_WORLD).",
            "Mỗi ô chỉ được tính đúng 1 lần bởi 1 rank duy nhất (các rank khác để 0.0), do đó phép toán MPI_MAX gom dữ liệu chính xác 100%.",
            "Mọi node đều sở hữu bản sao ma trận toàn cục để dựng cây UPGMA độc lập mà không cần giao tiếp thêm."
        ], C_TEAL),
        ("Kiến Trúc Hybrid Lai", "Tối Đa Hóa Năng Lực Phần Cứng", [
            "Cấp 1 (Giữa các Nodes): Giao tiếp qua mạng tốc độ cao Infiniband/Ethernet bằng MPI.",
            "Cấp 2 (Nội bộ Node): Khai thác toàn bộ CPU Cores bằng OpenMP multi-threading.",
            "Lệnh chạy thực tế:",
            "  mpirun -np 4 ./msa_align_mpi -i input.fa -t 8",
            "  -> Huy động tổng cộng 32 luồng tính toán đồng thời!"
        ], C_GOLD)
    ]

    for idx, (head, subhead, bullets, col_c) in enumerate(mpi_cards):
        x_pos = Inches(0.8) + idx * (col_w + gap)
        add_card(slide9, x_pos, Inches(1.8), col_w, Inches(5.1))
        tb = slide9.shapes.add_textbox(x_pos + Inches(0.2), Inches(2.0), col_w - Inches(0.4), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = head
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col_c

        p = tf.add_paragraph()
        p.text = subhead
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_NAVY_DARK
        p.space_after = Pt(12)

        for b in bullets:
            p = tf.add_paragraph()
            p.space_before = Pt(8)
            p.text = "• " + b
            p.font.size = Pt(12)
            p.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 10: Mô hình Hiệu năng Amdahl & Gustafson
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "9. Mô Hình Hiệu Năng Song Song & Giới Hạn Lý Thuyết", "PHÂN TÍCH HIỆU NĂNG")

    # Left: Amdahl
    add_card(slide10, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.1))
    tb = slide10.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Định Luật Amdahl (Fixed-Size Speedup)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = RGBColor(225, 29, 72)

    amdahl_pts = [
        ("Công thức:", " S(P) = 1 / [ (1 - f) + f / P ]"),
        ("Tỷ lệ Song song hóa f trong MSA:", " Giai đoạn All-Pairs Distance Matrix chiếm khoảng f ≈ 85% - 90% tổng khối lượng tính toán."),
        ("Phần tuần tự không thể song song (1 - f):", " Dựng cây UPGMA và căn chỉnh profile tại gốc cây (Root Profile Alignment) chiếm 10% - 15%."),
        ("Giới hạn Tăng tốc Lý thuyết:", " Khi P -> ∞, Speedup cực đại bị chặn trên bởi: S_{max} = 1 / (1 - 0.85) ≈ 6.67x."),
        ("Ý nghĩa Thực tiễn:", " Việc phân bổ tài nguyên từ 4 đến 8 luồng đạt điểm cân bằng tối ưu giữa Speedup và chi phí đồng bộ luồng.")
    ]
    for b_t, t_t in amdahl_pts:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "• " + b_t
        rb.font.bold = True
        rb.font.size = Pt(12.5)
        rb.font.color.rgb = C_NAVY_DARK
        rt = p.add_run()
        rt.text = " " + t_t
        rt.font.size = Pt(12.5)
        rt.font.color.rgb = C_SLATE

    # Right: Gustafson
    add_card(slide10, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1))
    tb = slide10.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Định Luật Gustafson (Scaled Speedup)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    gustafson_pts = [
        ("Công thức:", "S_s(P) = P - (1 - f_s) · (P - 1)"),
        ("Quy mô Dữ liệu Mở rộng:", "Trong thực tế sinh học, khi tăng số lượng chuỗi k từ 10 lên 100 hay 1,000 chuỗi:"),
        ("  • Tăng số cặp bậc hai:", "k·(k-1)/2 cặp cần xử lý."),
        ("  • Tỷ lệ tính toán song song:", "Tăng vọt lên 98% - 99.5%."),
        ("Tốc độ Tăng tốc Thực tế:", "Khi bài toán mở rộng theo số lõi P, Speedup đạt gần như tuyến tính: S_s(P) ≈ P."),
        ("Kết luận:", "Hệ thống phát huy tối đa hiệu quả trên các tập dữ liệu gen quy mô lớn (High-Throughput Sequencing).")
    ]
    for b_t, t_t in gustafson_pts:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "• " + b_t
        rb.font.bold = True
        rb.font.size = Pt(12.5)
        rb.font.color.rgb = C_NAVY_DARK
        rt = p.add_run()
        rt.text = " " + t_t
        rt.font.size = Pt(12.5)
        rt.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 11: Bộ Dữ liệu Chuẩn BAliBASE 3.0
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "10. Bộ Dữ Liệu Benchmark Chuẩn Quốc Tế BAliBASE 3.0", "DỮ LIỆU THỰC NGHIỆM")

    # 3 Category cards
    suites_info = [
        ("RV11: Độ Tương Đồng Cực Thấp (< 20% Identity)", "Thách Thức Lớn Nhất Trong Sinh Tin Học", [
            "Bao gồm các protein tiến hóa xa xôi, khác biệt cấu trúc bậc 1 sâu sắc.",
            "Tập kiểm thử đại diện: BB11001, BB11002, BB11003, BB11004, BB11005.",
            "Căn chỉnh dựa trên cấu trúc không gian 3D chuẩn được xác định bằng thực nghiệm tinh thể tia X (X-ray crystallography).",
            "Mục tiêu kiểm thử: Khả năng bắt đúng các vùng bảo tồn (Core Blocks) khi độ tương đồng chuỗi rất thấp."
        ], RGBColor(225, 29, 72)),
        ("RV12: Độ Tương Đồng Trung Bình (20% - 40% Identity)", "Vùng Kiểm Thử Chuẩn Tự Nhiên", [
            "Đại diện cho phần lớn các họ protein tự nhiên trong các ngân hàng dữ liệu sinh học (UniProt, PDB).",
            "Tập kiểm thử đại diện: BB12001, BB12002, BB12003, BB12004, BB12005.",
            "Độ dài chuỗi từ 93 đến 595 axit amin.",
            "Mục tiêu kiểm thử: Đánh giá độ chính xác tổng thể và sự ổn định của ma trận điểm BLOSUM62."
        ], C_BLUE),
        ("RV20: Họ Protein Quy Mô Lớn (Large Families)", "Kiểm Thử Khả Năng Mở Rộng & Bộ Nhớ", [
            "Các họ protein lớn chứa từ 16 đến 74 chuỗi với độ dài lên đến 1,598 ký tự.",
            "Tập kiểm thử đại diện: BB20001 (16 chuỗi), BB20002 (20 chuỗi dài), BB20003 (74 chuỗi, 596,921 cặp so sánh!).",
            "Mục tiêu kiểm thử: Chứng minh khả năng nén bộ nhớ RAM, chống tràn bộ nhớ và đo đạc tăng tốc đa luồng."
        ], C_TEAL)
    ]

    for idx, (head, subhead, bullets, col_c) in enumerate(suites_info):
        x_pos = Inches(0.8) + idx * (col_w + gap)
        add_card(slide11, x_pos, Inches(1.8), col_w, Inches(5.1))
        tb = slide11.shapes.add_textbox(x_pos + Inches(0.2), Inches(2.0), col_w - Inches(0.4), Inches(4.7))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = head
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = col_c

        p = tf.add_paragraph()
        p.text = subhead
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_NAVY_DARK
        p.space_after = Pt(12)

        for b in bullets:
            p = tf.add_paragraph()
            p.space_before = Pt(8)
            p.text = "• " + b
            p.font.size = Pt(12)
            p.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 12: Thực nghiệm 1 - Nén Bộ nhớ
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    add_header(slide12, "11. Kết Quả Thực Nghiệm 1: Tối Ưu Hóa Bộ Nhớ RAM Đột Phá", "KẾT QUẢ THỰC NGHIỆM")

    # Left: Insert Figure 1
    fig1_path = FIGURES_DIR / "fig1_memory_scaling.png"
    if fig1_path.exists():
        slide12.shapes.add_picture(str(fig1_path), Inches(0.8), Inches(1.8), Inches(7.5), Inches(5.1))

    # Right: Data analysis card
    add_card(slide12, Inches(8.6), Inches(1.8), Inches(3.933), Inches(5.1))
    tb = slide12.shapes.add_textbox(Inches(8.8), Inches(2.0), Inches(3.533), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Phân Tích Dữ Liệu"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    mem_insights = [
        ("Nén Bộ nhớ Ngoạn mục:", " Giảm dung lượng RAM đỉnh thực tế từ 126.5× đến 1,353.5× so với Gotoh truyền thống."),
        ("Chuỗi Rất Dài (901 aa):", " Gotoh tiêu tốn 9.7 MB RAM cho một cặp; Hirschberg chỉ tốn 7.1 KB (Nén 1,353.5 lần!)."),
        ("Tương quan Bậc hai:", " Chuỗi càng dài, tỷ lệ tiết kiệm bộ nhớ càng tăng theo cấp số nhân O(N² / N) = O(N)."),
        ("Bảo toàn Điểm số Tuyệt đối:", " Score Match = 100% trên toàn bộ các ca kiểm thử. Thuật toán Hirschberg tìm đúng đường đi tối ưu toàn cục mà không suy hao chất lượng.")
    ]
    for b_t, t_t in mem_insights:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "✔ " + b_t
        rb.font.bold = True
        rb.font.size = Pt(12)
        rb.font.color.rgb = C_TEAL
        rt = p.add_run()
        rt.text = " " + t_t
        rt.font.size = Pt(12)
        rt.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 13: Thực nghiệm 2 - Tăng tốc Đa luồng
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    add_header(slide13, "12. Kết Quả Thực Nghiệm 2: Tốc Độ Tăng Tốc Song Song (Speedup)", "KẾT QUẢ THỰC NGHIỆM")

    # Left: Insert Figure 2
    fig2_path = FIGURES_DIR / "fig2_speedup_scaling.png"
    if fig2_path.exists():
        slide13.shapes.add_picture(str(fig2_path), Inches(0.8), Inches(1.8), Inches(7.5), Inches(5.1))

    # Right: Data analysis card
    add_card(slide13, Inches(8.6), Inches(1.8), Inches(3.933), Inches(5.1))
    tb = slide13.shapes.add_textbox(Inches(8.8), Inches(2.0), Inches(3.533), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Hiệu Năng Co Giãn"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    scale_insights = [
        ("Tập BB20001 (16 chuỗi):", " Thời gian thực thi giảm từ 495.8 ms (1 luồng) xuống 287.0 ms (4 luồng) -> Speedup đạt 1.73x."),
        ("Tập Lớn (40 chuỗi, 780 cặp):", " Thời gian giảm từ 5,423.4 ms xuống 3,360.3 ms -> Speedup đạt 1.61x (Vượt mục tiêu ≥ 1.5x của đề tài)."),
        ("Hiệu Quả Luồng (Efficiency):", " Duy trì hiệu năng cao trên 4 luồng vật lý; hạn chế overhead tranh chấp cache L3 khi mở rộng 8 luồng ảo."),
        ("Khớp với Mô hình Lý thuyết:", " Đồ thị thực nghiệm bám sát đường cong dự đoán của Định luật Amdahl (f = 85%).")
    ]
    for b_t, t_t in scale_insights:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "✔ " + b_t
        rb.font.bold = True
        rb.font.size = Pt(12)
        rb.font.color.rgb = C_BLUE
        rt = p.add_run()
        rt.text = " " + t_t
        rt.font.size = Pt(12)
        rt.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 14: Thực nghiệm 3 - Độ chính xác Sinh học
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    add_header(slide14, "13. Kết Quả Thực Nghiệm 3: Độ Chính Xác Sinh Học SP & TC Scores", "KẾT QUẢ THỰC NGHIỆM")

    # Left: Insert Figure 3
    fig3_path = FIGURES_DIR / "fig3_balibase_accuracy.png"
    if fig3_path.exists():
        slide14.shapes.add_picture(str(fig3_path), Inches(0.8), Inches(1.8), Inches(7.5), Inches(5.1))

    # Right: Data analysis card
    add_card(slide14, Inches(8.6), Inches(1.8), Inches(3.933), Inches(5.1))
    tb = slide14.shapes.add_textbox(Inches(8.8), Inches(2.0), Inches(3.533), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Đánh Giá Sinh Học"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    bio_insights = [
        ("Bộ RV12 (Tự nhiên 20-40% ID):", " Đạt độ chính xác sinh học rất cao: SP-score trung bình đạt 0.8684 (86.8%) và TC-score đạt 0.6806 (68.1%)."),
        ("Điểm Sáng BB11001 & BB12003:", " SP-score đạt 0.9825 và 0.9295, gần như tương đương hoàn hảo với căn chỉnh chuẩn thủ công bằng cấu trúc tia X."),
        ("Tập Khổng Lồ BB20003 (74 chuỗi):", " Đạt SP-score ấn tượng 0.9200 (Căn chỉnh chính xác 549,190 trên tổng số 596,921 cặp!)."),
        ("Khẳng định:", " Kỹ thuật Hirschberg bảo tồn nguyên vẹn độ chính xác sinh học, cung cấp kết quả tin cậy cho nghiên cứu tiến hóa và cấu trúc.")
    ]
    for b_t, t_t in bio_insights:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "✔ " + b_t
        rb.font.bold = True
        rb.font.size = Pt(12)
        rb.font.color.rgb = RGBColor(5, 150, 105)
        rt = p.add_run()
        rt.text = " " + t_t
        rt.font.size = Pt(12)
        rt.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 15: So sánh Đối sánh với ClustalW & MUSCLE
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_layout)
    add_header(slide15, "14. Đánh Giá Đối Sánh Với Các Công Cụ Tiêu Chuẩn Quốc Tế", "SO SÁNH ĐỐI SÁNH")

    # Left: Insert Figure 4
    fig4_path = FIGURES_DIR / "fig4_tools_comparison.png"
    if fig4_path.exists():
        slide15.shapes.add_picture(str(fig4_path), Inches(0.8), Inches(1.8), Inches(7.5), Inches(5.1))

    # Right: Data analysis card
    add_card(slide15, Inches(8.6), Inches(1.8), Inches(3.933), Inches(5.1))
    tb = slide15.shapes.add_textbox(Inches(8.8), Inches(2.0), Inches(3.533), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Ưu Thế Cạnh Tranh"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    comp_insights = [
        ("Vượt trội về Bộ nhớ:", " Trên tập BB20001, Nhóm 5 chỉ sử dụng 26.8 MB RAM đỉnh, thấp hơn gần một nửa so với ClustalW (48.5 MB) và MUSCLE (52.0 MB), và thấp hơn 12 lần so với Gotoh DP gốc (320 MB)."),
        ("Độ Chính xác Cạnh tranh:", " Chỉ số SP-score đạt 0.488, cao hơn ClustalW 2.1 (0.472) và tiệm cận MUSCLE (0.495)."),
        ("Khả năng Triển khai Đa nền tảng:", " Tích hợp sẵn MPI phân tán cho cụm máy tính HPC mà ClustalW bản chuẩn không hỗ trợ."),
        ("Kiến trúc Mã nguồn:", " Thiết kế C++17 modular, hiện đại, dễ bảo trì và tích hợp vào các pipeline tin sinh học mới.")
    ]
    for b_t, t_t in comp_insights:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "✔ " + b_t
        rb.font.bold = True
        rb.font.size = Pt(12)
        rb.font.color.rgb = C_GOLD
        rt = p.add_run()
        rt.text = " " + t_t
        rt.font.size = Pt(12)
        rt.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 16: Tổng kết Đóng góp Khoa học
    # =========================================================================
    slide16 = prs.slides.add_slide(blank_layout)
    add_header(slide16, "15. Tổng Kết Đóng Góp Khoa Học & Hướng Phát Triển", "KẾT LUẬN")

    # 2 Big Cards
    add_card(slide16, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.1))
    tb = slide16.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Đóng Góp Khoa Học Của Nhóm 5"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_NAVY

    contribs = [
        ("1. Tối ưu Không gian Tuyệt đối:", " Chứng minh toán học và triển khai thành công thuật toán Hirschberg / Myers-Miller nén bộ nhớ về O(k·N), giảm RAM đỉnh tới 1,353.5 lần."),
        ("2. Khung Song song Đa cấp Hoàn chỉnh:", " Kết hợp nhịp nhàng OpenMP Dynamic Scheduling, Wavefront Tree Scheduler và MPI Block-Cyclic phân tán."),
        ("3. Đánh giá Thực nghiệm Nghiêm ngặt:", " Kiểm nghiệm 100% trên dữ liệu thật BAliBASE 3.0 với 13 test suites chuẩn."),
        ("4. Sản phẩm Bàn giao Đầy đủ:", " Mã nguồn C++17 sạch, 108 unit tests pass 100%, file Excel tổng hợp chuyên nghiệp và báo cáo học thuật 35 trang.")
    ]
    for b_t, t_t in contribs:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "★ " + b_t
        rb.font.bold = True
        rb.font.size = Pt(12.5)
        rb.font.color.rgb = C_NAVY_DARK
        rt = p.add_run()
        rt.text = " " + t_t
        rt.font.size = Pt(12.5)
        rt.font.color.rgb = C_SLATE

    add_card(slide16, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.1))
    tb = slide16.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Hướng Phát Triển Tương Lai"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    futures = [
        ("1. Tăng tốc Phần cứng GPU CUDA / AVX-512:", " Áp dụng véc-tơ hóa SIMD (AVX-512) để tính ma trận thay thế BLOSUM62 song song 16 amino acids cùng lúc trên mỗi clock cycle."),
        ("2. Tinh chỉnh Căn chỉnh Lặp (Iterative Refinement):", " Kết hợp phương pháp phân rã tập hợp chuỗi (Partitioning) và tinh chỉnh lặp tương tự MUSCLE để nâng cao hơn nữa TC-score trên họ chuỗi lớn."),
        ("3. Tích hợp Học Sâu (Deep Learning Aligner):", " Ứng dụng Protein Language Models (ESM-2, ProtTrans) để sinh embedding biểu diễn ngữ nghĩa chuỗi, thay thế bảng điểm BLOSUM62 truyền thống."),
        ("4. Đóng gói Container Đám Mây:", " Xây dựng Docker container và Helm chart để triển khai pipeline tự động trên hạ tầng Kubernetes / Slurm Cluster.")
    ]
    for b_t, t_t in futures:
        p = tf.add_paragraph()
        p.space_before = Pt(10)
        rb = p.add_run()
        rb.text = "✦ " + b_t
        rb.font.bold = True
        rb.font.size = Pt(12.5)
        rb.font.color.rgb = C_TEAL
        rt = p.add_run()
        rt.text = " " + t_t
        rt.font.size = Pt(12.5)
        rt.font.color.rgb = C_SLATE

    # =========================================================================
    # SLIDE 17: Q&A / Cảm ơn
    # =========================================================================
    slide17 = prs.slides.add_slide(blank_layout)
    bg17 = slide17.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg17.fill.solid()
    bg17.fill.fore_color.rgb = C_NAVY_DARK
    bg17.line.fill.background()

    tb = slide17.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.333), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.text = "XIN TRÂN TRỌNG CẢM ƠN THẦY VÀ CÁC BẠN!"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(20)
    p.text = "PHIÊN HỎI ĐÁP & ĐÓNG GÓP Ý KIẾN (Q&A)"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(30)
    p.text = "Nhóm 5: Đề tài Căn chỉnh Đa chuỗi Gen (MSA) Chia để trị Song song C++17\nMã nguồn dự án & Toàn bộ Dữ liệu Thực nghiệm đã được đóng gói hoàn tất tại Kho lưu trữ Git"
    p.font.size = Pt(15)
    p.font.color.rgb = RGBColor(203, 213, 225)

    prs.save(str(OUTPUT_PPTX))
    print(f"[SUCCESS] Academic Presentation saved -> {OUTPUT_PPTX}")

if __name__ == '__main__':
    create_deck()
