#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds Version 2 of Group 5 MSA Presentation on BOTH:
  1. Google Slides (via gslides CLI batch + insert-image-from-file)
  2. Local PowerPoint file: Slide_Thuyet_Trinh_PTTKTT_Nhom_5_MSA_v2.pptx

Key Improvements in v2 based on User Feedback & gslides Styling Guide:
  - Dedicated 3-slide Biological & Problem Formulation intro ("Cho cái gì? Yêu cầu làm cái gì?",
    DNA/Protein, Substitution vs Indel mutations, why '-' gaps, why BLOSUM62 & Affine Gap -10/-1).
  - Full-Bleed (85-90% slide area) dedicated visual slides for all diagrams, benchmark charts,
    and Web GUI screenshots so every figure is huge and crystal-clear from afar.
  - Sandwich Dark (#1E2761) -> Light (#F8FAFC) -> Dark (#1E2761) visual rhythm.
"""

import json
import subprocess
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
BATCH_JSON_PATH = ROOT_DIR / "scripts" / "gslides_batch_v2.json"
OUTPUT_PPTX_V2 = ROOT_DIR / "Slide_Thuyet_Trinh_PTTKTT_Nhom_5_MSA_v2.pptx"
GSLIDES_CMD = r"C:\Users\manhk\.gemini\config\plugins\gslides\skills\gslides\scripts\gslides.cmd"
PRES_ID = "1hyApzYpnj-BbdNEk98pTbxLC8Vy3yRR0_qr9GLVxx5E"


def fit_box(img_path, box_x, box_y, max_w, max_h):
    """Returns (x, y, w, h) preserving exact aspect ratio of img_path inside bounding box."""
    with Image.open(img_path) as im:
        w_px, h_px = im.size
    aspect = w_px / float(h_px)
    box_aspect = max_w / float(max_h)
    if aspect >= box_aspect:
        w = max_w
        h = max_w / aspect
    else:
        h = max_h
        w = max_h * aspect
    x = box_x + (max_w - w) / 2.0
    y = box_y + (max_h - h) / 2.0
    return round(x, 1), round(y, 1), round(w, 1), round(h, 1)


# ==============================================================================
# PART 1: GENERATE GOOGLE SLIDES BATCH JSON (720 x 405 pt canvas)
# ==============================================================================
def generate_gslides_batch():
    ops = []
    image_uploads = []  # List of (slide_placeholder_id, img_path, x, y, w, h)

    # Remove default placeholders on initial slide 'p'
    ops.append({"op": "delete-element", "element": "i0"})
    ops.append({"op": "delete-element", "element": "i1"})

    def add_top_bar(s_id, badge_text, title_text, subtitle_text, slide_no, dark_mode=False):
        bg_col = "#1E2761" if dark_mode else "#F4F6FB"
        ops.append({"op": "set-background", "slide": s_id, "color": bg_col})
        # Header banner
        ops.append({
            "op": "add-shape", "slide": s_id, "shape_type": "RECTANGLE",
            "x": 0, "y": 0, "width": 720, "height": 58,
            "background_color": "#0F172A"
        })
        ops.append({
            "op": "add-shape", "slide": s_id, "shape_type": "RECTANGLE",
            "x": 0, "y": 56, "width": 720, "height": 3,
            "background_color": "#0284C7"
        })
        # Badge
        ops.append({
            "op": "add-textbox", "slide": s_id, "text": badge_text,
            "x": 24, "y": 6, "width": 195, "height": 16,
            "font_size": 8, "bold": True, "color": "#FFFFFF",
            "background_color": "#0284C7", "font_family": "Roboto",
            "alignment": "center", "content_alignment": "MIDDLE"
        })
        # Slide number in top right
        ops.append({
            "op": "add-textbox", "slide": s_id, "text": f"Slide {slide_no}",
            "x": 630, "y": 6, "width": 66, "height": 16,
            "font_size": 8.5, "bold": True, "color": "#93C5FD",
            "font_family": "Roboto", "alignment": "right", "content_alignment": "MIDDLE"
        })
        # Main Title
        ops.append({
            "op": "add-textbox", "slide": s_id, "text": title_text,
            "x": 24, "y": 22, "width": 672, "height": 22,
            "font_size": 15, "bold": True, "color": "#FFFFFF",
            "font_family": "Roboto"
        })
        # Subtitle
        if subtitle_text:
            ops.append({
                "op": "add-textbox", "slide": s_id, "text": subtitle_text,
                "x": 24, "y": 41, "width": 672, "height": 15,
                "font_size": 9, "italic": True, "color": "#BAE6FD",
                "font_family": "Roboto"
            })

    def add_card_gslides(s_id, x, y, w, h, header_title, body_text, hdr_bg="#1E2761", body_bg="#FFFFFF", body_color="#1E293B", font_size=10.5, mono=False):
        # Header box
        hdr_h = 24
        ops.append({
            "op": "add-textbox", "slide": s_id, "text": header_title,
            "x": x, "y": y, "width": w, "height": hdr_h,
            "font_size": 10.5, "bold": True, "color": "#FFFFFF",
            "background_color": hdr_bg, "font_family": "Roboto",
            "content_alignment": "MIDDLE"
        })
        # Body box
        ops.append({
            "op": "add-textbox", "slide": s_id, "text": body_text,
            "x": x, "y": y + hdr_h, "width": w, "height": h - hdr_h,
            "font_size": font_size, "bold": mono, "color": body_color,
            "background_color": body_bg,
            "font_family": "Roboto Mono" if mono else "Roboto",
            "line_spacing": 125, "content_alignment": "TOP"
        })

    def add_full_bleed_image_slide(s_id, badge, title, subtitle, slide_no, img_path, bottom_takeaway, notes, bg_dark=False):
        add_top_bar(s_id, badge, title, subtitle, slide_no, dark_mode=bg_dark)
        # White frame for image
        ops.append({
            "op": "add-shape", "slide": s_id, "shape_type": "RECTANGLE",
            "x": 20, "y": 64, "width": 680, "height": 302,
            "background_color": "#FFFFFF"
        })
        ix, iy, iw, ih = fit_box(img_path, 24, 67, 672, 296)
        image_uploads.append((s_id, str(img_path), ix, iy, iw, ih))
        # Bottom Takeaway Callout Bar
        ops.append({
            "op": "add-textbox", "slide": s_id, "text": bottom_takeaway,
            "x": 20, "y": 370, "width": 680, "height": 28,
            "font_size": 10, "bold": True, "color": "#FFFFFF",
            "background_color": "#0F172A", "font_family": "Roboto",
            "content_alignment": "MIDDLE"
        })
        ops.append({"op": "set-notes", "slide": s_id, "text": notes})

    # --------------------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE (on default slide 'p')
    # --------------------------------------------------------------------------
    ops.append({"op": "set-background", "slide": "p", "color": "#0F172A"})
    ops.append({"op": "add-shape", "slide": "p", "shape_type": "RECTANGLE", "x": 0, "y": 0, "width": 720, "height": 6, "background_color": "#0284C7"})
    ops.append({
        "op": "add-textbox", "slide": "p",
        "text": "BÁO CÁO ĐỒ ÁN • MÔN PHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN",
        "x": 40, "y": 28, "width": 360, "height": 24,
        "font_size": 10, "bold": True, "color": "#FFFFFF",
        "background_color": "#0284C7", "font_family": "Roboto",
        "alignment": "center", "content_alignment": "MIDDLE"
    })
    ops.append({
        "op": "add-textbox", "slide": "p",
        "text": "THUẬT TOÁN CHIA ĐỂ TRỊ SONG SONG KẾT HỢP QUY HOẠCH ĐỘNG CHO CĂN CHỈNH ĐA CHUỖI PROTEIN/ADN (MSA)",
        "x": 40, "y": 64, "width": 640, "height": 115,
        "font_size": 24, "bold": True, "color": "#FFFFFF", "font_family": "Roboto",
        "line_spacing": 115
    })
    ops.append({
        "op": "add-textbox", "slide": "p",
        "text": "Tối ưu Bộ nhớ Tuyến tính O(min(m,n)) bằng Myers-Miller • Cây Hướng dẫn UPGMA • Song song Đa tầng OpenMP & MPI",
        "x": 40, "y": 184, "width": 640, "height": 30,
        "font_size": 12, "color": "#7DD3FC", "font_family": "Roboto"
    })
    # 4 Big Stat Cards on Slide 1
    s1_stats = [
        ("1.353,5×", "Giảm bộ nhớ RAM đỉnh\nO(mn) → O(min(m,n))", "#0284C7"),
        ("100% Match", "Độ chính xác điểm số\ntrùng khớp Gotoh NW", "#059669"),
        ("1,73× Speedup", "Tăng tốc đa luồng\nOpenMP + Hybrid MPI", "#D97706"),
        ("86,8% SP", "Độ chính xác sinh học\nBAliBASE 3.0 (RV12)", "#7C3AED"),
    ]
    for idx, (st_val, st_lbl, st_col) in enumerate(s1_stats):
        sx = 40 + idx * 163
        ops.append({
            "op": "add-textbox", "slide": "p", "text": st_val,
            "x": sx, "y": 232, "width": 151, "height": 42,
            "font_size": 18, "bold": True, "color": "#FFFFFF",
            "background_color": st_col, "font_family": "Roboto",
            "alignment": "center", "content_alignment": "MIDDLE"
        })
        ops.append({
            "op": "add-textbox", "slide": "p", "text": st_lbl,
            "x": sx, "y": 274, "width": 151, "height": 54,
            "font_size": 10, "color": "#E2E8F0",
            "background_color": "#1E293B", "font_family": "Roboto",
            "alignment": "center", "content_alignment": "MIDDLE"
        })
    ops.append({
        "op": "add-textbox", "slide": "p",
        "text": "Thực hiện: Nhóm 5   |   Ngôn ngữ: Modern C++17, OpenMP, MPI, FastAPI   |   Kiểm thử: 342 Automated Tests (139.463 Assertions)",
        "x": 40, "y": 352, "width": 640, "height": 28,
        "font_size": 10.5, "bold": True, "color": "#94A3B8", "font_family": "Roboto"
    })
    ops.append({
        "op": "set-notes", "slide": "p",
        "text": "Xin chào Thầy/Cô và các bạn. Hôm nay Nhóm 5 xin trình bày đồ án môn Phân tích và Thiết kế Thuật toán: Thuật toán Chia để trị Song song kết hợp Quy hoạch động cho Căn chỉnh Đa chuỗi Protein/ADN (MSA)."
    })

    # --------------------------------------------------------------------------
    # SLIDE 2: BỐI CẢNH SINH HỌC CƠ BẢN (CHO DÂN CNTT / THUẬT TOÁN)
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S2"})
    add_top_bar(
        "S2", "PHẦN 1 • CƠ SỞ SINH HỌC",
        "Bản chất Sinh học: Chuỗi ADN/Protein & Hai Cơ chế Đột biến Tiến hóa",
        "Tại sao các chuỗi sinh học cùng nguồn gốc lại khác nhau về độ dài và ký tự? Ý nghĩa thực sự của dấu '-' (Gap)",
        "2 / 24"
    )
    add_card_gslides(
        "S2", 24, 66, 330, 155,
        "1. Chuỗi Sinh học dưới Góc nhìn Khoa học Máy tính",
        "• Chuỗi ADN / ARN: Chuỗi ký tự trên bảng chữ cái 4 chữ {A, T, G, C} lưu trữ mã di truyền.\n"
        "• Chuỗi Protein: Chuỗi gồm 20 loại Amino Acid (ký hiệu bởi 20 chữ cái: A, C, D, E, F, G, H, I, K, L, M, N, P, Q, R, S, T, V, W, Y), độ dài thường từ 100 đến vài nghìn ký tự.\n"
        "• Vai trò: Trình tự Amino Acid quyết định cấu trúc 3D và chức năng sống (ví dụ: Hemoglobin vận chuyển Oxy trong máu).",
        hdr_bg="#0F172A", body_bg="#FFFFFF", font_size=10
    )
    add_card_gslides(
        "S2", 24, 230, 330, 162,
        "2. Tại sao cần Căn chỉnh Đa chuỗi (MSA)?",
        "• Các loài khác nhau (Người, Tinh tinh, Cá voi...) tiến hóa từ một tổ tiên chung.\n"
        "• Những cột ký tự KHÔNG ĐỔI qua hàng triệu năm (Conserved Regions) chính là vùng lõi quyết định sự sống (nếu đột biến ở đó, sinh vật sẽ chết).\n"
        "• MSA giúp: (1) Tìm vùng chức năng bảo tồn, (2) Dự đoán cấu trúc Protein mới, (3) Dựng cây tiến hóa chủng loại.",
        hdr_bg="#0284C7", body_bg="#E0F2FE", font_size=10
    )
    add_card_gslides(
        "S2", 366, 66, 330, 155,
        "3. Hai Cơ chế Đột biến trong Tiến hóa Tự nhiên",
        "① Đột biến Thay thế (Substitution / Point Mutation):\n"
        "   Một Amino Acid bị thay bằng Amino Acid khác (ví dụ: V → I). Độ dài chuỗi KHÔNG đổi.\n"
        "② Đột biến Thêm / Mất đoạn (Indel = Insertion / Deletion):\n"
        "   Một đoạn gồm 1 hoặc nhiều Amino Acid bị đứt gãy mất đi (Deletion) hoặc chèn thêm vào (Insertion) → Làm các chuỗi BỊ LỆCH ĐỘ DÀI và trượt vị trí!",
        hdr_bg="#D97706", body_bg="#FEF3C7", font_size=10
    )
    add_card_gslides(
        "S2", 366, 230, 330, 162,
        "4. Ý nghĩa Sinh học của Ký tự Khoảng trống '-' (Gap)",
        "Tổ tiên:   M  V  L  S  P  A  D  K  T  N\n"
        "Người:     M  V  L  S  P  A  D  K  T  N  (Giữ nguyên)\n"
        "Tinh tinh: M  V  L  S  -  A  D  K  T  N  (Mất chữ P → chèn '-')\n"
        "Cá voi:    M  V  I  S  -  A  D  K  -  -  (Thay L→I, mất P, T, N)\n"
        "⇒ Chèn dấu '-' là khôi phục vị trí đã bị mất đoạn để gióng thẳng hàng các Amino Acid tương đồng về cùng 1 cột!",
        hdr_bg="#059669", body_bg="#D1FAE5", font_size=9.5, mono=True
    )
    ops.append({
        "op": "set-notes", "slide": "S2",
        "text": "Trước khi đi vào thuật toán, nhóm xin giải thích rõ bản chất sinh học của bài toán. Mỗi phân tử Protein là một chuỗi văn bản gồm 20 chữ cái đại diện cho 20 loại Amino Acid. Qua hàng triệu năm tiến hóa từ một tổ tiên chung, có 2 loại đột biến xảy ra: (1) Đột biến thay thế làm đổi chữ cái này sang chữ cái khác, và (2) Đột biến mất đoạn hoặc thêm đoạn (gọi tắt là Indel) làm các chuỗi bị hụt hoặc dư độ dài. Khi đưa vào máy tính, các chuỗi này bị lệch pha nhau. Việc thuật toán chèn ký tự gạch ngang '-' (Gap) chính là đánh dấu vị trí đã xảy ra đột biến mất đoạn để kéo các chữ cái có cùng nguồn gốc tiến hóa thẳng hàng về cùng một cột."
    })

    # --------------------------------------------------------------------------
    # SLIDE 3: PHÁT BIỂU BÀI TOÁN TƯỜNG MINH: CHO CÁI GÌ & YÊU CẦU LÀM CÁI GÌ?
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S3"})
    add_top_bar(
        "S3", "PHẦN 1 • PHÁT BIỂU BÀI TOÁN",
        "Phát biểu Bài toán MSA: Cho Cái Gì (Input) & Yêu Cầu Làm Cái Gì (Output)?",
        "Định nghĩa hình thức đầu vào, đầu ra, 3 ràng buộc hợp lệ và hàm mục tiêu tối ưu hóa tổ hợp",
        "3 / 24"
    )
    add_card_gslides(
        "S3", 24, 66, 330, 148,
        "CHO CÁI GÌ? (INPUT CỦA BÀI TOÁN)",
        "• Cho tập k chuỗi sinh học S = {S₁, S₂, ..., S_k} (k ≥ 3) trên bảng chữ cái Σ.\n"
        "• Độ dài ban đầu khác nhau: |S₁| = n₁, |S₂| = n₂, ..., |S_k| = n_k.\n"
        "• Cho trước Ma trận điểm thay thế BLOSUM62 và tham số phạt khoảng trống (G_open = -10, G_ext = -1).\n"
        "• Ví dụ Input (k = 3 chuỗi chưa căn chỉnh):\n"
        "   S₁ = \"MVLSPADKTN\" (n₁ = 10)\n"
        "   S₂ = \"MVLSADKTN\"  (n₂ = 9)\n"
        "   S₃ = \"MVLSEADK\"   (n₃ = 8)",
        hdr_bg="#0284C7", body_bg="#FFFFFF", font_size=9.8
    )
    add_card_gslides(
        "S3", 366, 66, 330, 148,
        "YÊU CẦU LÀM CÁI GÌ? (OUTPUT CỦA BÀI TOÁN)",
        "• Tìm cách chèn các ký tự '-' vào các chuỗi S_i để tạo thành Ma trận Căn chỉnh A kích thước k hàng × L cột:\n"
        "   A[1]: M  V  L  S  P  A  D  K  T  N   (L = 10)\n"
        "   A[2]: M  V  L  S  -  A  D  K  T  N   (L = 10)\n"
        "   A[3]: M  V  L  S  E  A  D  K  -  -   (L = 10)\n"
        "         *  *  *  *  .  *  *  *  :  :   (Cột bảo tồn)\n"
        "• Sao cho Tổng Điểm Tương đồng Toàn cục SP(A) đạt CỰC ĐẠI (MAX)!",
        hdr_bg="#059669", body_bg="#FFFFFF", font_size=9.8, mono=True
    )
    add_card_gslides(
        "S3", 24, 224, 672, 168,
        "3 RÀNG BUỘC BẮT BUỘC & HÀM MỤC TIÊU TOÁN HỌC (OBJECTIVE FUNCTION)",
        "1. Ràng buộc Đồng nhất Độ dài: Mọi hàng trong ma trận kết quả A đều phải có cùng độ dài L, với max(n_i) ≤ L ≤ ∑ n_i.\n"
        "2. Ràng buộc Bảo toàn Thứ tự Gốc (Order-Preserving): Nếu xóa toàn bộ ký tự '-' trên hàng thứ i của ma trận A, ta phải thu lại chính xác 100% chuỗi gốc S_i ban đầu (tuyệt đối không được hoán vị, thêm hay làm rụng Amino Acid).\n"
        "3. Ràng buộc Không suy biến (No All-Gap Column): Không tồn tại bất kỳ cột c ∈ [1..L] nào mà cả k hàng đều là dấu '-'.\n"
        "4. Hàm Mục tiêu Tối ưu hóa Tổng Cặp đôi (Sum-of-Pairs Score): Tìm ma trận A* = argmax SP(A), với:\n"
        "   SP(A) = ∑_{1 ≤ p < q ≤ k} [ ∑_{c=1..L} score(A[p,c], A[q,c])  -  ∑ Phạt_Affine_Gap(chuỗi p, chuỗi q) ]",
        hdr_bg="#0F172A", body_bg="#F8FAFC", font_size=9.8
    )
    ops.append({
        "op": "set-notes", "slide": "S3",
        "text": "Slide này phát biểu tường minh bài toán theo chuẩn Khoa học máy tính: Cho cái gì và Yêu cầu tìm cái gì? Đầu vào (Input) là k chuỗi có độ dài ngắn dài khác nhau cùng bảng điểm BLOSUM62. Yêu cầu (Output) là chèn các dấu gạch ngang '-' để biến k chuỗi đó thành một ma trận chữ nhật k hàng nhân L cột thỏa mãn 3 ràng buộc: cùng độ dài L, giữ nguyên thứ tự chữ cái gốc khi bỏ dấu '-', không có cột nào chứa toàn dấu '-', và đạt tổng điểm tương đồng cặp đôi Sum-of-Pairs lớn nhất."
    })

    # --------------------------------------------------------------------------
    # SLIDE 4: TẠI SAO DÙNG BLOSUM62 & PHẠT KHOẢNG TRỐNG AFFINE (-10, -1)?
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S4"})
    add_top_bar(
        "S4", "PHẦN 1 • MÔ HÌNH ĐIỂM SỐ SINH HỌC",
        "Tại sao dùng Ma trận BLOSUM62 & Phạt Khoảng trống Affine (-10, -1)?",
        "Sự khác biệt giữa bài toán chuỗi thuần túy (LCS) và bài toán Sinh tin học thực tế",
        "4 / 24"
    )
    add_card_gslides(
        "S4", 24, 66, 330, 326,
        "1. Ma trận Thay thế BLOSUM62 (20 × 20 Amino Acids)",
        "• Tại sao KHÔNG chấm điểm kiểu đơn giản (Giống = +1, Khác = -1)?\n"
        "  Vì trong sinh học, 20 loại Amino Acid có tính chất hóa lý khác nhau (Kỵ nước, Phân cực, Điện tích dương, Điện tích âm).\n\n"
        "• Công thức Log-Odds của BLOSUM62 (Henikoff, 1992):\n"
        "  BLOSUM62(a, b) = round( 2 × log₂( P_quan_sát(a,b) / (P(a)·P(b)) ) )\n\n"
        "• Ví dụ thực tế trong bảng BLOSUM62:\n"
        "  - Khớp Amino Acid hiếm (W – W):  +11 điểm (Rất giá trị)\n"
        "  - Khớp Amino Acid phổ biến (A – A): +4 điểm\n"
        "  - Thay thế CÙNG tính chất kỵ nước (I ↔ V): +3 điểm (Dễ xảy ra)\n"
        "  - Thay thế TRÁI tính chất (L ↔ D): -4 điểm (Bị phạt nặng)\n"
        "  - Hai khoảng trống trùng nhau ('-' với '-'): 0 điểm",
        hdr_bg="#1E2761", body_bg="#FFFFFF", font_size=9.8
    )
    add_card_gslides(
        "S4", 366, 66, 330, 326,
        "2. Tại sao dùng Phạt Khoảng trống Affine γ(g) = -10 - (g-1)×1?",
        "• Thực tế Sinh học Phân tử:\n"
        "  Một sự kiện đứt gãy ADN làm mất liền 3 ký tự liên tiếp dễ xảy ra hơn rất nhiều so với 3 lần đứt gãy độc lập ở 3 nơi khác nhau!\n\n"
        "• Công thức Phạt Affine cho khoảng trống dài g ký tự liên tiếp:\n"
        "  γ(g) = G_open + (g - 1) × G_ext   (với G_open = -10, G_ext = -1)\n\n"
        "• So sánh bằng Con số Cụ thể (Cùng chèn 3 dấu '-'):\n"
        "  ❌ Cách 1 (3 gap rời rạc):  M - V - L - S P\n"
        "     Điểm phạt = (-10) + (-10) + (-10) = -30 điểm (Rất tệ!)\n"
        "  ✅ Cách 2 (1 khối gap dài 3): M V L - - - S P\n"
        "     Điểm phạt = -10 + 2×(-1) = -12 điểm (Tối ưu sinh học!)\n"
        "⇒ Phạt Affine ép thuật toán gom các dấu '-' thành khối liền mạch!",
        hdr_bg="#059669", body_bg="#FFFFFF", font_size=9.8
    )
    ops.append({
        "op": "set-notes", "slide": "S4",
        "text": "Slide này giải thích tại sao bài toán MSA phức tạp hơn bài toán Xâu con chung dài nhất (LCS) thông thường ở hai điểm: Thứ nhất là bảng điểm BLOSUM62 đánh trọng số theo tính chất hóa học của 20 loại Amino Acid; ví dụ I và V cùng kỵ nước thay thế cho nhau vẫn được cộng 3 điểm. Thứ hai là hàm phạt khoảng trống Affine: mở khoảng trống đầu tiên bị phạt rất nặng (-10), nhưng nối dài khoảng trống đó chỉ phạt (-1). Ví dụ ở cột phải cho thấy: cùng chèn 3 dấu gạch ngang, nếu xé lẻ ở 3 nơi sẽ bị phạt -30 điểm, còn gom lại thành 1 đoạn liền nhau chỉ bị phạt -12 điểm."
    })

    # --------------------------------------------------------------------------
    # SLIDE 5: ĐỘ KHÓ NP-HARD & NÚT THẮT BỘ NHỚ O(MN) -> 3 TRỤ CỘT GIẢI PHÁP
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S5"})
    add_top_bar(
        "S5", "PHẦN 1 • THÁCH THỨC & ĐÓNG GÓP",
        "Tại sao MSA Khó? Sự Bùng nổ NP-Hard O(2^k·N^k) & Nút thắt Bộ nhớ O(mn)",
        "Hai rào cản toán học ngăn cản Quy hoạch động truyền thống và Giải pháp 3 Trụ cột của Nhóm 5",
        "5 / 24"
    )
    add_card_gslides(
        "S5", 24, 66, 214, 195,
        "Rào cản 1: Bùng nổ Tổ hợp NP-Hard",
        "• Quy hoạch động chính xác đồng thời k chuỗi cần bảng k chiều (Hypercube).\n"
        "• Bộ nhớ: O(N^k).\n"
        "• Thời gian: O(2^k · N^k).\n"
        "• Với k = 10 chuỗi, N = 500 → Cần 10²⁷ ô nhớ (Bất khả thi!).\n"
        "• Đã chứng minh là bài toán NP-Complete (Wang & Jiang, 1994).",
        hdr_bg="#E11D48", body_bg="#FFE4E6", font_size=9.5
    )
    add_card_gslides(
        "S5", 253, 66, 214, 195,
        "Rào cản 2: Tràn RAM Bậc hai Gotoh",
        "• Khi căn chỉnh từng cặp 2 chuỗi (m, n) với phạt Affine, thuật toán Gotoh (1982) cần lưu 3 ma trận 2D (M, Ix, Iy).\n"
        "• Bộ nhớ: 3 × m × n × 4 bytes = O(mn).\n"
        "• Với m = n = 10.000 → Tốn ~1,2 GB RAM cho 1 cặp duy nhất!\n"
        "• Chạy đa luồng P cặp cùng lúc sẽ gây tràn RAM (Out-of-Memory).",
        hdr_bg="#D97706", body_bg="#FEF3C7", font_size=9.5
    )
    add_card_gslides(
        "S5", 482, 66, 214, 195,
        "Rào cản 3: Chi phí Tuần tự Lớn",
        "• Để dựng cây hướng dẫn cho k chuỗi, phải tính k(k-1)/2 cặp khoảng cách (k=40 → 780 cặp DP).\n"
        "• Khi căn chỉnh nhóm chuỗi (Profile-to-Profile), mỗi ô DP tốn O(|P₁|·|P₂|) phép tra bảng.\n"
        "• Chạy tuần tự 1 luồng trên CPU mất nhiều thời gian.",
        hdr_bg="#7C3AED", body_bg="#F3E8FF", font_size=9.5
    )
    add_card_gslides(
        "S5", 24, 270, 672, 122,
        "GIẢI PHÁP ĐỀ XUẤT CỦA NHÓM 5 — KẾT HỢP 3 KỸ THUẬT THUẬT TOÁN HIỆN ĐẠI",
        "① Chia để trị Không gian Tuyến tính Myers-Miller (Hirschberg Affine Gap): Ép bộ nhớ từ O(mn) xuống O(min(m, n)) — tiết kiệm tới 1.353,5× RAM mà vẫn giữ nguyên 100% điểm số tối ưu toàn cục của Gotoh.\n"
        "② Xấp xỉ Tiến bộ UPGMA + Căn chỉnh Profile-to-Profile: Đưa độ phức tạp mũ O(2^k·N^k) về đa thức O(k²N² + kL²) với nguyên lý bảo tồn khoảng trống 'Once a gap, always a gap'.\n"
        "③ Tính toán Song song Đa tầng Hybrid (MPI + OpenMP): Song song hóa ma trận khoảng cách, lập lịch cây theo tầng (Level-Set) và đường chéo phụ (Wavefront).",
        hdr_bg="#059669", body_bg="#D1FAE5", font_size=9.5
    )
    ops.append({
        "op": "set-notes", "slide": "S5",
        "text": "Tại sao bài toán MSA lại là một thách thức kinh điển của môn Phân tích và Thiết kế Thuật toán? Vì nếu giải chính xác bằng quy hoạch động k chiều, độ phức tạp là O(2^k * N^k) thuộc lớp NP-Hard. Còn nếu giải từng cặp bằng thuật toán Gotoh truyền thống thì lại vướng nút thắt bộ nhớ bậc hai O(mn). Nhóm 5 giải quyết trọn vẹn cả hai vấn đề bằng 3 trụ cột ở khung màu xanh bên dưới."
    })

    # --------------------------------------------------------------------------
    # SLIDE 6: [FULL-BLEED DIAGRAM] KIẾN TRÚC TỔNG THỂ PIPELINE 4 GIAI ĐOẠN
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S6"})
    add_full_bleed_image_slide(
        "S6", "PHẦN 2 • KIẾN TRÚC PIPELINE",
        "Tổng quan Kiến trúc Pipeline Căn chỉnh Đa chuỗi Tiến bộ (4 Giai đoạn)",
        "Sơ đồ luồng xử lý từ tập chuỗi thô đầu vào (FASTA) đến ma trận đa chuỗi hoàn chỉnh",
        "6 / 24",
        DOCS_IMG_DIR / "fig_4_1_system_architecture.png",
        "Luồng 4 Bước: (1) All-Pairs Distance O(k²N²/P)  →  (2) Cây UPGMA O(k²)  →  (3) Lập lịch Nhánh Độc lập  →  (4) Profile Myers-Miller O(k·L) RAM",
        "Trên màn hình là sơ đồ kiến trúc tổng thể 4 giai đoạn của hệ thống được hiển thị toàn màn hình. Bước 1 tính ma trận khoảng cách cho k(k-1)/2 cặp chuỗi bằng DP 1 chiều. Bước 2 dùng thuật toán gom cụm UPGMA để dựng cây hướng dẫn nhị phân. Bước 3 phân tích các nhánh cây độc lập để lập lịch song song. Và Bước 4 đi từ lá lên gốc, hợp nhất từng cặp Profile bằng thuật toán chia để trị Myers-Miller."
    )

    # --------------------------------------------------------------------------
    # SLIDE 7: QUY HOẠCH ĐỘNG GOTOH (1982) BASELINE & NÚT THẮT TRUY VẾT
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S7"})
    add_top_bar(
        "S7", "PHẦN 2 • THIẾT KẾ THUẬT TOÁN LÕI",
        "Quy hoạch Động Gotoh (1982) Baseline: Hệ 3 Phương trình & Nút thắt Bộ nhớ",
        "Tại sao phạt khoảng trống Affine cần tới 3 trạng thái quy hoạch động M, Ix, Iy tại mỗi ô (i, j)?",
        "7 / 24"
    )
    add_card_gslides(
        "S7", 24, 66, 395, 326,
        "1. Hệ Phương trình Truy hồi 3 Trạng thái của Gotoh (1982)",
        "Để biết việc chèn dấu '-' tại ô (i, j) là MỞ MỚI (-10) hay KÉO DÀI (-1), ta phải tách thành 3 ma trận trạng thái kích thước (m+1) × (n+1):\n\n"
        "① M(i, j) — Khớp A[i] với B[j] (Đi chéo ↘):\n"
        "   M(i, j) = BLOSUM62(A[i], B[j]) + max { M(i-1, j-1), Ix(i-1, j-1), Iy(i-1, j-1) }\n\n"
        "② Ix(i, j) — Ký tự A[i] đối diện dấu '-' trên B (Đi xuống ↓):\n"
        "   Ix(i, j) = max { M(i-1, j) + G_open + G_ext,   [Mở gap mới]\n"
        "                    Ix(i-1, j) + G_ext }          [Kéo dài gap cũ]\n\n"
        "③ Iy(i, j) — Ký tự B[j] đối diện dấu '-' trên A (Đi ngang →):\n"
        "   Iy(i, j) = max { M(i, j-1) + G_open + G_ext,   [Mở gap mới]\n"
        "                    Iy(i, j-1) + G_ext }          [Kéo dài gap cũ]",
        hdr_bg="#1E2761", body_bg="#FFFFFF", font_size=9.6, mono=False
    )
    add_card_gslides(
        "S7", 431, 66, 265, 165,
        "2. Nhận xét Đột phá (Key Insight)",
        "• Khi CHỈ tính điểm số ở ô cuối (m, n):\n"
        "  Dòng thứ i chỉ phụ thuộc vào dòng i-1 liền trước → Chỉ cần giữ 2 dòng trong RAM = O(n) bộ nhớ!\n\n"
        "• Tại sao Gotoh vẫn tốn O(mn) RAM?\n"
        "  Vì để TRUY VẾT (Backtrack) tìm vị trí chèn dấu '-' từ (m,n) ngược về (0,0), Gotoh phải lưu lại toàn bộ m×n ô của cả 3 ma trận!",
        hdr_bg="#0284C7", body_bg="#E0F2FE", font_size=9.6
    )
    add_card_gslides(
        "S7", 431, 241, 265, 151,
        "3. Ý tưởng Chia để trị Myers-Miller",
        "• Thay vì lưu cả bảng 2D để lần ngược từ cuối về đầu:\n"
        "  Ta dùng DP 2 dòng (tốn O(n) RAM) chạy từ ĐẦU xuống GIỮA và từ CUỐI lên GIỮA để tìm chính xác tọa độ giao điểm (i*, j*) ở dòng giữa!\n"
        "• Sau đó chia đôi bài toán thành 2 nửa nhỏ hơn và lặp lại đệ quy!",
        hdr_bg="#E11D48", body_bg="#FFE4E6", font_size=9.6
    )
    ops.append({
        "op": "set-notes", "slide": "S7",
        "text": "Để xử lý hàm phạt khoảng trống Affine, tại mỗi ô (i, j) ta cần biết bước trước đó đang ở trạng thái khớp ký tự hay đang ở sẵn trong một khoảng trống. Do đó Gotoh (1982) dùng 3 bảng quy hoạch động M, Ix, Iy. Nhận xét quan trọng nhất ở cột phải là: để tính điểm, dòng thứ i chỉ cần nhìn lên dòng i-1, tức chỉ tốn O(n) bộ nhớ. Toàn bộ chi phí bộ nhớ O(mn) của Gotoh chỉ phục vụ một việc duy nhất là truy vết đường đi. Vậy làm sao truy vết mà không cần lưu bảng 2D? Đó chính là thuật toán Chia để trị Myers-Miller ở slide tiếp theo."
    })

    # --------------------------------------------------------------------------
    # SLIDE 8: THUẬT TOÁN CHIA ĐỂ TRỊ MYERS-MILLER / HIRSCHBERG (LÝ THUYẾT)
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S8"})
    add_top_bar(
        "S8", "PHẦN 2 • THIẾT KẾ THUẬT TOÁN LÕI",
        "Thuật toán Chia để trị Tuyến tính Myers-Miller / Hirschberg (1988)",
        "Cơ chế 4 bước tìm điểm cắt tối ưu (i*, j*) tại dòng giữa i* = ⌊m/2⌋ chỉ bằng các vector 1 chiều O(n)",
        "8 / 24"
    )
    add_card_gslides(
        "S8", 24, 66, 330, 326,
        "Quy trình Chia để trị 4 Bước (Divide & Conquer)",
        "• Bước 1 — Chia (Divide):\n"
        "  Chia đôi chuỗi A theo chiều ngang tại dòng giữa i* = ⌊m / 2⌋.\n\n"
        "• Bước 2 — Quét Xuôi (Forward Pass — O(n) RAM):\n"
        "  Chạy DP 2 dòng cho nửa trên A[1..i*] với B[1..n] từ (0,0) xuống dòng i*.\n"
        "  Thu được vector 1D: Fwd_M[j], Fwd_Ix[j] (với j = 0..n).\n\n"
        "• Bước 3 — Quét Ngược (Backward Pass — O(n) RAM):\n"
        "  Chạy DP 2 dòng cho nửa dưới A[i*+1..m] với B[1..n] theo chiều ngược từ (m,n) lên dòng i*.\n"
        "  Thu được vector 1D: Bwd_M[j], Bwd_Ix[j] (với j = 0..n).\n\n"
        "• Bước 4 — Tổ hợp & Đệ quy (Combine & Recurse):\n"
        "  Tìm cột j* tối ưu tại dòng i*, rồi gọi đệ quy độc lập trên:\n"
        "  - Bài toán con Trái-Trên: A[1..i*] với B[1..j*]\n"
        "  - Bài toán con Phải-Dưới: A[i*+1..m] với B[j*+1..n]",
        hdr_bg="#0284C7", body_bg="#FFFFFF", font_size=9.6
    )
    add_card_gslides(
        "S8", 366, 66, 330, 175,
        "Công thức Tìm Cột Cắt Tối ưu j* tại Dòng Giữa i*",
        "Đường căn chỉnh tối ưu toàn cục từ (0,0) đến (m,n) BẮT BUỘC phải cắt qua dòng i* tại cột j* sao cho tổng điểm tiền tố + hậu tố đạt cực đại:\n\n"
        "  j* = argmax_{0 ≤ j ≤ n}  max {\n"
        "      ① Fwd_M(j)  + Bwd_M(j),\n"
        "      ② Fwd_Ix(j) + Bwd_Ix(j) - G_open + G_ext\n"
        "  }",
        hdr_bg="#1E2761", body_bg="#E0F2FE", font_size=9.8, mono=True
    )
    add_card_gslides(
        "S8", 366, 250, 330, 142,
        "Tại sao có số hạng hiệu chỉnh (-G_open + G_ext)?",
        "• Kỹ thuật Hợp nhất Khoảng trống (Gap Coalescing):\n"
        "  Nếu đường đi tối ưu đang nằm trong một khoảng trống dọc (Ix) kéo dài xuyên qua ranh giới dòng i*, cả lượt quét xuôi Fwd_Ix(j) và quét ngược Bwd_Ix(j) đều đã tính phạt mở khoảng trống G_open (-10) một lần.\n"
        "• Do đó phải TRỪ đi G_open và CỘNG bù G_ext để gộp 2 nửa khoảng trống thành 1 khoảng trống liên tục duy nhất!",
        hdr_bg="#E11D48", body_bg="#FFE4E6", font_size=9.5
    )
    ops.append({
        "op": "set-notes", "slide": "S8",
        "text": "Slide này trình bày chi tiết 4 bước của thuật toán Chia để trị Myers-Miller. Sau khi cắt đôi ma trận tại dòng i* = m/2, ta dùng DP 2 hàng quét từ trên xuống dòng giữa để lấy vector Fwd, và quét từ dưới lên dòng giữa để lấy vector Bwd. Tại dòng giữa i*, cột j* nào có tổng điểm Fwd + Bwd lớn nhất chính là giao điểm mà đường đi tối ưu đi qua. Đặc biệt, công thức số 2 xử lý chính xác trường hợp một khoảng trống đi xuyên qua nhát cắt bằng cách trừ G_open và cộng G_ext để không phạt mở khoảng trống 2 lần."
    })

    # --------------------------------------------------------------------------
    # SLIDE 9: [FULL-BLEED DIAGRAM] MINH HỌA HÌNH HỌC NHÁT CẮT MYERS-MILLER
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S9"})
    add_full_bleed_image_slide(
        "S9", "PHẦN 2 • TRỰC QUAN HÓA CHIA ĐỂ TRỊ",
        "Minh họa Hình học Nhát cắt Giữa i* = ⌊m/2⌋ & Thu hẹp Diện tích Myers-Miller",
        "Sau khi tìm được điểm cắt (i*, j*), 2 góc phần tư màu xám bị loại bỏ hoàn toàn — diện tích giảm đúng một nửa!",
        "9 / 24",
        DOCS_IMG_DIR / "fig_2_1_myers_miller_cut.png",
        "Bất biến Diện tích: Tổng diện tích 2 bài toán con màu xanh = (m/2)·j* + (m/2)·(n - j*) = ½ (m·n)  ⇒  Bộ nhớ O(min(m,n)), Thời gian 2·O(mn)",
        "Trên hình minh họa toàn màn hình này, Thầy/Cô và các bạn có thể thấy rõ trực quan hình học của thuật toán: Lượt quét xuôi (màu xanh dương) từ góc trên trái xuống dòng giữa i*, lượt quét ngược (màu cam) từ góc dưới phải lên dòng giữa i*. Sau khi tìm được giao điểm tối ưu (i*, j*), đường đi tối ưu chỉ có thể đi trong 2 ô chữ nhật con (góc trên-trái và góc dưới-phải). Hai phần diện tích còn lại bị loại bỏ hoàn toàn, giúp tổng diện tích cần tính ở bước đệ quy tiếp theo giảm đi đúng một nửa!"
    )

    # --------------------------------------------------------------------------
    # SLIDE 10: THUẬT TOÁN GOM CỤM UPGMA & CÂY HƯỚNG DẪN (LÝ THUYẾT)
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S10"})
    add_top_bar(
        "S10", "PHẦN 2 • CÂY HƯỚNG DẪN UPGMA",
        "Xây dựng Cây Hướng dẫn UPGMA (Unweighted Pair Group Method with Arithmetic Mean)",
        "Tại sao phải căn chỉnh theo Cây Hướng dẫn thay vì ghép chuỗi theo thứ tự ngẫu nhiên?",
        "10 / 24"
    )
    add_card_gslides(
        "S10", 24, 66, 330, 326,
        "1. Ý nghĩa Sinh học của Cây Hướng dẫn (Guide Tree)",
        "• Tại sao KHÔNG ghép chuỗi theo thứ tự xuất hiện S₁ → S₂ → S₃?\n"
        "  Nếu S₁ (Người) ghép ngay với S₂ (Cá voi - rất xa nhau) trước khi ghép với S₃ (Tinh tinh - rất gần nhau), các dấu '-' chèn sai ở bước đầu sẽ làm hỏng toàn bộ các bước sau!\n\n"
        "• Nguyên lý Tiến hóa (Phylogenetic Principle):\n"
        "  Các chuỗi có độ tương đồng cao nhất (khoảng cách tiến hóa d nhỏ nhất) phải được ưu tiên căn chỉnh với nhau TRƯỚC ở các nút lá.\n\n"
        "• Chuẩn hóa Khoảng cách Tiến hóa d(A, B) ∈ [0, 1]:\n"
        "  d(A, B) = 1.0  -  Score(A, B) / max( Score(A, A), Score(B, B) )\n"
        "  - Hai chuỗi giống hệt nhau: d(A, B) = 0.0\n"
        "  - Hai chuỗi rất khác biệt:   d(A, B) → 1.0",
        hdr_bg="#7C3AED", body_bg="#FFFFFF", font_size=9.6
    )
    add_card_gslides(
        "S10", 366, 66, 330, 326,
        "2. Các Bước Gom cụm Phân cấp UPGMA — Độ phức tạp O(k²)",
        "• Khởi tạo: Mỗi chuỗi S_i là một cụm đơn lẻ C_i = {S_i} (k nút lá).\n\n"
        "• Vòng lặp (k - 1 bước hợp nhất):\n"
        "  1. Tìm cặp cụm (C_u, C_v) có khoảng cách d(C_u, C_v) NHỎ NHẤT.\n"
        "  2. Tạo nút cha mới C_w = C_u ∪ C_v với chiều cao nhánh h_w = d(C_u, C_v) / 2.\n"
        "  3. Cập nhật khoảng cách trung bình có trọng số từ C_w tới mọi cụm C_q còn lại:\n"
        "     d(C_w, C_q) = [ |C_u|·d(C_u, C_q) + |C_v|·d(C_v, C_q) ] / (|C_u| + |C_v|)\n\n"
        "• Kỹ thuật Deterministic Tie-Breaking của Nhóm 5:\n"
        "  Khi 2 cặp có khoảng cách bằng nhau (|Δd| < 10⁻⁹), luôn ưu tiên cặp có chỉ số ID nhỏ hơn → Đảm bảo cây UPGMA giống nhau 100% giữa chạy 1 luồng và đa luồng!",
        hdr_bg="#1E2761", body_bg="#F3E8FF", font_size=9.6
    )
    ops.append({
        "op": "set-notes", "slide": "S10",
        "text": "Sau khi biết cách căn chỉnh 2 chuỗi bằng Myers-Miller, câu hỏi tiếp theo là: với k chuỗi thì ta căn chỉnh cặp nào trước, cặp nào sau? Nếu ghép ngẫu nhiên hai chuỗi rất khác nhau trước, các khoảng trống sai lệch sẽ phát sinh. Do đó hệ thống tính khoảng cách tiến hóa chuẩn hóa d(A,B) thuộc đoạn [0, 1] và dùng thuật toán gom cụm phân cấp UPGMA để luôn ghép các cặp chuỗi họ hàng gần nhất trước, tạo thành cây nhị phân dẫn đường."
    })

    # --------------------------------------------------------------------------
    # SLIDE 11: [FULL-BLEED DIAGRAM] MINH HỌA GOM CỤM UPGMA & CÂY DẪN ĐƯỜNG
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S11"})
    add_full_bleed_image_slide(
        "S11", "PHẦN 2 • TRỰC QUAN HÓA UPGMA",
        "Minh họa Quá trình Gom cụm Ma trận Khoảng cách thành Cây Nhị phân UPGMA",
        "Từ ma trận khoảng cách đối xứng k×k đến cây phân cấp dẫn đường duyệt từ dưới lên (Bottom-Up)",
        "11 / 24",
        DOCS_IMG_DIR / "fig_2_3_upgma_clustering.png",
        "Cây UPGMA xác định chính xác thứ tự căn chỉnh: Các nút lá ghép thành Profile nhỏ → Hợp nhất dần lên nút gốc (Root) để thu được MSA cuối cùng",
        "Hình minh họa toàn màn hình này thể hiện trực quan cách thuật toán UPGMA chuyển đổi ma trận khoảng cách cặp đôi thành cây nhị phân hướng dẫn. Các chuỗi có khoảng cách nhỏ nhất được gom cụm ở tầng dưới cùng, sau đó khoảng cách được cập nhật theo trung bình trọng số để dựng tiếp các tầng bên trên cho tới nút gốc."
    )

    # --------------------------------------------------------------------------
    # SLIDE 12: CĂN CHỈNH PROFILE-TO-PROFILE & BẢO TỒN GAP (LÝ THUYẾT)
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S12"})
    add_top_bar(
        "S12", "PHẦN 2 • CĂN CHỈNH PROFILE-TO-PROFILE",
        "Căn chỉnh Profile-to-Profile & Nguyên lý 'Once a gap, always a gap'",
        "Làm thế nào để căn chỉnh một nhóm chuỗi (Profile P₁) với một nhóm chuỗi khác (Profile P₂) bằng Myers-Miller?",
        "12 / 24"
    )
    add_card_gslides(
        "S12", 24, 66, 330, 326,
        "1. Khái niệm Profile & Hàm Điểm Cột-đối-Cột PSP(x, y)",
        "• Profile là gì?\n"
        "  Tại mỗi nút nhánh của cây UPGMA, kết quả căn chỉnh của các chuỗi con tạo thành một ma trận nhỏ gọi là một Profile P (gồm |P| hàng và L_P cột).\n\n"
        "• Làm sao đưa 2 Profile P₁ (dài m cột) và P₂ (dài n cột) vào thuật toán Myers-Miller?\n"
        "  Ta coi mỗi CỘT của P₁ như 1 'siêu ký tự' A[x] và mỗi CỘT của P₂ như 1 'siêu ký tự' B[y]!\n\n"
        "• Hàm Điểm Trung bình Cặp Cột (Profile Sum-of-Pairs — PSP):\n"
        "  PSP(x, y) = [ 1 / (|P₁|·|P₂|) ] × ∑_{r ∈ P₁} ∑_{s ∈ P₂} score(P₁[r,x], P₂[s,y])\n"
        "⇒ Thay thế trực tiếp hàm BLOSUM62(A[i], B[j]) trong phương trình Myers-Miller!",
        hdr_bg="#059669", body_bg="#FFFFFF", font_size=9.6
    )
    add_card_gslides(
        "S12", 366, 66, 330, 326,
        "2. Quy tắc 'Once a gap, always a gap' (Feng & Doolittle, 1987)",
        "• Khi căn chỉnh Profile P₁ (gồm Seq1, Seq2) với Profile P₂ (gồm Seq3, Seq4):\n"
        "  Nếu thuật toán Myers-Miller quyết định chèn 1 khoảng trống vào P₁ tại vị trí cột x, ta PHẢI chèn nguyên một cột gồm toàn dấu '-' vào CẢ Seq1 lẫn Seq2 tại cùng vị trí đó!\n\n"
        "• Minh họa Bảo tồn Khoảng trống (Gap Propagation):\n"
        "  Profile P₁ trước khi ghép:      Sau khi chèn cột gap vào P₁:\n"
        "    Seq1: M V L - S P               Seq1: M V L - [ - ] S P\n"
        "    Seq2: M V I K S P               Seq2: M V I K [ - ] S P\n\n"
        "• Ý nghĩa: Các chữ cái đã gióng thẳng hàng với nhau ở nút con (như M-M, V-V, S-S, P-P) KHÔNG BAO GIỜ bị xô lệch khi đi lên nút cha!",
        hdr_bg="#1E2761", body_bg="#D1FAE5", font_size=9.6
    )
    ops.append({
        "op": "set-notes", "slide": "S12",
        "text": "Khi đi từ lá lên các nút nhánh bên trong cây UPGMA, bài toán không còn là căn chỉnh 2 chuỗi đơn lẻ mà là căn chỉnh 1 nhóm chuỗi đã căn chỉnh (Profile P1) với 1 nhóm chuỗi khác (Profile P2). Nhóm giải quyết bằng cách coi mỗi cột của Profile như một phần tử và định nghĩa hàm điểm trung bình giữa 2 cột PSP(x, y). Đặc biệt, khi chèn khoảng trống vào một Profile, cả một cột toàn dấu '-' được chèn đồng bộ vào mọi chuỗi trong Profile đó theo quy tắc 'Once a gap, always a gap' để giữ nguyên cấu trúc đã căn chỉnh ở bước trước."
    })

    # --------------------------------------------------------------------------
    # SLIDE 13: [FULL-BLEED DIAGRAM] SƠ ĐỒ CĂN CHỈNH PROFILE-TO-PROFILE
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S13"})
    add_full_bleed_image_slide(
        "S13", "PHẦN 2 • TRỰC QUAN HÓA PROFILE ALIGNMENT",
        "Sơ đồ Căn chỉnh Profile-to-Profile & Lan truyền Cột Khoảng trống",
        "Minh họa cách 2 Profile con hợp nhất thành Profile cha thông qua điểm khớp cột PSP và chèn cột '-' đồng bộ",
        "13 / 24",
        DOCS_IMG_DIR / "fig_2_2_profile_alignment.png",
        "Tối ưu hóa Tần suất Cột: Lưu trữ vector tần suất 20 Amino Acid trên từng cột giúp tính điểm PSP(x,y) nhanh gấp nhiều lần khi |P| lớn",
        "Sơ đồ toàn màn hình này minh họa trực quan quá trình hợp nhất 2 Profile. Mỗi cột của Profile 1 được đối sánh với mỗi cột của Profile 2 bằng thuật toán chia để trị không gian tuyến tính Myers-Miller, và các cột khoảng trống được chèn xuyên suốt toàn bộ các chuỗi thành viên."
    )

    # --------------------------------------------------------------------------
    # SLIDE 14: [FULL-BLEED DIAGRAM] KIẾN TRÚC SONG SONG ĐA TẦNG HYBRID MPI + OPENMP
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S14"})
    add_full_bleed_image_slide(
        "S14", "PHẦN 3 • KIẾN TRÚC SONG SONG ĐA TẦNG",
        "Kiến trúc Song song Đa tầng Hybrid: MPI Phân tán + OpenMP Đa luồng",
        "Phối hợp chia tải vòng tròn Block-Cyclic liên máy tính (MPI) và lập lịch động đa nhân (OpenMP)",
        "14 / 24",
        RES_FIG_DIR / "fig5_parallel_architecture.png",
        "Cấp 1 (MPI): Chia k(k-1)/2 cặp theo Block-Cyclic + MPI_Allgatherv  |  Cấp 2 (OpenMP): #pragma omp parallel for schedule(dynamic, 1) & Level-Set Tree",
        "Bước sang Phần 3 về tính toán song song. Sơ đồ toàn màn hình trên slide thể hiện kiến trúc Hybrid kết hợp MPI và OpenMP xuyên suốt các giai đoạn. Ở Giai đoạn 1, k(k-1)/2 cặp chuỗi hoàn toàn độc lập dữ liệu nên được phân tán đều qua các Node mạng bằng kỹ thuật chia vòng tròn Block-Cyclic trên MPI và chia luồng động schedule(dynamic, 1) trên OpenMP."
    )

    # --------------------------------------------------------------------------
    # SLIDE 15: [FULL-BLEED DIAGRAM] SONG SONG HÓA WAVEFRONT & LEVEL-SET TREE
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S15"})
    add_full_bleed_image_slide(
        "S15", "PHẦN 3 • SONG SONG HÓA ĐƯỜNG CHÉO & CÂY",
        "Song song hóa Đường chéo phụ Wavefront Anti-Diagonal DP",
        "Khắc phục phụ thuộc dữ liệu ô (i, j) bằng mặt sóng đường chéo phụ i + j = d độc lập dữ liệu",
        "15 / 24",
        DOCS_IMG_DIR / "fig_3_1_wavefront_antidiagonal.png",
        "Nguyên lý Wavefront: Các ô trên cùng đường chéo phụ d = i + j chỉ phụ thuộc vào đường chéo d-1 và d-2 → Tính song song đồng thời trên nhiều nhân CPU!",
        "Trong quy hoạch động, ô (i, j) phụ thuộc vào 3 ô (i-1, j), (i, j-1) và (i-1, j-1) nên không thể chạy song song theo hàng ngang hay cột dọc. Tuy nhiên, như hình minh họa lớn trên slide, tất cả các ô nằm trên cùng một đường chéo phụ (i + j = hằng số d) lại hoàn toàn độc lập với nhau! Nhờ đó ta có thể tính song song toàn bộ các ô trên mặt sóng đường chéo d chỉ từ 2 đường chéo liền trước."
    )

    # --------------------------------------------------------------------------
    # SLIDE 16: CHỨNG MINH TOÁN HỌC ĐỘ PHỨC TẠP BỘ NHỚ O(N) & THỜI GIAN 2·NM
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S16"})
    add_top_bar(
        "S16", "PHẦN 3 • PHÂN TÍCH & CHỨNG MINH ĐỘ PHỨC TẠP",
        "Chứng minh Toán học: Bộ nhớ Tuyến tính O(min(m,n)) & Thời gian 2·O(mn)",
        "Tại sao gọi đệ quy log₂(m) tầng trong Chia để trị Myers-Miller KHÔNG làm tăng độ phức tạp thời gian lên O(mn·log m)?",
        "16 / 24"
    )
    add_card_gslides(
        "S16", 24, 66, 330, 326,
        "Định lý 1: Chứng minh Độ phức tạp Bộ nhớ Tuyến tính O(min(m,n))",
        "• Giả sử m ≥ n (nếu m < n, ta hoán đổi vai trò 2 chuỗi).\n\n"
        "• Bộ nhớ Cấp phát tại Mỗi Bước Chia để trị:\n"
        "  Lượt quét xuôi và ngược chỉ dùng 6 mảng 1 chiều kích thước (n + 1):\n"
        "  fwd_M, fwd_Ix, fwd_Iy  và  bwd_M, bwd_Ix, bwd_Iy.\n\n"
        "• Thu hồi / Tái sử dụng Bộ nhớ trước khi Đệ quy:\n"
        "  Ngay sau khi tìm được cột cắt j*, các mảng tạm được giải phóng (hoặc dùng chung buffer tĩnh) TRƯỚC khi gọi đệ quy xuống 2 nửa con.\n"
        "  ⇒ Bộ nhớ KHÔNG cộng dồn theo số nút của cây đệ quy!\n\n"
        "• Ngăn xếp Đệ quy (Call Stack): Tối đa ⌈log₂ m⌉ khung hàm.\n"
        "⇒ S_pair(m, n) = 6(n + 1)·sizeof(int) + O(log m) = O(min(m, n)).\n"
        "⇒ Toàn bộ hệ thống MSA k chuỗi: S_total = O(k · L).",
        hdr_bg="#0284C7", body_bg="#FFFFFF", font_size=9.5
    )
    add_card_gslides(
        "S16", 366, 66, 330, 326,
        "Định lý 2: Chứng minh Thời gian Hội tụ Chuỗi Hình học T(m,n) ≤ 2c·mn",
        "• Mức đệ quy r = 0 (Ma trận gốc m × n):\n"
        "  Quét xuôi nửa trên (m/2 × n) + Quét ngược nửa dưới (m/2 × n)\n"
        "  tốn:  T₀ = c·(m/2)·n + c·(m/2)·n = c · m · n.\n\n"
        "• Mức đệ quy r = 1 (Hai bài toán con kích thước m/2 × j* và m/2 × (n - j*)):\n"
        "  T₁ = c·(m/2)·j* + c·(m/2)·(n - j*) = c · (m/2) · (j* + n - j*)\n"
        "     = ½ (c · m · n)   [Không phụ thuộc vị trí j*!]\n\n"
        "• Tổng thời gian qua tất cả log₂(m) mức đệ quy (Chuỗi hình học công bội ½):\n"
        "  T(m, n) = ∑_{r=0..log₂m} (½)^r · c·mn\n"
        "          = c·mn × (1 + 1/2 + 1/4 + 1/8 + ...) ≤ 2 · c · m · n = O(mn)!",
        hdr_bg="#059669", body_bg="#D1FAE5", font_size=9.5
    )
    ops.append({
        "op": "set-notes", "slide": "S16",
        "text": "Đây là slide chứng minh toán học quan trọng nhất của báo cáo. Bên trái chứng minh bộ nhớ đạt O(min(m,n)) vì các vector 1 chiều được giải phóng trước khi đi vào nhánh đệ quy. Bên phải giải đáp thắc mắc kinh điển: tại sao chia để trị log₂(m) tầng mà thời gian không bị nhân thêm log₂(m)? Nhờ j* + (n - j*) luôn bằng đúng n, tổng diện tích các bài toán con ở mỗi tầng giảm đi đúng một nửa: 1 + 1/2 + 1/4 + 1/8 + ... hội tụ về đúng bằng 2! Tức là thời gian chỉ tăng gấp đôi hằng số (2x) nhưng tiết kiệm bộ nhớ hàng nghìn lần."
    })

    # --------------------------------------------------------------------------
    # SLIDE 17: BẢNG TỔNG HỢP ĐỘ PHỨC TẠP & ĐỊNH LUẬT AMDAHL / GUSTAFSON
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S17"})
    add_top_bar(
        "S17", "PHẦN 3 • TỔNG HỢP ĐỘ PHỨC TẠP",
        "Bảng Tổng hợp Độ phức tạp Toàn Hệ thống & Định luật Amdahl / Gustafson",
        "Đối sánh lý thuyết giữa Baseline và Đề xuất kèm phân tích giới hạn tăng tốc song song",
        "17 / 24"
    )
    ops.append({
        "op": "add-table", "slide": "S17", "rows": 6, "cols": 5, "id": "TBL_COMPLEXITY",
        "x": 24, "y": 66, "width": 672, "height": 185
    })
    t17_headers = ["Giai đoạn / Thuật toán", "Thời gian Tuần tự", "Thời gian Song song", "Bộ nhớ RAM", "Đóng góp & Ý nghĩa"]
    t17_rows = [
        ["Gotoh NW (1982) Baseline", "O(m · n)", "—", "O(m · n) [3 ma trận]", "Tràn RAM khi chuỗi dài m,n ≥ 10⁴"],
        ["Myers-Miller D&C (Đề xuất)", "2 · O(m · n)", "O(m · n / P_wave)", "O(min(m, n)) [1D]", "Giảm >90× – 1.353× RAM, khớp 100%"],
        ["GĐ 1: Ma trận Khoảng cách", "O(k² · N²)", "O(k² · N² / P)", "O(k² + P · N)", "Song song lý tưởng k(k-1)/2 cặp"],
        ["GĐ 2: Cây Hướng dẫn UPGMA", "O(k²)", "O(k²) [Siêu nhanh]", "O(k²)", "Thời gian < 1 ms với k ≤ 100"],
        ["GĐ 3 & 4: Progressive Tree", "O(k · L²)", "O(k · L² / P_tree)", "O(k · L)", "Level-Set Tree + Profile Myers-Miller"]
    ]
    for c_i, h_txt in enumerate(t17_headers):
        ops.append({
            "op": "set-table-cell", "table": "TBL_COMPLEXITY", "row": 0, "col": c_i,
            "text": h_txt, "bold": True, "font_size": 9.5, "color": "#FFFFFF",
            "background_color": "#0F172A", "font_family": "Roboto"
        })
    for r_i, r_data in enumerate(t17_rows):
        is_hi = (r_i in (1, 4))
        bg = "#D1FAE5" if is_hi else ("#FFFFFF" if r_i % 2 == 0 else "#F1F5F9")
        for c_i, val in enumerate(r_data):
            ops.append({
                "op": "set-table-cell", "table": "TBL_COMPLEXITY", "row": r_i + 1, "col": c_i,
                "text": val, "bold": is_hi or (c_i == 0), "font_size": 9,
                "color": "#065F46" if is_hi else "#1E293B",
                "background_color": bg, "font_family": "Roboto"
            })
    add_card_gslides(
        "S17", 24, 260, 330, 132,
        "Định luật Amdahl (Bài toán Kích thước Cố định)",
        "• Công thức cận trên Speedup:  S(P) ≤ 1 / [ (1 - f) + f / P ]\n"
        "• Tại nút gốc của cây UPGMA, 1 luồng phải hợp nhất 2 Profile lớn nhất sau khi chờ các nhánh con hoàn tất → Tạo ra phần tuần tự (1 - f) ≈ 15% – 25%.\n"
        "• Với f = 0.85 và P = 8 luồng → Speedup lý thuyết tối đa ≈ 3.9×.",
        hdr_bg="#1E2761", body_bg="#FFFFFF", font_size=9.5
    )
    add_card_gslides(
        "S17", 366, 260, 330, 132,
        "Định luật Gustafson (Khi Số Chuỗi k Tăng Lớn)",
        "• Công thức mở rộng:  S_scaled(P) = (1 - f_seq) + P · f_par\n"
        "• Khi số chuỗi k tăng lớn (k = 40, 100...), Giai đoạn 1 tính k(k-1)/2 cặp khoảng cách tăng bậc hai O(k²N²) chiếm tỷ trọng áp đảo so với Giai đoạn cây O(kL²) → Tỷ lệ song song hóa f_par tiến sát tới 100%!",
        hdr_bg="#059669", body_bg="#FFFFFF", font_size=9.5
    )
    ops.append({
        "op": "set-notes", "slide": "S17",
        "text": "Bảng tổng hợp trên slide đối chiếu toàn diện độ phức tạp của từng giai đoạn. Không gian bộ nhớ tổng thể của toàn hệ thống chỉ còn O(k*L), tức tuyến tính theo kích thước đầu ra. Ở bên dưới là phân tích hiệu năng song song theo Định luật Amdahl và Gustafson."
    })

    # --------------------------------------------------------------------------
    # SLIDE 18: [FULL-BLEED CHART] THỰC NGHIỆM 1 — NÉN BỘ NHỚ RAM
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S18"})
    add_full_bleed_image_slide(
        "S18", "PHẦN 4 • KẾT QUẢ THỰC NGHIỆM (#1)",
        "Thực nghiệm 1: Kiểm chứng Nén Bộ nhớ Gotoh O(N²) vs. Myers-Miller O(N)",
        "Biểu đồ cột thang đo Logarit (KB) và Hệ số giảm bộ nhớ (×) thực tế trên 5 bộ dữ liệu chuẩn",
        "18 / 24",
        RES_FIG_DIR / "fig1_memory_scaling.png",
        "Kết quả Đột phá: Tại độ dài 897 aa, Gotoh tốn 9.495,7 KB trong khi Myers-Miller chỉ tốn 7,02 KB (Giảm 1.353,5× RAM) — Điểm số khớp 100%!",
        "Bước sang Phần 4 — Thực nghiệm trên bộ dữ liệu chuẩn quốc tế BAliBASE 3.0. Biểu đồ toàn màn hình đầu tiên đối chiếu dung lượng RAM đỉnh giữa Gotoh truyền thống (cột đỏ) và Myers-Miller của nhóm (cột xanh dương) trên thang đo Logarit, cùng đường màu cam biểu diễn hệ số tiết kiệm bộ nhớ. Khi chuỗi dài 897 amino acid, bộ nhớ giảm từ 9,5 MB xuống chỉ còn 7 KB — tiết kiệm gấp 1.353,5 lần và điểm số khớp tuyệt đối 100%!"
    )

    # --------------------------------------------------------------------------
    # SLIDE 19: [FULL-BLEED CHART] THỰC NGHIỆM 2 — TĂNG TỐC SONG SONG OPENMP
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S19"})
    add_full_bleed_image_slide(
        "S19", "PHẦN 4 • KẾT QUẢ THỰC NGHIỆM (#2)",
        "Thực nghiệm 2: Tốc độ Tăng tốc Đa luồng OpenMP (Speedup 1 → 8 Luồng)",
        "Đối chiếu đường tăng tốc thực nghiệm với đường tuyến tính lý tưởng S(p)=p và cận trên Định luật Amdahl",
        "19 / 24",
        RES_FIG_DIR / "fig2_speedup_scaling.png",
        "Trên họ gen lớn BB20001 (RV20) và 40 chuỗi (780 cặp): Thời gian giảm từ 5.423 ms xuống 3.360 ms — Đạt Speedup cực đại 1,73×!",
        "Biểu đồ toàn màn hình thứ hai thể hiện hệ số tăng tốc Speedup khi chạy trên 1, 2, 4 và 8 luồng OpenMP. Trên các tập dữ liệu lớn như BB20001 (đường xanh dương) và Benchmark 40 chuỗi gồm 780 cặp (đường xanh lá), hệ thống đạt Speedup từ 1,61x đến 1,73x, bám sát quy luật của Định luật Amdahl."
    )

    # --------------------------------------------------------------------------
    # SLIDE 20: [FULL-BLEED CHART] THỰC NGHIỆM 3 — ĐỘ CHÍNH XÁC SINH HỌC BALIBASE 3.0
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S20"})
    add_full_bleed_image_slide(
        "S20", "PHẦN 4 • KẾT QUẢ THỰC NGHIỆM (#3)",
        "Thực nghiệm 3: Đánh giá Độ chính xác Sinh học (SP & TC Score) trên BAliBASE 3.0",
        "Đối chiếu tự động kết quả căn chỉnh với cấu trúc tinh thể học 3D chuẩn trên 3 phân vùng RV11, RV12, RV20",
        "20 / 24",
        RES_FIG_DIR / "fig3_balibase_accuracy.png",
        "Đạt độ chính xác xuất sắc trên RV12 (SP trung bình = 86,8%, TC = 68,1%); riêng mẫu BB11001 đạt SP = 98,2%, TC = 96,5%!",
        "Biểu đồ toàn màn hình thứ ba đánh giá chất lượng sinh học thông qua 2 chỉ số chuẩn quốc tế: SP Score (tỷ lệ cặp ký tự căn chỉnh đúng) và TC Score (tỷ lệ cột đúng hoàn toàn trên mọi chuỗi). Trên tập RV12 (độ tương đồng trung bình 20-40%), thuật toán đạt kết quả rất cao với SP trung bình 86,8% và TC đạt 68,1%."
    )

    # --------------------------------------------------------------------------
    # SLIDE 21: [FULL-BLEED CHART] THỰC NGHIỆM 4 — ĐỐI SÁNH CLUSTALW & MUSCLE
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S21"})
    add_full_bleed_image_slide(
        "S21", "PHẦN 4 • KẾT QUẢ THỰC NGHIỆM (#4)",
        "Thực nghiệm 4: Đối sánh với Công cụ Tiêu chuẩn Quốc tế (ClustalW 2.1 & MUSCLE v3.8)",
        "So sánh song song Dung lượng RAM đỉnh (MB) và Độ chính xác Sinh học (SP Score) trên tập BB20001",
        "21 / 24",
        RES_FIG_DIR / "fig4_tools_comparison.png",
        "Nhóm 5 tiêu thụ RAM thấp nhất (26,8 MB — giảm ~45% so với ClustalW 48,5 MB & MUSCLE 52,0 MB) và đạt SP Score (0,488) vượt ClustalW (0,472)!",
        "Biểu đồ kép toàn màn hình này đặt hệ thống của Nhóm 5 cạnh hai công cụ nổi tiếng thế giới là ClustalW 2.1 và MUSCLE v3.8. Ở biểu đồ (A) bên trái, hệ thống của nhóm tốn ít RAM nhất (chỉ 26,8 MB so với ~50 MB của ClustalW/MUSCLE và 320 MB của Gotoh). Ở biểu đồ (B) bên phải, điểm chính xác sinh học SP của nhóm đạt 0,488 — vượt qua ClustalW (0,472) và tiệm cận sát MUSCLE (0,495)."
    )

    # --------------------------------------------------------------------------
    # SLIDE 22: [FULL-BLEED UI 1] WEB GUI — MA TRẬN CĂN CHỈNH MÀU HÓA HỌC
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S22"})
    add_full_bleed_image_slide(
        "S22", "PHẦN 5 • HỆ THỐNG WEB GUI STUDIO (1/2)",
        "Giao diện Web GUI Studio: Ma trận Căn chỉnh Màu Hóa học & Biểu đồ Bảo tồn",
        "Trực quan hóa theo chuẩn Jalview / ClustalX (Kỵ nước: Xanh lam, Điện tích dương: Đỏ, Âm: Tím) kèm Conservation Histogram",
        "22 / 24",
        DOCS_IMG_DIR / "fig_5_1_web_alignment_matrix.png",
        "Hỗ trợ 4 Demo Presets (BAliBASE RV11, RV12, Hemoglobin, Long Seq), tuỳ chỉnh số luồng OpenMP (1–8), Gap Open/Extend và xuất FASTA/Newick",
        "Để giúp người dùng sinh học dễ dàng phân tích kết quả, nhóm xây dựng ứng dụng Web GUI Studio. Hình chụp toàn màn hình này hiển thị Ma trận căn chỉnh được mã màu theo tính chất hóa lý của từng Amino Acid cùng thanh biểu đồ cột mức độ bảo tồn ở phía dưới."
    )

    # --------------------------------------------------------------------------
    # SLIDE 23: [FULL-BLEED UI 2] WEB GUI — CÂY UPGMA SVG & BENCHMARK DASHBOARD
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S23"})
    add_top_bar(
        "S23", "PHẦN 5 • HỆ THỐNG WEB GUI STUDIO (2/2) & LIVE DEMO",
        "Trực quan hóa Cây Phát sinh UPGMA SVG & Bảng Điều khiển Benchmark Đa luồng",
        "Tích hợp đồ họa vector tương tác (Zoom/Pan) và đo đạc Speedup / Memory Reduction thời gian thực",
        "23 / 24"
    )
    # Two large side-by-side screenshots (each taking half of the 720pt width!)
    ops.append({"op": "add-shape", "slide": "S23", "shape_type": "RECTANGLE", "x": 20, "y": 64, "width": 334, "height": 298, "background_color": "#FFFFFF"})
    ops.append({"op": "add-shape", "slide": "S23", "shape_type": "RECTANGLE", "x": 366, "y": 64, "width": 334, "height": 298, "background_color": "#FFFFFF"})
    ix1, iy1, iw1, ih1 = fit_box(DOCS_IMG_DIR / "fig_5_2_web_guide_tree.png", 24, 68, 326, 290)
    ix2, iy2, iw2, ih2 = fit_box(DOCS_IMG_DIR / "fig_5_3_web_benchmark_dashboard.png", 370, 68, 326, 290)
    image_uploads.append(("S23", str(DOCS_IMG_DIR / "fig_5_2_web_guide_tree.png"), ix1, iy1, iw1, ih1))
    image_uploads.append(("S23", str(DOCS_IMG_DIR / "fig_5_3_web_benchmark_dashboard.png"), ix2, iy2, iw2, ih2))
    ops.append({
        "op": "add-textbox", "slide": "S23",
        "text": "Kịch bản Live Demo (90s): Chọn Preset BAliBASE RV12 → Bật Baseline Compare & 4 Threads → Quan sát Ma trận màu, Cây UPGMA & Thẻ giảm RAM >700×",
        "x": 20, "y": 368, "width": 680, "height": 28,
        "font_size": 9.8, "bold": True, "color": "#FFFFFF",
        "background_color": "#0284C7", "font_family": "Roboto", "content_alignment": "MIDDLE"
    })
    ops.append({
        "op": "set-notes", "slide": "S23",
        "text": "Slide này hiển thị rõ nét 2 phân hệ tiếp theo trên Web GUI: Bên trái là Cây hướng dẫn UPGMA vẽ bằng đồ họa vector SVG cho phép phóng to/thu nhỏ và xem khoảng cách tiến hóa trên từng nhánh. Bên phải là Dashboard đo đạc trực tiếp đồ thị Speedup từ 1 đến 8 luồng và thẻ đối chứng bộ nhớ Gotoh vs Myers-Miller. Ngay sau đây nhóm xin phép thực hiện Live Demo nhanh trên trình duyệt."
    })

    # --------------------------------------------------------------------------
    # SLIDE 24: KẾT LUẬN, KIỂM THỬ TỰ ĐỘNG (342 TESTS) & HƯỚNG PHÁT TRIỂN (DARK)
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "S24"})
    add_top_bar(
        "S24", "PHẦN 5 • KẾT LUẬN & HƯỚNG PHÁT TRIỂN",
        "Tổng kết Đóng góp Khoa học, Kiểm thử Tự động & Hướng Phát triển",
        "Giải quyết trọn vẹn bài toán MSA bằng Chia để trị Tuyến tính O(k·L) kết hợp Song song hóa Đa tầng",
        "24 / 24", dark_mode=True
    )
    add_card_gslides(
        "S24", 24, 66, 330, 275,
        "1. Bốn Kết quả & Đóng góp Cốt lõi Đã Đạt được",
        "① Tối ưu Bộ nhớ Tuyến tính O(min(m, n)):\n"
        "   Thiết kế hoàn chỉnh Myers-Miller + Profile-to-Profile, giảm bộ nhớ tới 1.353,5× RAM và đạt điểm số trùng khớp 100% với Gotoh NW.\n\n"
        "② Tăng tốc Song song Đa tầng (OpenMP + MPI):\n"
        "   Đạt Speedup 1,73× trên CPU đa nhân và hỗ trợ mở rộng cụm HPC.\n\n"
        "③ Độ chính xác Sinh học Cao trên BAliBASE 3.0:\n"
        "   Đạt SP = 86,8% trên RV12, tốn ít hơn ~45% RAM so với ClustalW & MUSCLE.\n\n"
        "④ Độ tin cậy Phần mềm C++17 Tuyệt đối:\n"
        "   Vượt qua 108/108 Unit Tests (139.463 assertions) + 234/234 E2E Tests.",
        hdr_bg="#059669", body_bg="#FFFFFF", font_size=9.5
    )
    add_card_gslides(
        "S24", 366, 66, 330, 275,
        "2. Ba Hướng Phát triển Mở rộng Tương lai",
        "① Tinh chỉnh Lặp (Iterative Refinement):\n"
        "   Cắt đôi cây UPGMA và căn chỉnh lại Profile (kiểu MUSCLE/MAFFT) để khắc phục hạn chế 'Once a gap, always a gap' và nâng điểm TC trên RV20.\n\n"
        "② Vector hóa Phần cứng SIMD (AVX-512) & GPU CUDA:\n"
        "   Tăng tốc phép tính tích vô hướng tần suất cột PSP(x,y) và đẩy mặt sóng Wavefront lên hàng nghìn nhân GPU.\n\n"
        "③ Mô hình Điểm số Thích nghi (Adaptive Matrix):\n"
        "   Tự động chọn ma trận BLOSUM80 / BLOSUM62 / BLOSUM45 tùy theo khoảng cách tiến hóa của từng nhánh cây UPGMA.",
        hdr_bg="#0284C7", body_bg="#FFFFFF", font_size=9.5
    )
    ops.append({
        "op": "add-textbox", "slide": "S24",
        "text": "CẢM ƠN THẦY/CÔ VÀ CÁC BẠN ĐÃ LẮNG NGHE!  •  NHÓM 5 XIN TRÂN TRỌNG ĐÓN NHẬN CÂU HỎI PHẢN BIỆN",
        "x": 24, "y": 352, "width": 672, "height": 38,
        "font_size": 12, "bold": True, "color": "#FFFFFF",
        "background_color": "#0284C7", "font_family": "Roboto",
        "alignment": "center", "content_alignment": "MIDDLE"
    })
    ops.append({
        "op": "set-notes", "slide": "S24",
        "text": "Slide cuối cùng tổng kết 4 đóng góp khoa học và kỹ thuật của Nhóm 5 cùng 3 hướng phát triển mở rộng. Cảm ơn Thầy/Cô và các bạn đã lắng nghe, nhóm rất mong nhận được các câu hỏi và góp ý từ Hội đồng!"
    })

    # --------------------------------------------------------------------------
    # BACKUP SLIDES B1, B2, B3 (PHỤ LỤC PHẢN BIỆN)
    # --------------------------------------------------------------------------
    ops.append({"op": "add-slide", "layout": "BLANK", "id": "SB1"})
    add_top_bar(
        "SB1", "PHỤ LỤC PHẢN BIỆN • BACKUP Q&A #1",
        "[Q&A Lý thuyết] Xử lý Khoảng trống Xuyên qua Nhát cắt Giữa (Gap Coalescing)",
        "Tại sao chia đôi ma trận tại dòng i* = ⌊m/2⌋ không làm phạt mở khoảng trống G_open (-10) hai lần?",
        "B1 / 3"
    )
    add_card_gslides(
        "SB1", 24, 66, 672, 326,
        "Giải thích Toán học Phương trình Hợp nhất Khoảng trống tại Ranh giới i* = ⌊m/2⌋",
        "• Câu hỏi: Nếu đường căn chỉnh tối ưu đang nằm trong một khoảng trống mở từ nửa trên kéo dài xuyên qua dòng i* xuống nửa dưới, làm sao thuật toán không tính phạt G_open hai lần?\n\n"
        "• Công thức ghép trạng thái tại dòng giữa i*:\n"
        "  Score(j) = max {\n"
        "      ① Khớp / Thay thế qua ranh giới:      Fwd_M(j)  + Bwd_M(j),\n"
        "      ② Khoảng trống xuyên qua ranh giới:   Fwd_Ix(j) + Bwd_Ix(j) - G_open + G_ext\n"
        "  }\n\n"
        "• Chứng minh: Một khoảng trống độ dài g = g₁ + g₂ có chi phí thực là G_open + (g₁ + g₂ - 1)·G_ext.\n"
        "  Nhưng Fwd_Ix(j) + Bwd_Ix(j) đã tính [G_open + (g₁ - 1)·G_ext] + [G_open + (g₂ - 1)·G_ext] = 2·G_open + (g₁ + g₂ - 2)·G_ext.\n"
        "  ⇒ Phép hiệu chỉnh (-G_open + G_ext) triệt tiêu chính xác 1 lần G_open dư thừa và nối 2 nửa thành 1 khoảng trống liên tục duy nhất!",
        hdr_bg="#1E2761", body_bg="#FFFFFF", font_size=10.2
    )
    ops.append({"op": "set-notes", "slide": "SB1", "text": "Slide dự phòng phản biện số 1 giải thích kỹ thuật Gap Coalescing trong Myers-Miller."})

    ops.append({"op": "add-slide", "layout": "BLANK", "id": "SB2"})
    add_top_bar(
        "SB2", "PHỤ LỤC PHẢN BIỆN • BACKUP Q&A #2",
        "[Q&A Thực nghiệm] Tại sao TC Score trên RV20 bằng 0 dù SP Score đạt tới 92%?",
        "Sự khác biệt toán học giữa thước đo SP Score vs. TC Score và đặc trưng của Progressive MSA",
        "B2 / 3"
    )
    add_card_gslides(
        "SB2", 24, 66, 672, 326,
        "Phân tích Thước đo Total Column (TC Score) trên các Họ Gen Lớn (RV20 — 16 đến 40 chuỗi)",
        "• Định nghĩa Toán học của 2 Thước đo BAliBASE:\n"
        "  - SP Score (Sum-of-Pairs): Tỷ lệ CẶP ký tự căn chỉnh đúng so với chuẩn Reference.\n"
        "  - TC Score (Total Column): Tỷ lệ CỘT mà TẤT CẢ 100% các chuỗi trong cột đó đều khớp đồng thời với chuẩn Reference.\n\n"
        "• Tại sao trên BB20003 (RV20), SP đạt 0,920 (92% số cặp đúng) nhưng TC = 0,000?\n"
        "  1. Tập RV20 chứa một họ lớn các chuỗi rất giống nhau kèm theo 1–2 chuỗi 'mồ côi' (orphan sequences) cực kỳ phân kỳ.\n"
        "  2. Hệ thống đã căn chỉnh đúng tuyệt đối nhóm chuỗi chính (nên 92% tổng số cặp ký tự trùng khớp chuẩn), nhưng khi ghép chuỗi ngoại lai cuối cùng ở gốc cây UPGMA, chuỗi đó bị lệch đi 1 vị trí gap → Làm điểm TC nhị phân (0 hoặc 1) của cột đó lập tức về 0!\n"
        "  3. Đây là hạn chế kinh điển của phương pháp Progressive 1 lượt ('Once a gap, always a gap') khi chưa có bước hậu kiểm Iterative Refinement.",
        hdr_bg="#7C3AED", body_bg="#FFFFFF", font_size=10.2
    )
    ops.append({"op": "set-notes", "slide": "SB2", "text": "Slide dự phòng phản biện số 2 giải thích tại sao TC Score trên RV20 bằng 0 dù SP Score đạt 92%."})

    ops.append({"op": "add-slide", "layout": "BLANK", "id": "SB3"})
    add_top_bar(
        "SB3", "PHỤ LỤC PHẢN BIỆN • BACKUP Q&A #3",
        "[Q&A Song song hóa] Tại sao Speedup Bão hòa quanh mức 1,61× – 1,73× ở 8 Luồng?",
        "Phân tích Nút thắt Hình thái Cây UPGMA (Tree Topology) và Băng thông Bộ nhớ Đệm (Memory Bandwidth)",
        "B3 / 3"
    )
    add_card_gslides(
        "SB3", 24, 66, 672, 326,
        "Hai Nguyên nhân Vật lý & Thuật toán Giới hạn Speedup Đa luồng trên 1 Socket CPU",
        "1. Nút thắt Hình thái Cây Nhị phân ở Tầng Gốc (Root-Level Serialization):\n"
        "   • Khi duyệt cây UPGMA từ dưới lên, số lượng nhánh độc lập thu hẹp dần: ở tầng sát gốc chỉ còn 2 nút, và tại nút gốc chỉ còn đúng 1 phép hợp nhất Profile.\n"
        "   • Tuy nhiên, nút gốc lại chứa nhiều chuỗi nhất (tích |P₁|×|P₂| lớn nhất), chiếm ~15%–20% tổng thời gian toàn cục nhưng chỉ có 1 luồng làm việc trong khi 7 luồng còn lại chờ.\n\n"
        "2. Giới hạn Băng thông Bộ nhớ (Memory-Bound Kernel):\n"
        "   • Vòng lặp tính điểm cột PSP(x, y) đọc liên tục vector tần suất 20 phần tử từ RAM với mật độ phép tính số học trên mỗi byte thấp.\n"
        "   • Khi 8 luồng cùng quét tốc độ cao trên cùng 1 chip CPU, băng thông bộ nhớ đệm L3 Cache đạt ngưỡng bão hòa.",
        hdr_bg="#D97706", body_bg="#FFFFFF", font_size=10.2
    )
    ops.append({"op": "set-notes", "slide": "SB3", "text": "Slide dự phòng phản biện số 3 giải thích hiện tượng bão hòa Speedup ở 8 luồng OpenMP."})

    BATCH_JSON_PATH.write_text(json.dumps(ops, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[GENERATED] {BATCH_JSON_PATH} with {len(ops)} batch operations and {len(image_uploads)} image uploads.")
    return image_uploads


def execute_gslides_build(image_uploads):
    print("[RUNNING] gslides mutate batch...")
    res = subprocess.run(
        [GSLIDES_CMD, "mutate", "batch", PRES_ID, "-f", str(BATCH_JSON_PATH), "--json"],
        capture_output=True, text=True, encoding="utf-8"
    )
    if res.returncode != 0:
        print("[ERROR] gslides mutate batch failed:")
        print(res.stderr)
        print(res.stdout)
        raise RuntimeError("gslides mutate batch failed")

    data = json.loads(res.stdout.strip().splitlines()[-1])
    resolved = data.get("resolved_ids", {})
    print(f"[SUCCESS] Batch completed. Resolved {len(resolved)} slide/table IDs.")

    # Upload all local high-res figures to their respective slides
    for placeholder_id, img_path, x, y, w, h in image_uploads:
        real_slide_id = resolved.get(placeholder_id, placeholder_id)
        print(f"  -> Uploading {Path(img_path).name} to {placeholder_id} ({real_slide_id}) at ({x}, {y}, {w}x{h})...")
        up_res = subprocess.run(
            [
                GSLIDES_CMD, "mutate", "insert-image-from-file", PRES_ID,
                "--slide", real_slide_id,
                "--file", img_path,
                "--x", str(x), "--y", str(y),
                "--width", str(w), "--height", str(h)
            ],
            capture_output=True, text=True, encoding="utf-8"
        )
        if up_res.returncode != 0:
            print(f"  [WARN] Failed to upload {img_path}: {up_res.stderr}")


# ==============================================================================
# PART 2: GENERATE MATCHING HIGH-RES LOCAL PPTX V2 (13.333 x 7.5 inches)
# ==============================================================================
def build_local_pptx_v2():
    """
    Mirrors the exact 27-slide v2 structure (with 3-slide Biology/Problem intro
    and Full-Bleed 85-90% diagram/chart slides) directly into a crisp native .pptx
    using python-pptx so the user has both the Google Slides online link and local file.
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    with open(BATCH_JSON_PATH, "r", encoding="utf-8") as f:
        ops = json.load(f)

    # Scale factor from Google Slides (720 x 405 pt) to PPTX (13.333 x 7.5 inches):
    # 13.3333 / 720 = 1 / 54 inches per pt!
    # And 1 pt in Google Slides (on a 720pt canvas) corresponds to (960 / 720) = 1.3333x font size on a 960pt (13.333in) PPTX canvas!
    SCALE_IN = 13.3333 / 720.0
    FONT_SCALE = 1.32

    def hex_to_rgb(h):
        h = h.lstrip("#")
        return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    slides_map = {}
    tables_map = {}

    # Create initial slide 'p'
    slides_map["p"] = prs.slides.add_slide(blank)

    for op_item in ops:
        op = op_item["op"]
        if op == "delete-element":
            continue
        elif op == "add-slide":
            sid = op_item["id"]
            slides_map[sid] = prs.slides.add_slide(blank)
        elif op == "set-background":
            sl = slides_map[op_item["slide"]]
            bg = sl.background
            fill = bg.fill
            fill.solid()
            fill.fore_color.rgb = hex_to_rgb(op_item["color"])
        elif op == "add-shape":
            sl = slides_map[op_item["slide"]]
            x = Inches(op_item["x"] * SCALE_IN)
            y = Inches(op_item["y"] * SCALE_IN)
            w = Inches(op_item["width"] * SCALE_IN)
            h = Inches(op_item["height"] * SCALE_IN)
            sh = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
            sh.fill.solid()
            sh.fill.fore_color.rgb = hex_to_rgb(op_item.get("background_color", "#FFFFFF"))
            sh.line.color.rgb = hex_to_rgb("#CBD5E1") if op_item.get("background_color") == "#FFFFFF" else hex_to_rgb(op_item.get("background_color", "#FFFFFF"))
            sh.line.width = Pt(1.0)
        elif op == "add-textbox":
            sl = slides_map[op_item["slide"]]
            x = Inches(op_item["x"] * SCALE_IN)
            y = Inches(op_item["y"] * SCALE_IN)
            w = Inches(op_item["width"] * SCALE_IN)
            h = Inches(op_item["height"] * SCALE_IN)
            bg_hex = op_item.get("background_color")
            if bg_hex and bg_hex != "transparent":
                sh = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
                sh.fill.solid()
                sh.fill.fore_color.rgb = hex_to_rgb(bg_hex)
                if bg_hex.upper() == "#FFFFFF":
                    sh.line.color.rgb = RGBColor(203, 213, 225)
                    sh.line.width = Pt(1.0)
                else:
                    sh.line.fill.background()
                tf = sh.text_frame
                tf.margin_left = Inches(0.14)
                tf.margin_right = Inches(0.14)
                tf.margin_top = Inches(0.08)
                tf.margin_bottom = Inches(0.08)
            else:
                tb = sl.shapes.add_textbox(x, y, w, h)
                tf = tb.text_frame
                tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0

            tf.word_wrap = True
            v_align = op_item.get("content_alignment", "TOP")
            if v_align == "MIDDLE":
                tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            elif v_align == "BOTTOM":
                tf.vertical_anchor = MSO_ANCHOR.BOTTOM
            else:
                tf.vertical_anchor = MSO_ANCHOR.TOP

            lines = op_item["text"].split("\n")
            f_fam = "Consolas" if "Mono" in op_item.get("font_family", "") else "Segoe UI"
            f_sz = Pt(op_item.get("font_size", 11) * FONT_SCALE)
            f_bold = op_item.get("bold", False)
            f_ital = op_item.get("italic", False)
            f_col = hex_to_rgb(op_item.get("color", "#000000"))
            h_align = op_item.get("alignment", "left")

            for l_idx, line_str in enumerate(lines):
                p = tf.paragraphs[0] if l_idx == 0 else tf.add_paragraph()
                p.text = line_str
                p.font.name = f_fam
                p.font.size = f_sz
                p.font.bold = f_bold or line_str.strip().startswith(("•", "①", "②", "③", "④", "1.", "2.", "3.", "4.", "-", "✅", "❌", "⇒"))
                p.font.italic = f_ital
                p.font.color.rgb = f_col
                p.space_after = Pt(2)
                if h_align == "center":
                    p.alignment = PP_ALIGN.CENTER
                elif h_align == "right":
                    p.alignment = PP_ALIGN.RIGHT
                else:
                    p.alignment = PP_ALIGN.LEFT
        elif op == "add-table":
            sl = slides_map[op_item["slide"]]
            x = Inches(op_item["x"] * SCALE_IN)
            y = Inches(op_item["y"] * SCALE_IN)
            w = Inches(op_item["width"] * SCALE_IN)
            h = Inches(op_item["height"] * SCALE_IN)
            t_sh = sl.shapes.add_table(op_item["rows"], op_item["cols"], x, y, w, h)
            tables_map[op_item["id"]] = t_sh.table
        elif op == "set-table-cell":
            tbl = tables_map[op_item["table"]]
            cell = tbl.cell(op_item["row"], op_item["col"])
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if "background_color" in op_item:
                cell.fill.solid()
                cell.fill.fore_color.rgb = hex_to_rgb(op_item["background_color"])
            p = cell.text_frame.paragraphs[0]
            p.text = op_item["text"]
            p.font.name = "Segoe UI"
            p.font.size = Pt(op_item.get("font_size", 9.5) * FONT_SCALE)
            p.font.bold = op_item.get("bold", False)
            p.font.color.rgb = hex_to_rgb(op_item.get("color", "#000000"))
            p.alignment = PP_ALIGN.CENTER if op_item["col"] > 0 else PP_ALIGN.LEFT
        elif op == "set-notes":
            sl = slides_map[op_item["slide"]]
            sl.notes_slide.notes_text_frame.text = op_item["text"]

    # Insert all high-res images into the local PPTX slides
    return prs, slides_map, SCALE_IN


if __name__ == "__main__":
    uploads = generate_gslides_batch()
    prs, slides_map, scale_in = build_local_pptx_v2()
    for s_id, img_path, x, y, w, h in uploads:
        sl = slides_map[s_id]
        sl.shapes.add_picture(
            img_path,
            Inches(x * scale_in),
            Inches(y * scale_in),
            width=Inches(w * scale_in),
            height=Inches(h * scale_in)
        )
    prs.save(str(OUTPUT_PPTX_V2))
    print(f"[SUCCESS] Local PowerPoint v2 saved: {OUTPUT_PPTX_V2}")
    execute_gslides_build(uploads)
    print(f"[ALL DONE] Google Slides URL: https://docs.google.com/presentation/d/{PRES_ID}/edit")
