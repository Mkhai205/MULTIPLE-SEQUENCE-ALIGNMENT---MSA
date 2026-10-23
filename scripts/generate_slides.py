#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generator for Group 5 Presentation Slide Deck (.pptx)
Course: Algorithm Analysis and Design (Phân tích và Thiết kế Thuật toán)
Topic: Parallel Divide-and-Conquer & Dynamic Programming for Multiple Sequence Alignment (MSA)
Generates: Slide_Thuyet_Trinh_PTTKTT_Nhom_5_MSA.pptx (18 Main Slides + 3 Backup Q&A Slides)
"""

from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_IMG_DIR = ROOT_DIR / "docs" / "images"
RES_FIG_DIR = ROOT_DIR / "results" / "figures"
OUTPUT_PPTX = ROOT_DIR / "Slide_Thuyet_Trinh_PTTKTT_Nhom_5_MSA.pptx"

# Color Palette (Academic Deep Navy, Cyan, Emerald, Crimson, Amber)
C_NAVY = RGBColor(15, 23, 42)        # #0F172A
C_SLATE = RGBColor(30, 41, 59)       # #1E293B
C_MUTED = RGBColor(71, 85, 105)      # #475569
C_LIGHT_BG = RGBColor(248, 250, 252) # #F8FAFC
C_CARD_BG = RGBColor(255, 255, 255)  # #FFFFFF
C_BORDER = RGBColor(203, 213, 225)   # #CBD5E1

C_BLUE = RGBColor(2, 132, 199)       # #0284C7
C_BLUE_BG = RGBColor(224, 242, 254)  # #E0F2FE
C_GREEN = RGBColor(5, 150, 105)      # #059669
C_GREEN_BG = RGBColor(209, 250, 229) # #D1FAE5
C_RED = RGBColor(225, 29, 72)        # #E11D48
C_RED_BG = RGBColor(255, 228, 230)   # #FFE4E6
C_AMBER = RGBColor(217, 119, 6)      # #D97706
C_AMBER_BG = RGBColor(254, 243, 199) # #FEF3C7
C_PURPLE = RGBColor(124, 58, 237)    # #7C3AED
C_PURPLE_BG = RGBColor(243, 232, 255)# #F3E8FF
C_WHITE = RGBColor(255, 255, 255)

FONT_MAIN = "Segoe UI"
FONT_MONO = "Consolas"


def set_slide_bg(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_Notes(slide, text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text


def add_header_footer(slide, section_label, title_text, action_subtitle, slide_num, total_main=18):
    set_slide_bg(slide, C_LIGHT_BG)

    # Top Header Banner
    header = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.18)
    )
    header.fill.solid()
    header.fill.fore_color.rgb = C_NAVY
    header.line.fill.background()

    # Accent Bottom Stripe on Header
    stripe = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.04)
    )
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = C_BLUE
    stripe.line.fill.background()

    # Section Pill Badge
    pill = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.45), Inches(0.12), Inches(3.3), Inches(0.26)
    )
    pill.fill.solid()
    pill.fill.fore_color.rgb = C_BLUE
    pill.line.fill.background()
    tf_p = pill.text_frame
    tf_p.word_wrap = False
    tf_p.margin_left = tf_p.margin_right = tf_p.margin_top = tf_p.margin_bottom = 0
    p = tf_p.paragraphs[0]
    p.text = section_label.upper()
    p.font.name = FONT_MAIN
    p.font.size = Pt(9.5)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.alignment = PP_ALIGN.CENTER

    # Main Title & Action Subtitle
    tb = slide.shapes.add_textbox(Inches(0.45), Inches(0.38), Inches(12.4), Inches(0.75))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p1 = tf.paragraphs[0]
    p1.text = title_text
    p1.font.name = FONT_MAIN
    p1.font.size = Pt(20)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf.add_paragraph()
    p2.text = action_subtitle
    p2.font.name = FONT_MAIN
    p2.font.size = Pt(11.5)
    p2.font.italic = True
    p2.font.color.rgb = RGBColor(186, 230, 253)

    # Bottom Footer Bar
    footer = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.15), Inches(13.333), Inches(0.35)
    )
    footer.fill.solid()
    footer.fill.fore_color.rgb = RGBColor(226, 232, 240)
    footer.line.fill.background()

    ftb = slide.shapes.add_textbox(Inches(0.45), Inches(7.18), Inches(9.5), Inches(0.28))
    ftf = ftb.text_frame
    ftf.margin_left = ftf.margin_top = 0
    fp = ftf.paragraphs[0]
    fp.text = "Nhóm 5 | Phân tích & Thiết kế Thuật toán — Thuật toán Chia để trị Song song Myers-Miller cho MSA"
    fp.font.name = FONT_MAIN
    fp.font.size = Pt(9.5)
    fp.font.color.rgb = C_MUTED

    stb = slide.shapes.add_textbox(Inches(10.8), Inches(7.18), Inches(2.08), Inches(0.28))
    stf = stb.text_frame
    stf.margin_right = stf.margin_top = 0
    sp = stf.paragraphs[0]
    sp.text = f"Slide {slide_num} / {total_main}" if isinstance(slide_num, int) else f"Backup {slide_num}"
    sp.font.name = FONT_MAIN
    sp.font.size = Pt(9.5)
    sp.font.bold = True
    sp.font.color.rgb = C_NAVY
    sp.alignment = PP_ALIGN.RIGHT


def add_card(slide, left, top, width, height, title=None, bg_color=C_CARD_BG, border_color=C_BORDER, header_color=None):
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    card.adjustments[0] = 0.02
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1.25)
    else:
        card.line.fill.background()

    content_top = top + 0.12
    if title:
        if header_color:
            hbar = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(0.42)
            )
            hbar.adjustments[0] = 0.02
            hbar.fill.solid()
            hbar.fill.fore_color.rgb = header_color
            hbar.line.fill.background()
            tf = hbar.text_frame
            tf.margin_left = Inches(0.18)
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = FONT_MAIN
            p.font.size = Pt(13)
            p.font.bold = True
            p.font.color.rgb = C_WHITE
            content_top = top + 0.48
        else:
            tb = slide.shapes.add_textbox(Inches(left + 0.16), Inches(top + 0.1), Inches(width - 0.32), Inches(0.36))
            tf = tb.text_frame
            tf.margin_left = tf.margin_top = 0
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = FONT_MAIN
            p.font.size = Pt(13.5)
            p.font.bold = True
            p.font.color.rgb = C_NAVY
            content_top = top + 0.44

    return content_top


def add_bullets(slide, left, top, width, height, items, font_size=12, space_after=6):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        if isinstance(item, tuple):
            # (bold_prefix, regular_text) or (bold_prefix, regular_text, color)
            prefix = item[0]
            rest = item[1]
            col = item[2] if len(item) > 2 else C_SLATE

            r1 = p.add_run()
            r1.text = prefix
            r1.font.name = FONT_MAIN
            r1.font.size = Pt(font_size)
            r1.font.bold = True
            r1.font.color.rgb = col

            r2 = p.add_run()
            r2.text = rest
            r2.font.name = FONT_MAIN
            r2.font.size = Pt(font_size)
            r2.font.color.rgb = C_SLATE
        else:
            r = p.add_run()
            r.text = item
            r.font.name = FONT_MAIN
            r.font.size = Pt(font_size)
            r.font.color.rgb = C_SLATE


def add_formula_box(slide, left, top, width, height, title, formula_lines, bg_color=C_BLUE_BG, border_color=C_BLUE):
    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height)
    )
    box.adjustments[0] = 0.03
    box.fill.solid()
    box.fill.fore_color.rgb = bg_color
    box.line.color.rgb = border_color
    box.line.width = Pt(1.5)

    tb = slide.shapes.add_textbox(Inches(left + 0.16), Inches(top + 0.08), Inches(width - 0.32), Inches(height - 0.16))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    if title:
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.name = FONT_MAIN
        p0.font.size = Pt(11.5)
        p0.font.bold = True
        p0.font.color.rgb = border_color
        p0.space_after = Pt(4)

    for idx, fline in enumerate(formula_lines):
        p = tf.paragraphs[0] if (idx == 0 and not title) else tf.add_paragraph()
        p.text = fline
        p.font.name = FONT_MONO
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = C_NAVY
        p.space_after = Pt(3)


def add_picture_fit(slide, img_path, left, top, max_w, max_h, add_frame=True):
    img_path = Path(img_path)
    if not img_path.exists():
        return
    if add_frame:
        frame = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(max_w), Inches(max_h)
        )
        frame.adjustments[0] = 0.015
        frame.fill.solid()
        frame.fill.fore_color.rgb = C_WHITE
        frame.line.color.rgb = C_BORDER
        frame.line.width = Pt(1.0)
        pad = 0.08
        left += pad
        top += pad
        max_w -= 2 * pad
        max_h -= 2 * pad

    with Image.open(img_path) as im:
        w_px, h_px = im.size
    aspect = w_px / float(h_px)
    box_aspect = max_w / float(max_h)

    if aspect >= box_aspect:
        draw_w = max_w
        draw_h = max_w / aspect
    else:
        draw_h = max_h
        draw_w = max_h * aspect

    offset_x = left + (max_w - draw_w) / 2.0
    offset_y = top + (max_h - draw_h) / 2.0
    slide.shapes.add_picture(str(img_path), Inches(offset_x), Inches(offset_y), width=Inches(draw_w), height=Inches(draw_h))


def add_styled_table(slide, left, top, width, height, headers, rows, col_widths=None, font_size=10.5):
    num_rows = len(rows) + 1
    num_cols = len(headers)
    table_shape = slide.shapes.add_table(num_rows, num_cols, Inches(left), Inches(top), Inches(width), Inches(height))
    table = table_shape.table

    if col_widths:
        for i, cw in enumerate(col_widths):
            table.columns[i].width = Inches(cw)

    # Header formatting
    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        p.text = h_text
        p.font.name = FONT_MAIN
        p.font.size = Pt(font_size)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT

    # Rows formatting
    for r_idx, row_data in enumerate(rows):
        is_highlight = any("Myers-Miller" in str(x) or "Nhóm 5" in str(x) or "1.353" in str(x) for x in row_data)
        bg = C_GREEN_BG if is_highlight else (C_WHITE if r_idx % 2 == 0 else RGBColor(241, 245, 249))
        for c_idx, val in enumerate(row_data):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.text = str(val)
            p.font.name = FONT_MAIN
            p.font.size = Pt(font_size)
            p.font.bold = is_highlight or (c_idx == 0)
            p.font.color.rgb = C_GREEN if (is_highlight and c_idx > 0) else C_SLATE
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT


def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, C_NAVY)

    # Decorative geometric accent bars
    bar_top = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    bar_top.fill.solid()
    bar_top.fill.fore_color.rgb = C_BLUE
    bar_top.line.fill.background()

    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.9), Inches(5.2), Inches(0.42))
    badge.fill.solid()
    badge.fill.fore_color.rgb = C_BLUE
    badge.line.fill.background()
    bp = badge.text_frame.paragraphs[0]
    bp.text = "BÁO CÁO ĐỒ ÁN • PHÂN TÍCH & THIẾT KẾ THUẬT TOÁN"
    bp.font.name = FONT_MAIN
    bp.font.size = Pt(12)
    bp.font.bold = True
    bp.font.color.rgb = C_WHITE
    bp.alignment = PP_ALIGN.CENTER

    tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.55), Inches(11.7), Inches(2.5))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "THUẬT TOÁN CHIA ĐỂ TRỊ SONG SONG KẾT HỢP QUY HOẠCH ĐỘNG CHO CĂN CHỈNH ĐA CHUỖI PROTEIN/ADN (MSA)"
    p.font.name = FONT_MAIN
    p.font.size = Pt(30)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.space_after = Pt(14)

    p2 = tf1.add_paragraph()
    p2.text = "Tối ưu Bộ nhớ Tuyến tính O(min(m,n)) bằng Myers-Miller • Cây Hướng dẫn UPGMA • Song song Đa tầng OpenMP & MPI"
    p2.font.name = FONT_MAIN
    p2.font.size = Pt(15.5)
    p2.font.color.rgb = RGBColor(125, 211, 252)

    # 4 Key Metric Highlight Cards on Title Slide
    metrics = [
        ("1.353,5×", "Giảm bộ nhớ RAM đỉnh\nO(mn) → O(min(m, n))", C_BLUE),
        ("100% Match", "Độ chính xác điểm số\ntrùng khớp Gotoh NW", C_GREEN),
        ("OpenMP + MPI", "Song song hóa đa tầng\nSpeedup tới 1,73×", C_AMBER),
        ("BAliBASE 3.0", "Đạt 86,8% SP Score\n342 Automated Tests", C_PURPLE),
    ]
    for i, (big_val, desc, col) in enumerate(metrics):
        x = 0.8 + i * 2.98
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(4.35), Inches(2.78), Inches(1.45))
        card.fill.solid()
        card.fill.fore_color.rgb = RGBColor(30, 41, 59)
        card.line.color.rgb = col
        card.line.width = Pt(1.75)
        tfc = card.text_frame
        tfc.word_wrap = True
        tfc.margin_left = Inches(0.15)
        tfc.margin_top = Inches(0.18)
        pc1 = tfc.paragraphs[0]
        pc1.text = big_val
        pc1.font.name = FONT_MAIN
        pc1.font.size = Pt(22)
        pc1.font.bold = True
        pc1.font.color.rgb = col
        pc2 = tfc.add_paragraph()
        pc2.text = desc
        pc2.font.name = FONT_MAIN
        pc2.font.size = Pt(11.5)
        pc2.font.color.rgb = RGBColor(226, 232, 240)

    # Footer info on Title Slide
    ft = s1.shapes.add_textbox(Inches(0.8), Inches(6.25), Inches(11.7), Inches(0.8))
    ftf = ft.text_frame
    fp = ftf.paragraphs[0]
    fp.text = "Thực hiện: Nhóm 5   |   Ngôn ngữ: Modern C++17, OpenMP, MPI, Python FastAPI   |   Chuẩn đánh giá: BAliBASE 3.0"
    fp.font.name = FONT_MAIN
    fp.font.size = Pt(13)
    fp.font.bold = True
    fp.font.color.rgb = RGBColor(148, 163, 184)

    add_Notes(s1, (
        "Xin chào Thầy/Cô và các bạn. Hôm nay Nhóm 5 xin trình bày báo cáo đồ án môn Phân tích và Thiết kế Thuật toán "
        "với đề tài: Thuật toán Chia để trị Song song kết hợp Quy hoạch động cho Căn chỉnh Đa chuỗi Protein/ADN (MSA). "
        "Đóng góp trọng tâm của nhóm là giải quyết nút thắt bộ nhớ bậc hai O(mn) của quy hoạch động truyền thống xuống tuyến tính O(min(m,n)), "
        "tiết kiệm hơn 1.350 lần RAM mà không làm giảm điểm số, kết hợp song song hóa đa tầng OpenMP/MPI và kiểm chứng trên chuẩn quốc tế BAliBASE 3.0."
    ))

    # =========================================================================
    # SLIDE 2: BÀI TOÁN MSA & MÔ HÌNH HÓA TOÁN HỌC
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s2, "Phần 1 • Đặt vấn đề & Mô hình hóa",
        "Bài toán Căn chỉnh Đa chuỗi (MSA) & Mô hình Hóa Toán học",
        "MSA tìm kiếm sự tương đồng tiến hóa thông qua tối ưu hóa hàm mục tiêu Sum-of-Pairs và phạt khoảng trống Affine",
        2
    )

    # Left Column: Biological Context & Visual Alignment Example
    ct_left = add_card(s2, 0.45, 1.38, 6.05, 5.55, "1. Bối cảnh Sinh học & Định nghĩa Hình thức", header_color=C_NAVY)
    add_bullets(s2, 0.65, ct_left + 0.05, 5.65, 2.5, [
        ("• Đầu vào: ", "Tập k chuỗi sinh học S = {S₁, S₂, ..., Sₖ} trên bảng chữ cái Σ (20 Amino Acid hoặc 4 Nucleotide), độ dài n₁, n₂, ..., nₖ."),
        ("• Biến đổi Căn chỉnh: ", "Chèn ký tự khoảng trống '-' vào các chuỗi để tạo ma trận A kích thước k × L (với max(nᵢ) ≤ L ≤ ∑nᵢ), không có cột nào chứa toàn '-'."),
        ("• Ý nghĩa Thực tiễn: ", "Phát hiện vùng bảo tồn tiến hóa, dự đoán cấu trúc bậc 3 Protein, dựng cây phát sinh chủng loại (Phylogenetics)."),
    ], font_size=12, space_after=8)

    add_formula_box(s2, 0.65, 4.35, 5.65, 2.35, "Ví dụ Minh họa Căn chỉnh Đa chuỗi (Bảo tồn Cột):", [
        "Trước căn chỉnh (Độ dài lệch nhau):",
        "  Seq1: MVLSPADKTNVKAAW",
        "  Seq2: MVLSAADKTNVK",
        "Sau căn chỉnh MSA (Khớp các cột tương đồng):",
        "  Seq1: M V L S P A D K T N V K A A W",
        "  Seq2: M V L S A A D K T N V K - - -",
        "  Seq3: M V L S E G E W Q L V L H V W",
        "        * * * * . . : . . : * :      "
    ], bg_color=RGBColor(241, 245, 249), border_color=C_SLATE)

    # Right Column: Mathematical Scoring Models
    ct_right = add_card(s2, 6.75, 1.38, 6.13, 5.55, "2. Mô hình Hàm Mục tiêu Tối ưu hóa", header_color=C_BLUE)
    add_formula_box(s2, 6.95, ct_right + 0.08, 5.73, 2.25, "Hàm mục tiêu Sum-of-Pairs (SP Score) + Ma trận BLOSUM62:", [
        "SP(A) = ∑_{1 ≤ p < q ≤ k}  ∑_{c = 1..L}  score(A[p,c], A[q,c])",
        "",
        "• Khớp 2 Amino Acid: score(x, y) = BLOSUM62(x, y)",
        "• Cặp (-, -) giữa 2 khoảng trống: score('-', '-') = 0",
        "• Mục tiêu: Tìm ma trận A* đạt argmax SP(A)"
    ], bg_color=C_BLUE_BG, border_color=C_BLUE)

    add_formula_box(s2, 6.95, 4.35, 5.73, 2.35, "Mô hình Phạt Khoảng trống Affine (Affine Gap Penalty):", [
        "γ(g) = G_open + (g - 1) × G_ext   (với g ≥ 1)",
        "",
        "• Mở khoảng trống mới:   G_open = -10 (Phạt nặng)",
        "• Kéo dài khoảng trống: G_ext  = -1  (Phạt nhẹ)",
        "→ Phản ánh đúng đột biến sinh học: 1 sự kiện mất đoạn",
        "  dài xảy ra phổ biến hơn nhiều đột biến đơn lẻ rời rạc."
    ], bg_color=C_GREEN_BG, border_color=C_GREEN)

    add_Notes(s2, (
        "Về mặt mô hình hóa toán học, cho k chuỗi sinh học có độ dài khác nhau, ta cần chèn các dấu gạch ngang '-' "
        "để đưa chúng về cùng độ dài L sao cho tổng điểm tương đồng cặp đôi Sum-of-Pairs trên toàn bộ các cột là lớn nhất. "
        "Điểm tương đồng giữa 2 amino acid được tra từ ma trận tiến hóa BLOSUM62. Đặc biệt, hệ thống áp dụng hàm phạt khoảng trống Affine: "
        "mở khoảng trống mới phạt nặng (-10), kéo dài khoảng trống phạt nhẹ (-1) để gom cụm các đột biến mất đoạn liên tục."
    ))

    # =========================================================================
    # SLIDE 3: THÁCH THỨC TÍNH TOÁN & ĐỘNG LỰC NGHIÊN CỨU
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s3, "Phần 1 • Đặt vấn đề & Mô hình hóa",
        "Thách thức Tính toán: Sự Bùng nổ Không gian Trạng thái & Bộ nhớ",
        "Quy hoạch động đa chiều là NP-Hard O(2^k · N^k), trong khi DP cặp đôi truyền thống gây tràn RAM ở O(N²)",
        3
    )

    cards_s3 = [
        ("1. Bùng nổ Tổ hợp Đa chiều (NP-Hard)", C_RED, C_RED_BG, [
            ("• DP Đa chiều chính xác: ", "Cần duy trì siêu lập phương (hypercube) k chiều."),
            ("• Độ phức tạp Bộ nhớ: ", "O(N^k) — Với k = 10 chuỗi, N = 500 → cần 10²⁷ ô nhớ!"),
            ("• Độ phức tạp Thời gian: ", "O(2^k · N^k) tại mỗi đỉnh."),
            ("• Định lý Wang & Jiang (1994): ", "Bài toán MSA tối ưu hóa SP Score thuộc lớp NP-Complete. Không thể giải chính xác khi k ≥ 5.")
        ]),
        ("2. Nút thắt Bộ nhớ Bậc hai Gotoh O(mn)", C_AMBER, C_AMBER_BG, [
            ("• Thuật toán Gotoh (1982): ", "Để xử lý Affine Gap trên 2 chuỗi (m, n), cần lưu 3 ma trận 2D: M, Ix, Iy."),
            ("• Dung lượng RAM: ", "3 × m × n × 4 bytes."),
            ("• Khi chuỗi dài (m = n = 10.000): ", "Tốn ~1,2 GB RAM chỉ cho MỘT cặp chuỗi duy nhất!"),
            ("• Hệ quả khi chạy Đa luồng: ", "Nếu P luồng cùng căn chỉnh trên ma trận 2D, hệ thống lập tức tràn bộ nhớ (Out-Of-Memory).")
        ]),
        ("3. Chi phí Thời gian Tuần tự Lớn", C_PURPLE, C_PURPLE_BG, [
            ("• Ma trận Khoảng cách: ", "Cần thực hiện k(k-1)/2 phép căn chỉnh cặp đôi độc lập (ví dụ k=40 → 780 cặp)."),
            ("• Căn chỉnh Profile trên Cây: ", "Tính điểm cột-đối-cột PSP tốn O(|P₁|·|P₂|) cho mỗi ô quy hoạch động."),
            ("• Nhu cầu Cấp thiết: ", "Cần kết hợp giải thuật tiết kiệm bộ nhớ với kiến trúc tính toán song song đa nhân / phân tán.")
        ])
    ]

    for i, (ctitle, border_c, bg_c, citems) in enumerate(cards_s3):
        x = 0.45 + i * 4.18
        ct = add_card(s3, x, 1.38, 4.02, 4.15, ctitle, bg_color=C_WHITE, border_color=border_c, header_color=border_c)
        add_bullets(s3, x + 0.16, ct + 0.08, 3.70, 3.4, citems, font_size=11.5, space_after=8)

    # Bottom Solution Banner
    sol_top = add_card(s3, 0.45, 5.72, 12.43, 1.25, "ĐÓNG GÓP & GIẢI PHÁP CỦA NHÓM 5 (3 TRỤ CỘT KỸ THUẬT)", bg_color=C_GREEN_BG, border_color=C_GREEN, header_color=C_GREEN)
    add_bullets(s3, 0.65, sol_top + 0.02, 12.0, 0.7, [
        ("① Chia để trị Myers-Miller (Hirschberg): ", "Ép không gian bộ nhớ từ O(mn) xuống tuyến tính O(min(m, n)) — tiết kiệm tới 1.353× RAM, giữ nguyên 100% điểm số tối ưu."),
        ("② Xấp xỉ Tiến bộ UPGMA + Profile-to-Profile: ", "Đưa bài toán NP-Hard O(2^k·N^k) về đa thức O(k²N² + kL²) với nguyên lý bảo tồn khoảng trống."),
        ("③ Kiến trúc Song song Đa tầng Hybrid (MPI + OpenMP): ", "Song song hóa ma trận khoảng cách, lập lịch cây theo tầng (Level-Set) và đường chéo Wavefront.")
    ], font_size=11, space_after=3)

    add_Notes(s3, (
        "Slide này tóm tắt 3 rào cản lớn của bài toán MSA: Thứ nhất, quy hoạch động chính xác trên k chuỗi là bài toán NP-Hard với bộ nhớ O(N^k). "
        "Thứ hai, ngay cả khi quy về căn chỉnh cặp đôi bằng thuật toán Gotoh 3 ma trận, bộ nhớ bậc hai O(mn) vẫn gây tràn RAM khi chuỗi dài hoặc khi chạy song song nhiều luồng. "
        "Từ đó, nhóm đề xuất giải pháp 3 trụ cột ở khung màu xanh bên dưới: Chia để trị tuyến tính Myers-Miller, Progressive Profile UPGMA, và Song song hóa đa tầng OpenMP/MPI."
    ))

    # =========================================================================
    # SLIDE 4: TỔNG QUAN PIPELINE 4 GIAI ĐOẠN
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s4, "Phần 2 • Thiết kế Thuật toán Lõi",
        "Tổng quan Pipeline Căn chỉnh Đa chuỗi Tiến bộ (Progressive MSA)",
        "Chuyển bài toán NP-Hard về chuỗi 4 giai đoạn đa thức có khả năng mở rộng và song song hóa cao",
        4
    )

    add_picture_fit(s4, DOCS_IMG_DIR / "fig_4_1_system_architecture.png", 0.45, 1.38, 7.35, 5.55)

    ct_s4 = add_card(s4, 8.0, 1.38, 4.88, 5.55, "Luồng Xử lý 4 Giai đoạn Chính", header_color=C_NAVY)
    add_bullets(s4, 8.18, ct_s4 + 0.08, 4.52, 4.8, [
        ("Giai đoạn 1 — Ma trận Khoảng cách O(k²N²/P):", "\nTính k(k-1)/2 cặp điểm tương đồng độc lập bằng DP 1 chiều (chỉ lưu 2 hàng), chuẩn hóa về khoảng cách tiến hóa d(A,B) ∈ [0, 1].", C_BLUE),
        ("Giai đoạn 2 — Cây Hướng dẫn UPGMA O(k²):", "\nGom cụm phân cấp từ cặp chuỗi gần nhất đến xa nhất, sinh cây nhị phân dẫn đường (Binary Guide Tree).", C_PURPLE),
        ("Giai đoạn 3 — Lập lịch Cây Song song:", "\nPhân tích phụ thuộc dữ liệu trên cây UPGMA, gom các nút nhánh độc lập theo từng tầng (Level-Set).", C_GREEN),
        ("Giai đoạn 4 — Căn chỉnh Profile Myers-Miller:", "\nHợp nhất cặp Profile con tại mỗi nút cha bằng Chia để trị không gian tuyến tính O(min(m,n)) + bảo tồn khoảng trống.", C_RED),
    ], font_size=11.5, space_after=10)

    add_Notes(s4, (
        "Đây là kiến trúc tổng thể 4 giai đoạn của hệ thống Progressive MSA. "
        "Thay vì căn chỉnh tất cả chuỗi cùng lúc, ta tính khoảng cách tiến hóa giữa mọi cặp ở Giai đoạn 1, "
        "dựng cây hướng dẫn UPGMA ở Giai đoạn 2, lập lịch các nhánh con độc lập ở Giai đoạn 3, "
        "và hợp nhất tuần tự các Profile từ lá lên gốc bằng thuật toán chia để trị Myers-Miller ở Giai đoạn 4."
    ))

    # =========================================================================
    # SLIDE 5: QUY HOẠCH ĐỘNG GOTOH (1982) BASELINE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s5, "Phần 2 • Thiết kế Thuật toán Lõi",
        "Quy hoạch Động Gotoh (1982) Baseline & Nút thắt Truy vết",
        "Giải quyết chính xác phạt khoảng trống Affine bằng 3 trạng thái nhưng đòi hỏi O(mn) bộ nhớ để lưu vết đường đi",
        5
    )

    ct_s5_l = add_card(s5, 0.45, 1.38, 6.85, 5.55, "1. Hệ Phương trình Truy hồi 3 Ma trận của Gotoh (1982)", header_color=C_NAVY)
    add_bullets(s5, 0.65, ct_s5_l + 0.04, 6.45, 1.0, [
        ("Tại mỗi tọa độ (i, j), duy trì ", "3 giá trị quy hoạch động đại diện cho 3 trạng thái kết thúc của tiền tố A[1..i] và B[1..j]:")
    ], font_size=11.5)

    add_formula_box(s5, 0.65, 2.42, 6.45, 1.35, "① Trạng thái Khớp / Thay thế — M(i, j):", [
        "M(i, j) = σ(Aᵢ, Bⱼ) + max { M(i-1, j-1),",
        "                            Ix(i-1, j-1),",
        "                            Iy(i-1, j-1) }"
    ], bg_color=C_BLUE_BG, border_color=C_BLUE)

    add_formula_box(s5, 0.65, 3.88, 6.45, 1.35, "② Trạng thái Khoảng trống Dọc (Xóa ký tự Aᵢ) — Ix(i, j):", [
        "Ix(i, j) = max { M(i-1, j)  + G_open + G_ext,",
        "                 Ix(i-1, j) + G_ext }"
    ], bg_color=C_AMBER_BG, border_color=C_AMBER)

    add_formula_box(s5, 0.65, 5.34, 6.45, 1.35, "③ Trạng thái Khoảng trống Ngang (Chèn ký tự Bⱼ) — Iy(i, j):", [
        "Iy(i, j) = max { M(i, j-1)  + G_open + G_ext,",
        "                 Iy(i, j-1) + G_ext }"
    ], bg_color=C_GREEN_BG, border_color=C_GREEN)

    ct_s5_r = add_card(s5, 7.50, 1.38, 5.38, 5.55, "2. Phân tích Sự Đánh đổi: Tính Điểm vs. Truy Vết", header_color=C_RED)
    add_bullets(s5, 7.70, ct_s5_r + 0.08, 4.98, 3.1, [
        ("• Khi CHỈ tính điểm số tối ưu S(A, B):", "\nDòng thứ i chỉ phụ thuộc vào dòng i-1 liền trước → Chỉ cần lưu 2 hàng vector (prev & curr), tốn bộ nhớ tuyến tính O(n).", C_GREEN),
        ("• Khi CẦN khôi phục chuỗi căn chỉnh (Backtracking):", "\nThuật toán Gotoh truyền thống phải lưu toàn bộ 3 ma trận M, Ix, Iy kích thước (m+1)×(n+1) để lần ngược mũi tên từ (m,n) về (0,0) → Bắt buộc tốn O(mn) bộ nhớ!", C_RED),
    ], font_size=12, space_after=12)

    add_formula_box(s5, 7.70, 4.95, 4.98, 1.75, "Câu hỏi Nghiên cứu Trọng tâm:", [
        "Làm thế nào để khôi phục chính xác",
        "100% đường đi căn chỉnh tối ưu của",
        "mô hình Affine Gap mà CHỈ sử dụng",
        "các vector 1 chiều O(min(m, n))?"
    ], bg_color=C_RED_BG, border_color=C_RED)

    add_Notes(s5, (
        "Để xử lý phạt khoảng trống Affine, thuật toán Gotoh duy trì 3 trạng thái tại mỗi ô (i,j): M (khớp), Ix (khoảng trống dọc) và Iy (khoảng trống ngang). "
        "Nhận xét mấu chốt nằm ở cột bên phải: nếu chỉ cần tính điểm số cuối cùng (như ở Bước 1 tính ma trận khoảng cách), ta chỉ cần nhớ dòng liền trước, tốn O(n) bộ nhớ. "
        "Lý do duy nhất khiến Gotoh tốn O(mn) bộ nhớ là để lưu vết đường đi ngược từ (m,n) về (0,0). Đây chính là bài toán mà Chia để trị Myers-Miller giải quyết ở slide tiếp theo."
    ))

    # =========================================================================
    # SLIDE 6: ĐỘT PHÁ CHIA ĐỂ TRỊ MYERS-MILLER / HIRSCHBERG (1988)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s6, "Phần 2 • Thiết kế Thuật toán Lõi",
        "Đột phá Chia để trị Không gian Tuyến tính Myers-Miller (1988)",
        "Tìm giao điểm tối ưu (i*, j*) tại dòng giữa i* = ⌊m/2⌋ bằng 2 lượt quét DP Xuôi & Ngược chỉ với vector 1 chiều O(n)",
        6
    )

    add_picture_fit(s6, DOCS_IMG_DIR / "fig_2_1_myers_miller_cut.png", 0.45, 1.38, 6.45, 5.55)

    ct_s6 = add_card(s6, 7.10, 1.38, 5.78, 5.55, "Cơ chế Chia để trị 4 Bước (Linear-Space D&C)", header_color=C_BLUE)
    add_bullets(s6, 7.28, ct_s6 + 0.06, 5.42, 2.35, [
        ("1. Chia (Divide): ", "Cắt ngang ma trận tại dòng giữa i* = ⌊m / 2⌋."),
        ("2. Quét Xuôi (Forward Pass - O(n) RAM): ", "Chạy DP 2 hàng từ (0,0) → dòng i*, thu được vector điểm tiền tố Fwd_M[j], Fwd_Ix[j]."),
        ("3. Quét Ngược (Backward Pass - O(n) RAM): ", "Chạy DP 2 hàng từ (m,n) ngược về dòng i* trên hậu tố đảo ngược, thu được Bwd_M[j], Bwd_Ix[j]."),
    ], font_size=11.5, space_after=6)

    add_formula_box(s6, 7.28, 4.18, 5.42, 1.65, "4. Tìm Cột Cắt Tối ưu j* & Hợp nhất Khoảng trống (Gap Coalescing):", [
        "j* = argmax_{0 ≤ j ≤ n} max {",
        "   Fwd_M(j)  + Bwd_M(j),",
        "   Fwd_Ix(j) + Bwd_Ix(j) - G_open + G_ext",
        "}"
    ], bg_color=C_BLUE_BG, border_color=C_BLUE)

    add_bullets(s6, 7.28, 5.92, 5.42, 0.95, [
        ("• Hiệu chỉnh (-G_open + G_ext): ", "Nếu 1 khoảng trống xuyên qua đường cắt i*, cả lượt xuôi và ngược đều đã phạt G_open → Cộng bù để hợp nhất thành 1 gap duy nhất!", C_RED),
        ("• Đệ quy 2 Nửa Góc phần tư: ", "Gọi đệ quy trên (0,0)→(i*,j*) và (i*,j*)→(m,n). Tổng diện tích giảm đúng một nửa!"),
    ], font_size=10.8, space_after=4)

    add_Notes(s6, (
        "Đây là slide cốt lõi nhất của phần thiết kế thuật toán. Quan sát hình bên trái: thay vì lưu toàn bộ ma trận, "
        "ta cắt đôi ma trận tại dòng giữa i* = m/2. Ta chạy 1 lượt DP xuôi từ đỉnh xuống dòng i* và 1 lượt DP ngược từ đáy lên dòng i*, "
        "mỗi lượt chỉ dùng 2 hàng vector 1 chiều tốn O(n) bộ nhớ. Tại dòng giữa i*, tổng điểm xuôi cộng điểm ngược đạt cực đại tại cột j* nào "
        "thì đường đi tối ưu toàn cục bắt buộc phải đi qua điểm (i*, j*) đó! "
        "Đặc biệt, ở phương trình thứ hai trong khung xanh, nhóm xử lý trường hợp một khoảng trống mở từ nửa trên xuyên thẳng qua đường cắt xuống nửa dưới "
        "bằng cách trừ đi G_open và cộng G_ext để không phạt mở khoảng trống 2 lần. Sau khi tìm được (i*, j*), bài toán tách thành 2 bài toán con có tổng diện tích chỉ còn đúng 1/2!"
    ))

    # =========================================================================
    # SLIDE 7: CÂY HƯỚNG DẪN UPGMA
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s7, "Phần 2 • Thiết kế Thuật toán Lõi",
        "Xây dựng Cây Hướng dẫn Phân cấp UPGMA (Guide Tree)",
        "Gom cụm phân cấp theo khoảng cách trung bình trọng số, định hướng thứ tự căn chỉnh từ cặp gần nhất đến xa nhất",
        7
    )

    add_picture_fit(s7, DOCS_IMG_DIR / "fig_2_3_upgma_clustering.png", 0.45, 1.38, 6.25, 5.55)

    ct_s7 = add_card(s7, 6.90, 1.38, 5.98, 5.55, "Quy trình Toán học Thuật toán UPGMA", header_color=C_PURPLE)
    add_formula_box(s7, 7.10, ct_s7 + 0.08, 5.58, 1.45, "1. Chuẩn hóa Khoảng cách Tiến hóa Cặp đôi d(A, B) ∈ [0, 1]:", [
        "d(S_a, S_b) = max( 0.0,",
        "   1.0 - Score(S_a, S_b) / max(Score(S_a, S_a), Score(S_b, S_b))",
        ")"
    ], bg_color=C_PURPLE_BG, border_color=C_PURPLE)

    add_formula_box(s7, 7.10, 3.48, 5.58, 1.55, "2. Công thức Cập nhật Khoảng cách Cụm Trung bình Trọng số:", [
        "Khi hợp nhất 2 cụm gần nhất C_u và C_v thành cụm cha C_w:",
        "d(C_w, C_q) = ( |C_u|·d(C_u, C_q) + |C_v|·d(C_v, C_q) )",
        "              / ( |C_u| + |C_v| )"
    ], bg_color=C_BLUE_BG, border_color=C_BLUE)

    add_bullets(s7, 7.10, 5.18, 5.58, 1.6, [
        ("• Độ phức tạp: ", "O(k²) cả thời gian và không gian — thực thi < 1 ms với k ≤ 100 chuỗi."),
        ("• Tính Tiền định (Deterministic Tie-Breaking): ", "Khi hai cặp cụm có khoảng cách bằng nhau tới ngưỡng ε = 10⁻⁹, ưu tiên cặp có chỉ số ID nhỏ hơn → Đảm bảo cây UPGMA giống nhau 100% giữa chạy 1 luồng và đa luồng."),
        ("• Xuất chuẩn Sinh tin học: ", "Hỗ trợ xuất định dạng chuỗi Newick (.nwk) và JSON.")
    ], font_size=11.2, space_after=6)

    add_Notes(s7, (
        "Sau khi có ma trận khoảng cách giữa mọi cặp chuỗi từ Giai đoạn 1, thuật toán UPGMA khởi tạo mỗi chuỗi là một cụm lá độc lập. "
        "Ở mỗi bước lặp, thuật toán tìm 2 cụm có khoảng cách nhỏ nhất để ghép thành một nút cha mới trên cây nhị phân, "
        "đồng thời cập nhật khoảng cách từ cụm mới tới các cụm còn lại bằng trung bình có trọng số theo số lượng chuỗi con. "
        "Nhóm cũng thiết kế cơ chế Deterministic Tie-Breaking để cây sinh ra luôn bất biến dù chạy trên bao nhiêu luồng OpenMP."
    ))

    # =========================================================================
    # SLIDE 8: CĂN CHỈNH PROFILE-TO-PROFILE & BẢO TỒN GAP
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s8, "Phần 2 • Thiết kế Thuật toán Lõi",
        "Căn chỉnh Profile-to-Profile & Nguyên lý Bảo tồn Khoảng trống",
        "Tổng quát hóa thuật toán Myers-Miller từ 2 chuỗi đơn lên 2 Profile thông qua hàm điểm cột PSP và luật 'Once a gap, always a gap'",
        8
    )

    add_picture_fit(s8, DOCS_IMG_DIR / "fig_2_2_profile_alignment.png", 0.45, 1.38, 6.25, 5.55)

    ct_s8 = add_card(s8, 6.90, 1.38, 5.98, 5.55, "Mở rộng Chia để trị lên Không gian Profile", header_color=C_GREEN)
    add_bullets(s8, 7.10, ct_s8 + 0.06, 5.58, 1.3, [
        ("• Cấu trúc Profile: ", "Mỗi nút trong cây UPGMA lưu một Profile P gồm |P| chuỗi đã căn chỉnh có cùng độ dài cột L_P."),
        ("• Tái sử dụng Lõi Myers-Miller: ", "Xem Profile P₁ (dài m cột) và P₂ (dài n cột) như 2 'siêu chuỗi' mà mỗi phần tử là một Cột Vector Tần suất.")
    ], font_size=11.5, space_after=6)

    add_formula_box(s8, 7.10, 3.22, 5.58, 1.75, "Hàm Điểm Tương đồng Cột-đối-Cột (Profile Sum-of-Pairs — PSP):", [
        "PSP(x, y) =  1 / (|P₁| · |P₂|)",
        "           × ∑_{r=1..|P₁|} ∑_{s=1..|P₂|} score(P₁[r, x], P₂[s, y])",
        "",
        "→ Thay thế trực tiếp hàm σ(Aᵢ, Bⱼ) trong phương trình Myers-Miller!"
    ], bg_color=C_GREEN_BG, border_color=C_GREEN)

    add_bullets(s8, 7.10, 5.12, 5.58, 1.65, [
        ("• Quy tắc 'Once a gap, always a gap' (Feng & Doolittle): ", "Khi bước truy vết Myers-Miller quyết định chèn một khoảng trống vào Profile P₁, một cột gồm toàn ký tự '-' được chèn đồng loạt vào TẤT CẢ |P₁| chuỗi con tại cùng vị trí đó.", C_NAVY),
        ("• Ý nghĩa Toán học: ", "Bảo toàn 100% quan hệ căn chỉnh nội bộ đã tối ưu ở các nhánh cây con phía dưới.")
    ], font_size=11.2, space_after=6)

    add_Notes(s8, (
        "Ở các nút nhánh bên trong cây UPGMA, ta cần căn chỉnh một nhóm chuỗi này với một nhóm chuỗi khác (gọi là Profile-to-Profile). "
        "Điểm tinh tế trong thiết kế của nhóm là không viết lại thuật toán quy hoạch động mới, mà tổng quát hóa chính thuật toán chia để trị Myers-Miller: "
        "thay vì so sánh 2 ký tự A[i] và B[j], ta định nghĩa hàm điểm trung bình cặp đôi PSP(x, y) giữa toàn bộ các ký tự ở cột x của Profile 1 với cột y của Profile 2. "
        "Khi chèn khoảng trống, cả một cột dấu '-' được chèn đồng bộ vào mọi chuỗi trong Profile để không phá vỡ căn chỉnh của các bước trước."
    ))

    # =========================================================================
    # SLIDE 9: KIẾN TRÚC SONG SONG ĐA TẦNG HYBRID (MPI + OPENMP)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s9, "Phần 3 • Song song hóa & Độ phức tạp",
        "Kiến trúc Tính toán Song song Đa tầng Hybrid (MPI + OpenMP)",
        "Khai thác tính song song ở cả 3 mức: Phân tán Cụm máy tính (MPI), Đa luồng Cặp chuỗi/Nhánh cây (OpenMP) và Đường chéo phụ",
        9
    )

    add_picture_fit(s9, RES_FIG_DIR / "fig5_parallel_architecture.png", 0.45, 1.38, 7.45, 3.65)
    add_picture_fit(s9, DOCS_IMG_DIR / "fig_3_1_wavefront_antidiagonal.png", 0.45, 5.12, 7.45, 1.82)

    ct_s9 = add_card(s9, 8.08, 1.38, 4.80, 5.55, "3 Cấp độ Song song Hóa & Cân bằng Tải", header_color=C_AMBER)
    add_bullets(s9, 8.26, ct_s9 + 0.08, 4.44, 5.0, [
        ("Cấp 1 — Liên Node bằng MPI (Distributed):", "\n• Chia k(k-1)/2 cặp theo vòng tròn Block-Cyclic (idx % P == rank) giúp cân bằng tải tự nhiên.\n• Đồng bộ kết quả qua MPI_Allgatherv với chi phí truyền thông tối thiểu O(k²).", C_BLUE),
        ("Cấp 2 — Đa luồng OpenMP (Shared Memory):", "\n• Giai đoạn 1: #pragma omp parallel for schedule(dynamic, 1) chống lệch tải khi độ dài chuỗi chênh lệch.\n• Giai đoạn 3 (Level-Set Tree Scheduler): Phân rã cây UPGMA theo tầng độ cao Topo; các nhánh con độc lập cùng tầng chạy song song.", C_GREEN),
        ("Cấp 3 — Wavefront Anti-Diagonal DP:", "\n• Các ô (i, j) trên cùng đường chéo phụ i + j = d hoàn toàn độc lập dữ liệu → tính song song cho chuỗi cực dài.", C_PURPLE),
    ], font_size=11.0, space_after=8)

    add_Notes(s9, (
        "Để tăng tốc độ xử lý trên cả máy trạm đa nhân lẫn cụm máy tính HPC, nhóm xây dựng kiến trúc song song 3 tầng. "
        "Ở Giai đoạn 1 (tính ma trận khoảng cách), các cặp hoàn toàn độc lập nên đạt hiệu suất song song cao nhất nhờ chia vòng tròn Block-Cyclic trên MPI "
        "và lập lịch động schedule(dynamic, 1) trên OpenMP. "
        "Ở Giai đoạn căn chỉnh cây UPGMA, vì nút cha phụ thuộc dữ liệu vào 2 nút con, nhóm thiết kế thuật toán Level-Set Tree Scheduler gom các nút có cùng độ cao Topo vào một đợt sóng để chạy song song. "
        "Hình nhỏ bên dưới minh họa thêm kỹ thuật Wavefront Anti-Diagonal: các ô nằm trên cùng đường chéo phụ chỉ phụ thuộc vào 2 đường chéo trước đó nên có thể tính đồng thời."
    ))

    # =========================================================================
    # SLIDE 10: CHỨNG MINH TOÁN HỌC ĐỘ PHỨC TẠP THỜI GIAN & KHÔNG GIAN
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s10, "Phần 3 • Song song hóa & Độ phức tạp",
        "Chứng minh Toán học Độ phức tạp Bộ nhớ O(N) & Thời gian 2·NM",
        "Định lý chuỗi hình học chứng minh Chia để trị Myers-Miller giảm bậc bộ nhớ mà chỉ tăng thời gian đúng 2 lần hằng số",
        10
    )

    # Left Proof Card: Space Complexity
    ct_s10_l = add_card(s10, 0.45, 1.38, 6.05, 5.55, "Định lý 1: Chứng minh Độ phức tạp Không gian Tuyến tính", header_color=C_BLUE)
    add_bullets(s10, 0.65, ct_s10_l + 0.08, 5.65, 2.2, [
        ("• Cấp phát Vector Tĩnh tại mỗi Bước Chia để trị:", "\nLượt quét xuôi và ngược chỉ sử dụng 6 vector 1 chiều kích thước (n + 1): fwd_M, fwd_Ix, fwd_Iy và bwd_M, bwd_Ix, bwd_Iy."),
        ("• Thu hồi / Tái sử dụng Bộ nhớ trước khi Đệ quy:", "\nSau khi tìm được cột cắt j*, các vector tạm được giải phóng trước khi gọi đệ quy xuống 2 bài toán con → Bộ nhớ KHÔNG cộng dồn theo số nút đệ quy!"),
        ("• Độ sâu Ngăn xếp Đệ quy (Call Stack):", "\nMỗi bước chia đôi m → m/2 nên chiều cao cây đệ quy tối đa là ⌈log₂ m⌉.")
    ], font_size=11.2, space_after=8)

    add_formula_box(s10, 0.65, 4.45, 5.65, 2.25, "Tổng Không gian Bộ nhớ Đỉnh (Peak Memory Bound):", [
        "• Cho 1 cặp chuỗi (m ≥ n):",
        "  S_pair(m, n) = 6·(n + 1)·sizeof(int) + O(log₂ m)",
        "               = O(min(m, n))   [Tuyến tính hoàn toàn!]",
        "",
        "• Cho toàn bộ Pipeline MSA (k chuỗi, P luồng):",
        "  S_total(k, L, P) = O(k · L + P · L + k²) = O(k · L)"
    ], bg_color=C_BLUE_BG, border_color=C_BLUE)

    # Right Proof Card: Time Complexity Geometric Series
    ct_s10_r = add_card(s10, 6.75, 1.38, 6.13, 5.55, "Định lý 2: Chứng minh Độ phức tạp Thời gian Chuỗi Hình học", header_color=C_GREEN)
    add_bullets(s10, 6.95, ct_s10_r + 0.08, 5.73, 1.85, [
        ("• Bất biến Diện tích ở Mức Đệ quy thứ r:", "\nTại mức 0 (gốc), quét xuôi nửa trên (m/2 × n) + quét ngược nửa dưới (m/2 × n) tốn đúng c · m · n phép tính."),
        ("• Tổng diện tích 2 bài toán con ở mức 1 (với bất kỳ cột cắt j* nào):", "\nArea₁ = (m/2)·j* + (m/2)·(n - j*) = (m/2)·(j* + n - j*) = ½ (m · n)!")
    ], font_size=11.2, space_after=8)

    add_formula_box(s10, 6.95, 3.85, 5.73, 2.85, "Khai triển Tổng Chuỗi Hình học Hội tụ (Master Sum):", [
        "T(m, n) = c·mn + c·(mn / 2) + c·(mn / 4) + ... + c·(mn / 2^log₂m)",
        "",
        "        = c·mn × ∑_{r = 0..log₂m} (1 / 2)^r",
        "",
        "        ≤ c·mn × (1 + 1/2 + 1/4 + 1/8 + ...) = 2 · c · m · n",
        "",
        "⇒ T(m, n) = 2 · T_Gotoh(m, n) = O(m · n)   (Điều phải chứng minh)"
    ], bg_color=C_GREEN_BG, border_color=C_GREEN)

    add_Notes(s10, (
        "Slide này trình bày phép chứng minh toán học chặt chẽ cho cả Không gian và Thời gian. "
        "Ở Định lý 1 bên trái: vì các vector 1 chiều chỉ có kích thước n+1 và được giải phóng trước khi đi vào nhánh đệ quy, "
        "bộ nhớ tại mọi thời điểm chỉ tỉ lệ thuận với O(min(m,n)). "
        "Ở Định lý 2 bên phải: một câu hỏi kinh điển của môn Phân tích thuật toán là tại sao gọi đệ quy log₂(m) tầng mà thời gian không bị nhân thêm log₂(m)? "
        "Câu trả lời nằm ở tính chất triệt tiêu j*: tổng diện tích của 2 nửa bài toán con luôn bằng (m/2)*j* + (m/2)*(n - j*) = (1/2)*m*n. "
        "Do đó tổng khối lượng tính toán qua mọi tầng đệ quy lập thành cấp số nhân công bội 1/2: 1 + 1/2 + 1/4 + ... hội tụ về đúng bằng 2! "
        "Tức là thời gian chỉ gấp đôi hằng số so với Gotoh, giữ nguyên bậc O(mn)."
    ))

    # =========================================================================
    # SLIDE 11: BẢNG TỔNG HỢP ĐỘ PHỨC TẠP & ĐỊNH LUẬT AMDAHL
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s11, "Phần 3 • Song song hóa & Độ phức tạp",
        "Tổng hợp Độ phức tạp Toàn Hệ thống & Phân tích Định luật Amdahl",
        "Đối sánh toàn diện giữa Baseline và Hệ thống Đề xuất kèm mô hình giới hạn tăng tốc song song",
        11
    )

    headers_s11 = ["Giai đoạn / Thuật toán", "Thời gian Tuần tự", "Thời gian Song song (P luồng)", "Không gian Bộ nhớ", "Đóng góp & Ý nghĩa Kỹ thuật"]
    rows_s11 = [
        ["Gotoh NW (1982) Baseline", "O(m · n)", "—", "O(m · n)  [3 ma trận 2D]", "Tràn RAM khi chuỗi dài m, n ≥ 10⁴"],
        ["Myers-Miller D&C (Đề xuất)", "2 · O(m · n)", "O(m · n / P_wave)", "O(min(m, n))  [Vector 1D]", "Giảm >90× – 1.353× RAM, khớp 100% điểm"],
        ["GĐ 1: Ma trận Khoảng cách", "O(k² · N²)", "O(k² · N² / P)", "O(k² + P · N)", "Song song lý tưởng k(k-1)/2 cặp độc lập"],
        ["GĐ 2: Cây Hướng dẫn UPGMA", "O(k²)", "O(k²) [Tuần tự nhanh]", "O(k²)", "Thời gian không đáng kể (< 1 ms với k ≤ 100)"],
        ["GĐ 3 & 4: Progressive Tree", "O(k · L²)", "O(k · L² / P_tree)", "O(k · L)", "Duyệt cây Level-Set + Profile Myers-Miller"],
    ]
    add_styled_table(s11, 0.45, 1.38, 12.43, 3.15, headers_s11, rows_s11, col_widths=[2.65, 1.85, 2.25, 2.25, 3.43], font_size=10.5)

    # Bottom 2 Cards: Amdahl's Law & Gustafson's Law
    ct_amd = add_card(s11, 0.45, 4.72, 6.05, 2.22, "Mô hình Giới hạn Tăng tốc — Định luật Amdahl (1967)", header_color=C_NAVY)
    add_formula_box(s11, 0.65, ct_amd + 0.04, 5.65, 0.82, None, [
        "S(P) = T(1) / T(P) ≤  1 / [ (1 - f) + (f / P) ]"
    ], bg_color=C_BLUE_BG, border_color=C_BLUE)
    add_bullets(s11, 0.65, 6.08, 5.65, 0.8, [
        ("• Tỷ lệ tuần tự (1 - f) ≈ 15% – 25%: ", "Sinh ra tại nút gốc cây UPGMA (phải chờ 2 nhánh con hoàn tất mới gộp được Profile cuối cùng). Với f = 0.85, P = 8 → S_max ≈ 3.9×.")
    ], font_size=10.8)

    ct_gus = add_card(s11, 6.75, 4.72, 6.13, 2.22, "Khả năng Mở rộng Quy mô Lớn — Định luật Gustafson", header_color=C_GREEN)
    add_formula_box(s11, 6.95, ct_gus + 0.04, 5.73, 0.82, None, [
        "S_scaled(P) = (1 - f_seq) + P · f_par   (khi k → ∞)"
    ], bg_color=C_GREEN_BG, border_color=C_GREEN)
    add_bullets(s11, 6.95, 6.08, 5.73, 0.8, [
        ("• Khi số lượng chuỗi k tăng lớn: ", "Giai đoạn 1 tăng bậc hai O(k²N²) chiếm tỷ trọng áp đảo so với Giai đoạn 4 O(kL²) → Tỷ lệ song song f_par → 1, hệ thống mở rộng rất tốt!")
    ], font_size=10.8)

    add_Notes(s11, (
        "Bảng tổng hợp trên slide đối chiếu trực tiếp toàn bộ các giai đoạn. Đáng chú ý nhất là không gian bộ nhớ của toàn hệ thống "
        "chỉ còn O(k*L), tức chỉ tương đương kích thước lưu trữ các chuỗi đầu ra. "
        "Ở nửa dưới, nhóm kết hợp Định luật Amdahl và Định luật Gustafson: với một bộ dữ liệu cố định, nút gốc của cây UPGMA tạo ra phần tuần tự (1-f) khoảng 15%, "
        "nhưng khi số lượng chuỗi k tăng lên hàng chục hay hàng trăm chuỗi, pha tính ma trận khoảng cách O(k²N²) chiếm ưu thế tuyệt đối, giúp tỷ lệ song song hóa tiến dần tới 100%."
    ))

    # =========================================================================
    # SLIDE 12: THỰC NGHIỆM 1 — NÉN BỘ NHỚ RAM GOTOH VS MYERS-MILLER
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s12, "Phần 4 • Thực nghiệm BAliBASE 3.0 & Đối sánh",
        "Thực nghiệm 1: Kiểm chứng Nén Bộ nhớ Gotoh O(N²) vs. Myers-Miller O(N)",
        "Tiết kiệm tới 1.353,5× dung lượng RAM đỉnh và đạt độ trùng khớp điểm số tuyệt đối 100% trên mọi tập thử nghiệm",
        12
    )

    add_picture_fit(s12, RES_FIG_DIR / "fig1_memory_scaling.png", 0.45, 1.38, 6.75, 5.55)

    ct_s12 = add_card(s12, 7.38, 1.38, 5.50, 5.55, "Bảng Đối chứng Thực tế (--baseline-compare)", header_color=C_BLUE)
    headers_s12 = ["Bộ dữ liệu (Độ dài)", "Gotoh O(N²)", "Myers-Miller", "Giảm RAM", "Điểm số"]
    rows_s12 = [
        ["RV11 (85 aa)", "85,0 KB", "0,66 KB", "129,5×", "100% Match"],
        ["RV20 (74 aa)", "74,1 KB", "0,59 KB", "126,5×", "100% Match"],
        ["Hemoglobin (147 aa)", "248,6 KB", "1,12 KB", "222,5×", "100% Match"],
        ["RV12 (421 aa)", "2.395,3 KB", "3,30 KB", "726,5×", "100% Match"],
        ["Long Seq (897 aa)", "9.495,7 KB", "7,02 KB", "1.353,5×", "100% Match"],
    ]
    add_styled_table(s12, 7.54, ct_s12 + 0.08, 5.18, 2.75, headers_s12, rows_s12, col_widths=[1.42, 1.02, 1.02, 0.82, 0.90], font_size=9.5)

    add_bullets(s12, 7.54, 4.78, 5.18, 2.0, [
        ("• Kiểm chứng Thực nghiệm Khớp Lý thuyết:", "\nTỷ lệ nén bộ nhớ tăng tuyến tính theo độ dài chuỗi: từ 129,5× (ở 85 aa) vọt lên 1.353,5× (ở 897 aa), chứng minh hoàn hảo công thức O(N²)/O(N) = O(N).", C_BLUE),
        ("• Bảo toàn Điểm số Tối ưu 100%:", "\nĐiểm căn chỉnh của Myers-Miller và Gotoh NW bằng nhau tuyệt đối trên tất cả các cặp kiểm thử (ví dụ: 1aab_ vs 1j46_A đều đạt đúng 267 điểm).", C_GREEN),
    ], font_size=11.0, space_after=8)

    add_Notes(s12, (
        "Bước sang Phần 4 — Thực nghiệm trên bộ dữ liệu chuẩn quốc tế BAliBASE 3.0. "
        "Thực nghiệm đầu tiên kiểm chứng hiệu quả tiết kiệm bộ nhớ của Myers-Miller so với Gotoh truyền thống. "
        "Quan sát biểu đồ cột thang đo Logarit bên trái và bảng số liệu bên phải: với cặp chuỗi dài 897 amino acid, "
        "Gotoh cần gần 9,5 MB bộ nhớ cho 3 ma trận, trong khi Myers-Miller chỉ dùng đúng 7,02 KB — tức giảm 1.353,5 lần! "
        "Quan trọng hơn cả, cột ngoài cùng bên phải xác nhận điểm số quy hoạch động của hai thuật toán trùng khớp 100%."
    ))

    # =========================================================================
    # SLIDE 13: THỰC NGHIỆM 2 — HIỆU NĂNG TĂNG TỐC SONG SONG OPENMP
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s13, "Phần 4 • Thực nghiệm BAliBASE 3.0 & Đối sánh",
        "Thực nghiệm 2: Tốc độ Tăng tốc Song song Đa luồng OpenMP (Speedup)",
        "Đạt Speedup 1,73× trên họ gen lớn RV20 (BB20001) và 1,61× trên bộ 40 chuỗi (780 cặp), bám sát mô hình Amdahl",
        13
    )

    add_picture_fit(s13, RES_FIG_DIR / "fig2_speedup_scaling.png", 0.45, 1.38, 6.75, 5.55)

    ct_s13 = add_card(s13, 7.38, 1.38, 5.50, 5.55, "Phân tích Thực nghiệm Đa luồng (1, 2, 4, 8 Threads)", header_color=C_GREEN)
    headers_s13 = ["Bộ dữ liệu", "1 Thread", "2 Threads", "4 Threads", "8 Threads", "Max S(p)"]
    rows_s13 = [
        ["BB20001 (RV20)", "495,8 ms", "307,7 ms", "291,0 ms", "287,0 ms", "1,73×"],
        ["Bench 40 seqs", "5.423 ms", "5.093 ms", "3.660 ms", "3.360 ms", "1,61×"],
        ["BB12001 (RV12)", "612,9 ms", "485,1 ms", "540,5 ms", "874,4 ms", "1,26×"],
        ["BB11002 (RV11)", "23,2 ms", "18,9 ms", "18,7 ms", "19,1 ms", "1,24×"],
        ["BB11001 (4 seqs)", "5,14 ms", "4,52 ms", "5,26 ms", "5,97 ms", "1,14×"],
    ]
    add_styled_table(s13, 7.54, ct_s13 + 0.08, 5.18, 2.65, headers_s13, rows_s13, col_widths=[1.34, 0.80, 0.80, 0.80, 0.80, 0.64], font_size=9.2)

    add_bullets(s13, 7.54, 4.68, 5.18, 2.1, [
        ("1. Quy mô lớn (BB20001 & 40 chuỗi — 780 cặp):", "\nKhối lượng tính toán ma trận khoảng cách đủ lớn giúp phát huy tối đa sức mạnh đa nhân, giảm thời gian từ 5,42s xuống 3,36s (Speedup 1,61× – 1,73×).", C_GREEN),
        ("2. Quy mô siêu nhỏ (BB11001 — chỉ 4 chuỗi, 6 cặp, ~5 ms):", "\nĐạt đỉnh ở 2 luồng (1,14×); khi ép lên 8 luồng, chi phí đánh thức Thread Pool (Thread Overhead) lớn hơn thời gian tính toán thực tế.", C_AMBER),
        ("3. Bão hòa ở 8 luồng:", "\nDo nút thắt cổ chai tại nút gốc cây UPGMA và giới hạn băng thông bộ nhớ đệm L3 Cache khi truy cập mảng tần suất cột.", C_SLATE),
    ], font_size=10.5, space_after=6)

    add_Notes(s13, (
        "Ở Thực nghiệm 2, nhóm đo đạc thời gian chạy thực tế trên 1, 2, 4 và 8 luồng OpenMP. "
        "Kết quả cho thấy quy luật rất rõ ràng: với các tập dữ liệu lớn có hàng trăm cặp chuỗi như BB20001 hay Benchmark 40 chuỗi (780 cặp), "
        "thời gian giảm mạnh và đạt Speedup cực đại 1,73 lần. "
        "Ngược lại, với tập dữ liệu rất nhỏ như BB11001 chỉ có 4 chuỗi (chạy mất 5 mili-giây), việc dùng tới 8 luồng chỉ làm tốn thêm chi phí đồng bộ rào chắn OpenMP. "
        "Sự tiệm cận của đường thực nghiệm so với đường lý thuyết Amdahl phản ánh chính xác phần tuần tự tại nút gốc của cây UPGMA."
    ))

    # =========================================================================
    # SLIDE 14: THỰC NGHIỆM 3 — ĐỘ CHÍNH XÁC SINH HỌC TRÊN BALIBASE 3.0
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s14, "Phần 4 • Thực nghiệm BAliBASE 3.0 & Đối sánh",
        "Thực nghiệm 3: Đánh giá Độ chính xác Sinh học (SP & TC Score) trên BAliBASE 3.0",
        "Đạt độ chính xác xuất sắc trên tập RV12 (SP trung bình = 86,8%, TC = 68,1%) và lên tới 98,2% SP trên mẫu BB11001",
        14
    )

    add_picture_fit(s14, RES_FIG_DIR / "fig3_balibase_accuracy.png", 0.45, 1.38, 6.55, 5.55)

    ct_s14 = add_card(s14, 7.18, 1.38, 5.70, 5.55, "Kết quả Chấm điểm Đối chiếu Cấu trúc 3D Chuẩn", header_color=C_PURPLE)
    headers_s14 = ["Phân vùng BAliBASE 3.0", "Đặc trưng Sinh học", "SP Score", "TC Score", "Mẫu Đỉnh (Peak)"]
    rows_s14 = [
        ["RV11 (BB11001–11005)", "Rất phân kỳ (<20% ID)", "0,5311", "0,2941", "BB11001 (SP: 98,2%)"],
        ["RV12 (BB12001–12005)", "Tương đồng vừa (20–40%)", "0,8684", "0,6806", "BB12003 (SP: 93,0%)"],
        ["RV20 (BB20001–20003)", "Họ gen lớn (16–40 seqs)", "0,5556", "0,0000", "BB20003 (SP: 92,0%)"],
    ]
    add_styled_table(s14, 7.34, ct_s14 + 0.08, 5.38, 2.05, headers_s14, rows_s14, col_widths=[1.35, 1.35, 0.72, 0.72, 1.24], font_size=9.5)

    add_bullets(s14, 7.34, 4.08, 5.38, 2.75, [
        ("• Hai Thước đo Chuẩn Quốc tế (Thompson et al.):", "\n- SP Score (Sum-of-Pairs): Tỷ lệ cặp ký tự căn chỉnh trùng khớp với file chuẩn MSF.\n- TC Score (Total Column): Tỷ lệ cột căn chỉnh đúng tuyệt đối 100% trên mọi chuỗi.", C_NAVY),
        ("• Điểm sáng trên RV12 (Medium Identity):", "\nTrên cả 5 bộ mẫu từ BB12001 đến BB12005, điểm SP đều vượt ngưỡng 83% – 93%, chứng tỏ mô hình BLOSUM62 + Affine Gap (-10, -1) hoạt động rất chính xác.", C_GREEN),
        ("• Phân tích thẳng thắn Hạn chế trên RV20 (TC = 0):", "\nChỉ cần 1 chuỗi ngoại lai lệch 1 vị trí gap trong 40 chuỗi sẽ làm điểm TC của cột đó về 0 (hạn chế chung của Progressive MSA thuần túy chưa có Iterative Refinement).", C_AMBER),
    ], font_size=10.5, space_after=6)

    add_Notes(s14, (
        "Thực nghiệm thứ 3 kiểm tra chất lượng sinh học của kết quả căn chỉnh bằng cách so sánh tự động với các file chuẩn BAliBASE 3.0 "
        "được xác thực bằng cấu trúc tinh thể học tia X. "
        "Trên nhóm RV12 (độ tương đồng trung bình 20-40%), thuật toán đạt kết quả rất cao với SP trung bình 86,84% và TC đạt 68,06%. "
        "Trên nhóm khó nhất là RV11 (Vùng hoàng hôn dưới 20% tương đồng), mẫu BB11001 vẫn đạt tới 98,2% điểm SP. "
        "Nhóm cũng phân tích rõ tại sao trên RV20 điểm SP đạt tới 92% (BB20003) nhưng điểm TC bằng 0: vì TC đòi hỏi cả 40 chuỗi trong cột phải đúng đồng thời 100%, "
        "nên chỉ cần 1 chuỗi bị dịch nhẹ ở bước sớm theo luật 'Once a gap, always a gap' là cột đó mất điểm TC."
    ))

    # =========================================================================
    # SLIDE 15: THỰC NGHIỆM 4 — ĐỐI SÁNH VỚI CLUSTALW 2.1 & MUSCLE V3.8
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s15, "Phần 4 • Thực nghiệm BAliBASE 3.0 & Đối sánh",
        "Thực nghiệm 4: Đối sánh với Công cụ Quốc tế (ClustalW 2.1 & MUSCLE v3.8)",
        "Tiêu thụ RAM đỉnh thấp nhất (giảm ~45% so với ClustalW/MUSCLE) trong khi đạt điểm SP vượt ClustalW trên BB20001",
        15
    )

    add_picture_fit(s15, RES_FIG_DIR / "fig4_tools_comparison.png", 0.45, 1.38, 7.55, 5.55)

    ct_s15 = add_card(s15, 8.18, 1.38, 4.70, 5.55, "Tổng hợp Đối sánh Đa công cụ (BB20001)", header_color=C_NAVY)
    headers_s15 = ["Công cụ MSA", "Peak RAM", "SP Score", "Đặc điểm"]
    rows_s15 = [
        ["Gotoh DP Baseline", "320,0 MB", "0,488", "Bậc hai O(N²)"],
        ["ClustalW 2.1", "48,5 MB", "0,472", "Kinh điển, 1 luồng"],
        ["MUSCLE v3.8", "52,0 MB", "0,495", "Có lọc lặp (Iterative)"],
        ["Nhóm 5 (Đề xuất)", "26,8 MB", "0,488", "Tối ưu RAM + Đa luồng"],
    ]
    add_styled_table(s15, 8.34, ct_s15 + 0.08, 4.38, 2.25, headers_s15, rows_s15, col_widths=[1.38, 0.92, 0.82, 1.26], font_size=9.5)

    add_bullets(s15, 8.34, 4.25, 4.38, 2.5, [
        ("• Ưu thế Tuyệt đối về Bộ nhớ (26,8 MB):", "\nNhờ cơ chế cấp phát và thu hồi tức thời 6 vector 1 chiều trong Myers-Miller, hệ thống tốn ít RAM hơn gần một nửa so với ClustalW (48,5 MB) và MUSCLE (52,0 MB).", C_GREEN),
        ("• Cạnh tranh Sòng phẳng về Độ chính xác:", "\nĐạt SP = 0,488 — cao hơn ClustalW 2.1 (0,472) và chỉ thấp hơn nhẹ so với MUSCLE v3.8 (0,495) vốn thực hiện thêm nhiều vòng cắt cây tinh chỉnh lặp.", C_BLUE),
    ], font_size=10.8, space_after=8)

    add_Notes(s15, (
        "Khi đặt hệ thống của Nhóm 5 cạnh hai phần mềm sinh tin học tiêu chuẩn quốc tế là ClustalW 2.1 và MUSCLE v3.8 trên bộ dữ liệu BB20001: "
        "Hình A bên trái cho thấy hệ thống của nhóm có mức tiêu thụ bộ nhớ RAM đỉnh thấp nhất — chỉ 26,8 MB so với ~50 MB của ClustalW/MUSCLE và 320 MB của Gotoh. "
        "Hình B bên phải cho thấy điểm SP của nhóm đạt 0,488 — vượt qua ClustalW (0,472) và tiệm cận rất sát MUSCLE (0,495)."
    ))

    # =========================================================================
    # SLIDE 16: KIẾN TRÚC PHẦN MỀM C++17 & KIỂM THỬ TỰ ĐỘNG
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s16, "Phần 5 • Hệ thống Phần mềm, Demo & Kết luận",
        "Kiến trúc Phần mềm Modern C++17 & Kiểm thử Tự động Nghiêm ngặt",
        "Thiết kế hướng module không phụ thuộc thư viện ngoài, vượt qua 342 bài kiểm thử tự động (139.463 assertions)",
        16
    )

    # Top 3 Big Stat Cards
    stat_cards = [
        ("108 / 108 PASS", "Unit Tests (139.463 Assertions)", "Kiểm tra đối xứng BLOSUM62, đối chiếu 25 cặp ngẫu nhiên NW vs Hirschberg, chia tải MPI, cây UPGMA.", C_BLUE, C_BLUE_BG),
        ("234 / 234 PASS", "End-to-End Integration Tests", "Kiểm thử toàn diện 4 giai đoạn từ đọc FASTA/MSF, xuất cây Newick (.nwk) đến chấm điểm SP/TC BAliBASE.", C_GREEN, C_GREEN_BG),
        ("100% INVARIANT", "Bảo toàn Chuỗi Sinh học", "Đảm bảo toán học: loại bỏ ký tự '-' sau khi căn chỉnh luôn khôi phục chính xác 100% chuỗi Amino Acid gốc.", C_PURPLE, C_PURPLE_BG),
    ]
    for i, (headline, sub, desc, col, bg) in enumerate(stat_cards):
        x = 0.45 + i * 4.18
        ct = add_card(s16, x, 1.38, 4.02, 2.25, sub, bg_color=bg, border_color=col, header_color=col)
        tb = s16.shapes.add_textbox(Inches(x + 0.16), Inches(ct + 0.02), Inches(3.70), Inches(1.6))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = headline
        p1.font.name = FONT_MAIN
        p1.font.size = Pt(22)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.space_after = Pt(4)
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_MAIN
        p2.font.size = Pt(10.8)
        p2.font.color.rgb = C_SLATE

    # Bottom Card: 6 C++17 Modules & CLI Modes
    ct_m = add_card(s16, 0.45, 3.82, 12.43, 3.12, "Cấu trúc 6 Module C++17 (include/msa/) & Các Chế độ Thực thi CLI", header_color=C_NAVY)
    add_bullets(s16, 0.65, ct_m + 0.08, 6.0, 2.3, [
        ("• msa::core: ", "Sequence, Profile (tần suất cột), bảng BLOSUM62 tĩnh O(1), ScoreModel."),
        ("• msa::align: ", "NeedlemanWunschGotoh (3 ma trận), MyersMillerHirschberg (1D vector), ProfileAligner."),
        ("• msa::tree: ", "DistanceMatrix tam giác trên, UPGMA Clustering, GuideTree & xuất Newick/JSON."),
        ("• msa::parallel: ", "Wavefront Anti-Diagonal OpenMP DP, Level-Set TreeScheduler, Hybrid MPI."),
        ("• msa::eval & msa::io: ", "BAliBASE MSF/FASTA Parser, chấm điểm SP/TC, MemoryTracker, CLI Parser.")
    ], font_size=11.0, space_after=6)

    add_formula_box(s16, 6.85, ct_m + 0.08, 5.83, 2.35, "Các Chế độ Dòng lệnh (CLI Executables: msa_align & msa_align_mpi):", [
        "# 1. Căn chỉnh đa luồng + Chấm điểm chuẩn BAliBASE:",
        "./msa_align -i data/balibase/BB12001.msf --ref BB12001.msf -t 4",
        "# 2. Đối chứng trực tiếp Gotoh NW vs. Myers-Miller:",
        "./msa_align -i data/balibase/BB11001.msf --baseline-compare",
        "# 3. Chạy Hybrid MPI + OpenMP trên cụm máy tính:",
        "mpirun -np 2 -x OMP_NUM_THREADS=4 ./msa_align_mpi -i input.fa -t 4"
    ], bg_color=RGBColor(241, 245, 249), border_color=C_SLATE)

    add_Notes(s16, (
        "Về mặt kỹ thuật phần mềm, toàn bộ hệ thống được viết bằng C++17 hiện đại, chia thành 6 namespace rõ ràng "
        "và biên dịch ra 2 thực thi độc lập: msa_align (OpenMP) và msa_align_mpi (Hybrid MPI + OpenMP). "
        "Để đảm bảo độ tin cậy tuyệt đối của thuật toán chia để trị phức tạp, nhóm đã xây dựng 108 Unit Tests với 139.463 phép kiểm tra assertion "
        "và 234 bài kiểm thử tích hợp End-to-End, đạt tỷ lệ vượt qua 100%."
    ))

    # =========================================================================
    # SLIDE 17: GIAO DIỆN WEB GUI STUDIO & KỊCH BẢN LIVE DEMO (2 PHÚT)
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s17, "Phần 5 • Hệ thống Phần mềm, Demo & Kết luận",
        "Giao diện Web GUI Studio & Kịch bản Trình diễn Thực tế (Live Demo)",
        "Trực quan hóa Ma trận Màu Hóa học ClustalX, Cây Phát sinh UPGMA SVG và Bảng Điều khiển Benchmark Thời gian thực",
        17
    )

    # Bento Grid of 3 Web Screenshots on Left/Center
    add_picture_fit(s17, DOCS_IMG_DIR / "fig_5_1_web_alignment_matrix.png", 0.45, 1.38, 7.65, 2.85)
    add_picture_fit(s17, DOCS_IMG_DIR / "fig_5_2_web_guide_tree.png", 0.45, 4.35, 3.75, 2.58)
    add_picture_fit(s17, DOCS_IMG_DIR / "fig_5_3_web_benchmark_dashboard.png", 4.35, 4.35, 3.75, 2.58)

    # Right Demo Script Card
    ct_s17 = add_card(s17, 8.28, 1.38, 4.60, 5.55, "Kịch bản Live Demo (90 – 120 Giây)", header_color=C_BLUE)
    add_bullets(s17, 8.45, ct_s17 + 0.08, 4.26, 4.9, [
        ("Bước 1 — Khởi chạy & Chọn Preset (30s):", "\n• Mở http://localhost:8000 (FastAPI + C++17 IPC).\n• Chọn preset BAliBASE RV12 (BB12001.msf) hoặc Hemoglobin.\n• Bật Baseline Comparison + Multi-thread Benchmark (1→8 luồng), nhấn Run Alignment.", C_BLUE),
        ("Bước 2 — Phân tích Sinh học Trực quan (40s):", "\n• Quan sát Ma trận màu Amino Acid chuẩn Jalview/ClustalX (Kỵ nước: Xanh lam, Điện tích dương: Đỏ, Âm: Tím) & biểu đồ cột Conservation.\n• Chuyển sang tab UPGMA Guide Tree: tương tác phóng to/thu nhỏ cây SVG và xuất file Newick.", C_GREEN),
        ("Bước 3 — Kiểm chứng Hiệu năng (30s):", "\n• Mở tab Benchmark Dashboard: đối chiếu thẻ tiết kiệm RAM (>700×), điểm SP/TC tự động và đồ thị Speedup.", C_PURPLE),
    ], font_size=10.8, space_after=8)

    add_Notes(s17, (
        "Bên cạnh công cụ dòng lệnh CLI, nhóm phát triển giao diện Web GUI Studio kết nối trực tiếp tới nhân C++17 qua FastAPI. "
        "Trên màn hình là 3 phân hệ trực quan hóa chính: (1) Ma trận căn chỉnh tô màu theo tính chất hóa lý của từng amino acid kèm biểu đồ mức độ bảo tồn cột; "
        "(2) Cây phát sinh chủng loại UPGMA dạng đồ họa vector SVG tương tác; và (3) Dashboard đo đạc Speedup đa luồng và tỷ lệ nén bộ nhớ theo thời gian thực. "
        "Sau đây nhóm xin phép chuyển sang trình duyệt trong khoảng 1 phút rưỡi để demo trực tiếp trên bộ dữ liệu chuẩn BAliBASE."
    ))

    # =========================================================================
    # SLIDE 18: KẾT LUẬN, ĐÓNG GÓP KHOA HỌC & HƯỚNG PHÁT TRIỂN
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        s18, "Phần 5 • Hệ thống Phần mềm, Demo & Kết luận",
        "Kết luận, Đóng góp Khoa học & Hướng Phát triển Mở rộng",
        "Giải quyết trọn vẹn bài toán MSA với bộ nhớ tối ưu O(k · L), tốc độ đa luồng cao và kiểm chứng chuẩn quốc tế",
        18
    )

    ct_s18_l = add_card(s18, 0.45, 1.38, 6.25, 4.85, "1. Tổng kết 4 Đóng góp Cốt lõi của Đồ án", header_color=C_GREEN)
    add_bullets(s18, 0.65, ct_s18_l + 0.08, 5.85, 4.1, [
        ("① Đột phá Bộ nhớ Tuyến tính O(min(m, n)):", "\nThiết kế và cài đặt hoàn chỉnh thuật toán Chia để trị Myers-Miller kết hợp Profile-to-Profile, giảm bộ nhớ tới 1.353,5× so với Gotoh NW và đạt điểm số trùng khớp 100%.", C_GREEN),
        ("② Kiến trúc Song song Đa tầng (OpenMP + MPI):", "\nKhai thác đồng thời song song cặp khoảng cách, lập lịch cây Level-Set và đường chéo Wavefront, đạt Speedup 1,73× trên CPU đa nhân.", C_BLUE),
        ("③ Thực nghiệm Chuẩn Quốc tế BAliBASE 3.0:", "\nĐạt độ chính xác sinh học SP = 86,8% trên RV12, tiêu thụ RAM thấp hơn ~45% so với ClustalW 2.1 và MUSCLE v3.8.", C_PURPLE),
        ("④ Hệ thống C++17 Chuẩn Công nghiệp & Web Studio:", "\n342 bài kiểm thử tự động (100% Pass) cùng giao diện trực quan hóa sinh học toàn diện.", C_NAVY),
    ], font_size=11.0, space_after=8)

    ct_s18_r = add_card(s18, 6.90, 1.38, 5.98, 4.85, "2. Hướng Phát triển Mở rộng Tiếp theo", header_color=C_NAVY)
    add_bullets(s18, 7.10, ct_s18_r + 0.08, 5.58, 4.1, [
        ("• Bổ sung Pha Tinh chỉnh Lặp (Iterative Refinement):", "\nCắt ngẫu nhiên các nhánh cây UPGMA và căn chỉnh lại Profile (Tree-dependent Restricted Partitioning kiểu MUSCLE/MAFFT) để khắc phục lỗi 'Once a gap, always a gap' và nâng cao điểm TC trên RV20.", C_AMBER),
        ("• Tăng tốc Phần cứng Vector hóa SIMD (AVX-512) & GPU CUDA:", "\nVector hóa phép nhân tích vô hướng tần suất cột PSP(x,y) và đẩy mặt sóng Wavefront lên hàng nghìn nhân GPU.", C_BLUE),
        ("• Hàm Điểm Thích nghi Đa Ma trận (Adaptive Scoring):", "\nTự động chuyển đổi ma trận BLOSUM80 / BLOSUM62 / BLOSUM45 dựa trên độ sâu nhánh cây UPGMA.", C_PURPLE),
    ], font_size=11.0, space_after=10)

    # Thank you banner at bottom
    ty = s18.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.45), Inches(6.35), Inches(12.43), Inches(0.68))
    ty.fill.solid()
    ty.fill.fore_color.rgb = C_NAVY
    ty.line.color.rgb = C_BLUE
    ty.line.width = Pt(1.5)
    typ = ty.text_frame.paragraphs[0]
    typ.text = "CẢM ƠN THẦY/CÔ VÀ CÁC BẠN ĐÃ LẮNG NGHE!  •  NHÓM 5 XIN TRÂN TRỌNG ĐÓN NHẬN CÂU HỎI PHẢN BIỆN"
    typ.font.name = FONT_MAIN
    typ.font.size = Pt(13.5)
    typ.font.bold = True
    typ.font.color.rgb = C_WHITE
    typ.alignment = PP_ALIGN.CENTER

    add_Notes(s18, (
        "Để kết luận, đồ án của Nhóm 5 đã giải quyết trọn vẹn bài toán Căn chỉnh Đa chuỗi từ nền tảng lý thuyết, chứng minh độ phức tạp toán học "
        "đến cài đặt hệ thống C++17 song song và kiểm chứng trên chuẩn quốc tế BAliBASE 3.0. "
        "Trong tương lai, việc tích hợp thêm vòng lặp tinh chỉnh Iterative Refinement trên nền tảng bộ nhớ tuyến tính sẵn có của nhóm "
        "sẽ giúp nâng cao hơn nữa điểm số TC trên các họ gen lớn. Cảm ơn Thầy/Cô và các bạn đã lắng nghe, nhóm rất mong nhận được các câu hỏi phản biện ạ!"
    ))

    # =========================================================================
    # BACKUP SLIDE B1: GAP COALESCING TRONG MYERS-MILLER
    # =========================================================================
    sb1 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        sb1, "Phụ lục Phản biện • Backup Q&A #1",
        "[Q&A Lý thuyết] Xử lý Khoảng trống Xuyên qua Nhát cắt Giữa (Gap Coalescing)",
        "Tại sao chia đôi ma trận tại dòng i* = ⌊m/2⌋ không làm phạt mở khoảng trống G_open hai lần?",
        "B1 / 3"
    )

    ct_b1 = add_card(sb1, 0.45, 1.38, 12.43, 5.55, "Câu hỏi: Nếu đường căn chỉnh tối ưu đi qua một khoảng trống kéo dài xuyên qua dòng i*, thuật toán xử lý thế nào?", header_color=C_NAVY)
    add_formula_box(sb1, 0.65, ct_b1 + 0.12, 12.03, 2.05, "Phương trình Khớp Trạng thái tại Ranh giới Chia cắt i* = ⌊m/2⌋:", [
        "Score(j) = max {",
        "   ① Khớp / Thay thế qua ranh giới:      Fwd_M(j)  + Bwd_M(j),",
        "   ② Khoảng trống xuyên qua ranh giới:   Fwd_Ix(j) + Bwd_Ix(j) - G_open + G_ext",
        "}"
    ], bg_color=C_BLUE_BG, border_color=C_BLUE)

    add_bullets(sb1, 0.65, 4.18, 12.03, 2.5, [
        ("• Bản chất Toán học của Hiệu chỉnh (-G_open + G_ext):", "\nMột khoảng trống độ dài g = g₁ + g₂ (với g₁ ở nửa trên, g₂ ở nửa dưới) có chi phí thực tế là: G_open + (g₁ + g₂ - 1)·G_ext.\nTuy nhiên, tổng Fwd_Ix(j) + Bwd_Ix(j) đã tính: [G_open + (g₁ - 1)·G_ext] + [G_open + (g₂ - 1)·G_ext] = 2·G_open + (g₁ + g₂ - 2)·G_ext.\nDo đó, ta phải TRỪ đi 1 lần G_open và CỘNG bù 1 lần G_ext để hợp nhất (coalesce) hai nửa thành đúng 1 khoảng trống liên tục!", C_RED),
        ("• Truyền Cờ Biên Đệ quy (Boundary State Flags: tb_top, tb_bottom):", "\nKhi trường hợp ② đạt cực đại tại cột j*, lời gọi đệ quy truyền cờ ép bài toán con nửa trên phải kết thúc ở trạng thái Ix và bài toán con nửa dưới phải bắt đầu từ trạng thái Ix.", C_NAVY)
    ], font_size=11.5, space_after=10)

    add_Notes(sb1, (
        "Slide dự phòng giải thích chi tiết kỹ thuật Gap Coalescing trong bài báo gốc của Myers & Miller (1988) khi hội đồng hỏi sâu về cách nối 2 nửa quy hoạch động có phạt khoảng trống Affine."
    ))

    # =========================================================================
    # BACKUP SLIDE B2: TẠI SAO TC SCORE = 0 TRÊN RV20 DÙ SP SCORE CAO?
    # =========================================================================
    sb2 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        sb2, "Phụ lục Phản biện • Backup Q&A #2",
        "[Q&A Thực nghiệm] Tại sao TC Score trên RV20 bằng 0 dù SP Score đạt tới 92%?",
        "Phân tích sự khác biệt toán học giữa thước đo SP Score vs. TC Score và đặc trưng của Progressive MSA",
        "B2 / 3"
    )

    ct_b2 = add_card(sb2, 0.45, 1.38, 12.43, 5.55, "Câu hỏi: Trên tập BB20003 (RV20), tại sao SP Score đạt 0,920 (92%) nhưng TC Score lại bằng 0,000?", header_color=C_PURPLE)
    add_formula_box(sb2, 0.65, ct_b2 + 0.12, 12.03, 1.85, "So sánh Công thức Toán học của SP Score và TC Score:", [
        "• SP Score = (Tổng số cặp ký tự căn chỉnh đúng trong mọi cột Core Block) / (Tổng số cặp trong chuẩn Reference)",
        "• TC Score = (Số lượng cột mà TẤT CẢ 100% chuỗi đều khớp hoàn hảo) / (Tổng số cột Core Block chuẩn)",
        "  ⇒ Chỉ cần 1 chuỗi duy nhất (trong số 30–40 chuỗi của RV20) bị lệch đi 1 vị trí gap → Cả cột đó nhận TC = 0!"
    ], bg_color=C_PURPLE_BG, border_color=C_PURPLE)

    add_bullets(sb2, 0.65, 3.98, 12.03, 2.7, [
        ("1. Đặc trưng của Phân vùng BAliBASE RV20 (Families with Orphan Sequences):", "\nRV20 chứa một họ lớn các chuỗi rất giống nhau kèm theo một vài chuỗi 'mồ côi' (orphan sequences) cực kỳ phân kỳ. Hệ thống của nhóm đã căn chỉnh đúng tuyệt đối nhóm chuỗi chính (nên tổng số cặp đúng SP đạt tới 92,0%), nhưng chuỗi ngoại lai cuối cùng ghép vào gốc cây bị lệch pha vài cột.", C_GREEN),
        ("2. Nguyên lý 'Once a gap, always a gap' của Progressive Alignment thuần túy:", "\nPhương pháp tiến bộ một lượt (Single-pass Progressive) không quay lui để sửa lại vị trí gap sau khi đã hợp nhất. Đây là lý do các công cụ như ClustalW cũng thường có TC thấp trên RV20 nếu không có pha hậu xử lý Iterative Refinement.", C_AMBER)
    ], font_size=11.5, space_after=10)

    add_Notes(sb2, (
        "Slide dự phòng giải thích lý do điểm TC bằng 0 trên tập RV20 dù điểm SP đạt 92%."
    ))

    # =========================================================================
    # BACKUP SLIDE B3: PHÂN TÍCH NÚT THẮT ĐỒNG BỘ HÓA & BĂNG THÔNG Ở 8 LUỒNG
    # =========================================================================
    sb3 = prs.slides.add_slide(blank_layout)
    add_header_footer(
        sb3, "Phụ lục Phản biện • Backup Q&A #3",
        "[Q&A Song song hóa] Phân tích Hiện tượng Bão hòa Speedup ở 8 Luồng OpenMP",
        "Giải thích bằng Hình thái Cây UPGMA (Tree Topology) và Băng thông Bộ nhớ Đệm (Memory Bandwidth)",
        "B3 / 3"
    )

    ct_b3 = add_card(sb3, 0.45, 1.38, 12.43, 5.55, "Câu hỏi: Tại sao khi tăng từ 4 lên 8 luồng OpenMP, Speedup bão hòa quanh mức 1,61× – 1,73×?", header_color=C_AMBER)
    add_bullets(sb3, 0.65, ct_b3 + 0.15, 12.03, 5.0, [
        ("1. Nút thắt Hình thái Cây Nhị phân ở các Mức Trên cùng (Root-Level Serialization):", "\n• Ở Giai đoạn 4, cây hướng dẫn UPGMA thu hẹp dần khi đi từ lá lên gốc: ở tầng sát gốc chỉ còn 2 nút con, và ở tầng gốc chỉ còn đúng 1 nút.\n• Nghịch lý khối lượng: Nút gốc lại chứa nhiều chuỗi nhất (|P₁|×|P₂| lớn nhất), chiếm ~15%–20% tổng thời gian nhưng chỉ có 1 luồng thực thi phép chia để trị Myers-Miller tại nút đó, trong khi 7 luồng còn lại nghỉ chờ.", C_RED),
        ("2. Đặc tính Giới hạn Băng thông Bộ nhớ (Memory-Bound Kernel):", "\n• Phép tính điểm cột PSP(x, y) đọc liên tục vector tần suất 20 phần tử từ bộ nhớ với tỷ lệ phép tính số học trên mỗi byte đọc từ RAM thấp (Low Arithmetic Intensity).\n• Khi 8 luồng cùng quét tốc độ cao trên 1 CPU, băng thông bộ nhớ đệm L3 Cache đạt ngưỡng bão hòa.", C_BLUE),
        ("3. Giải pháp Đã Thiết kế Sẵn cho Quy mô Lớn:", "\n• Kết hợp song song nội bộ ma trận (Wavefront Anti-Diagonal) cho chính nút gốc của cây UPGMA khi chiều dài Profile L ≥ 2.000.", C_GREEN)
    ], font_size=11.5, space_after=12)

    add_Notes(sb3, (
        "Slide dự phòng phân tích nguyên nhân kiến trúc máy tính và hình thái cây nhị phân dẫn tới ngưỡng bão hòa Speedup ở 8 luồng."
    ))

    prs.save(str(OUTPUT_PPTX))
    print(f"[SUCCESS] Generated presentation deck: {OUTPUT_PPTX} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build_presentation()
