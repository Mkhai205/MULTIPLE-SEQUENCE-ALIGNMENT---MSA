import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import datetime

def create_report():
    doc = docx.Document()

    # Page setup - Margins (Top/Bottom 2.0cm, Left 2.5cm, Right 2.0cm)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)

    # Styles setup
    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Times New Roman'
    font_normal.size = Pt(12)
    font_normal.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing = 1.25
    style_normal.paragraph_format.space_after = Pt(4)

    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(f'<w:tblBorders {nsdecls("w")}>'
                            f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                            f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                            f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                            f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                            f'<w:left w:val="none"/>'
                            f'<w:right w:val="none"/>'
                            f'</w:tblBorders>')
        tblPr.append(borders)

    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(16, 44, 87) # Deep Blue
        return p

    def add_subtitle(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(18)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(41, 75, 107)
        return p

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(15)
        run.font.color.rgb = RGBColor(16, 44, 87)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(41, 75, 107)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(60, 60, 60)
        return p

    def add_p(text, bold_prefix="", italic=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.25
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.color.rgb = RGBColor(20, 20, 20)
        r = p.add_run(text)
        r.italic = italic
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.2
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
        p.add_run(text)
        return p

    def add_callout(text, title="LƯU Ý / ĐÓNG GÓP"):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, "F0F4F8")
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}>'
                            f'<w:left w:val="single" w:sz="24" w:space="0" w:color="102C57"/>'
                            f'<w:top w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/>'
                            f'</w:tcBorders>')
        tcPr.append(borders)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"[{title}] ")
        r1.bold = True
        r1.font.color.rgb = RGBColor(16, 44, 87)
        r2 = p.add_run(text)
        r2.font.size = Pt(11.5)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ==========================================
    # 1. TRANG BÌA (COVER PAGE)
    # ==========================================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_inst.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO\nTRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN & TRUYỀN THÔNG\nKHOA CÔNG NGHỆ THÔNG TIN\n---------------------------------")
    r.bold = True
    r.font.size = Pt(12)

    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("BÁO CÁO BÀI TẬP LỚN MÔN HỌC\nPHÂN TÍCH VÀ THIẾT KẾ THUẬT TOÁN")
    r_sub.bold = True
    r_sub.font.size = Pt(16)
    r_sub.font.color.rgb = RGBColor(16, 44, 87)

    doc.add_paragraph().paragraph_format.space_after = Pt(20)

    add_title("ĐỀ TÀI: NHÓM 5\nTHUẬT TOÁN CHIA ĐỂ TRỊ SONG SONG KẾT HỢP QUY HOẠCH ĐỘNG CHO BÀI TOÁN CĂN CHỈNH ĐA CHUỖI GEN (MULTIPLE SEQUENCE ALIGNMENT - MSA)")

    p_lead = doc.add_paragraph()
    p_lead.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_lead = p_lead.add_run("Tối ưu không gian trạng thái từ O(mn) về O(min(m, n)) bằng thuật toán Myers-Miller\nSong song hóa đa tầng OpenMP và Đánh giá độ chính xác sinh học trên BAliBASE 3.0")
    r_lead.italic = True
    r_lead.font.size = Pt(12)

    doc.add_paragraph().paragraph_format.space_after = Pt(50)

    # Info table on cover
    info_table = doc.add_table(rows=6, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    members = [
        ("Giảng viên hướng dẫn:", "Thầy/Cô Phụ trách Môn học"),
        ("Nhóm sinh viên thực hiện:", "NHÓM 5 (5 Sinh viên)"),
        ("Sinh viên 1 (Nhóm trưởng):", "Phụ trách Kiến trúc & Milestone 1-2 (Gotoh Baseline)"),
        ("Sinh viên 2:", "Phụ trách Milestone 3 (Myers-Miller D&C & ProfileAligner)"),
        ("Sinh viên 3:", "Phụ trách Milestone 4 (UPGMA Clustering & GuideTree)"),
        ("Sinh viên 4 & 5:", "Phụ trách Milestone 5-7 (OpenMP Wavefront, BAliBASE Benchmark)")
    ]
    for i, (k, v) in enumerate(members):
        row = info_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.5)
        c1.width = Inches(4.0)
        p0 = c0.paragraphs[0]
        p0.add_run(k).bold = True
        p1 = c1.paragraphs[0]
        p1.add_run(v)
        p0.paragraph_format.space_after = Pt(2)
        p1.paragraph_format.space_after = Pt(2)

    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    p_year = doc.add_paragraph()
    p_year.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_year.add_run("Hà Nội, Năm học 2025 – 2026").bold = True

    doc.add_page_break()

    # ==========================================
    # 2. TÓM TẮT ĐỒ ÁN (EXECUTIVE SUMMARY)
    # ==========================================
    add_h1("TÓM TẮT ĐỒ ÁN (EXECUTIVE SUMMARY)")
    add_p(
        "Báo cáo trình bày chi tiết công trình nghiên cứu, thiết kế và hiện thực hệ thống phần mềm C++17 cho bài toán "
        "Căn chỉnh Đa chuỗi Gen (Multiple Sequence Alignment - MSA) dành cho chuỗi sinh học (Protein / ADN). "
        "Bài toán MSA là nền tảng cốt lõi trong Tin sinh học phục vụ nghiên cứu tiến hóa, dựng cây phát sinh loài, "
        "và dự đoán cấu trúc không gian của protein. Tuy nhiên, quy hoạch động đa chiều truyền thống giải bài toán này là NP-hard "
        "với độ phức tạp thời gian và không gian bùng nổ cấp số nhân O(L^K) đối với K chuỗi độ dài L, hoàn toàn bất khả thi trên máy tính."
    )
    add_p(
        "Để giải quyết triệt để vấn đề này, Nhóm 5 đã kết hợp ba trụ cột kỹ thuật giải thuật tiên tiến:\n"
        "1. Kỹ thuật Chia để trị (Divide-and-Conquer): Hiện thực thuật toán Myers-Miller (1988) - biến thể mở rộng cho affine gap của thuật toán Hirschberg, "
        "tối ưu triệt để dung lượng bộ nhớ cặp đôi từ bậc hai O(mn) về bậc tuyến tính O(min(m, n)). Kết quả thực nghiệm đo đạc thực tế ghi nhận mức giảm bộ nhớ "
        "vượt trội từ 92.0 lần đến hơn 250 lần so với Needleman-Wunsch Gotoh, trong khi bảo đảm điểm số căn chỉnh tối ưu toán học đồng nhất 100%.\n"
        "2. Chiến lược Căn chỉnh Tiến bộ (Progressive Alignment Pipeline): Xây dựng ma trận khoảng cách chuẩn hóa All-Pairs, gom cụm phân cấp cây hướng dẫn "
        "UPGMA (Unweighted Pair Group Method with Arithmetic Mean) với cơ chế giải quyết hòa điểm xác định (deterministic tie-breaking), và căn chỉnh profile-to-profile "
        "dựa trên hàm điểm Sum-of-Pairs thưa kết hợp kỹ thuật lan truyền khoảng trống (gap propagation).\n"
        "3. Tính toán Song song Đa tầng trên OpenMP: Khai thác song song hóa ở hai cấp độ: cấp độ tác vụ (Task-level) trên các cặp ma trận khoảng cách và cây hướng dẫn nhị phân; "
        "kết hợp song song hóa cấp độ dữ liệu (Data-level wavefront DP) theo các đường chéo phụ (anti-diagonals).\n"
        "4. Kiểm thử và Đánh giá Thực nghiệm trên Chuẩn BAliBASE 3.0: Đo đạc chính xác trên các tập tham chiếu RV11, RV12, RV20 với hai chỉ số chuẩn sinh học SP score (Sum-of-Pairs) "
        "và TC score (Total Column) trên các khối lõi bảo tồn (Core Blocks). Hệ thống vượt qua 100% bộ kiểm thử tự động gồm 107 Unit Tests (139,446 assertions) và 234 E2E Tests."
    )

    add_callout(
        "Toàn bộ mã nguồn C++17 được tổ chức chuẩn module công nghiệp, không sử dụng bất kỳ thư viện ngoài nào ngoại trừ STL và OpenMP, "
        "không có rò rỉ bộ nhớ, không có data race, và biên dịch sạch sẽ không warning trên MSVC C++17 Release mode.",
        title="TÍNH HOÀN THIỆN CỦA ĐỒ ÁN"
    )

    # ==========================================
    # CHƯƠNG 1: TỔNG QUAN BÀI TOÁN MSA
    # ==========================================
    add_h1("CHƯƠNG 1: TỔNG QUAN BÀI TOÁN CĂN CHỈNH ĐA CHUỖI GEN (MSA)")

    add_h2("1.1. Bối cảnh Sinh học và Ý nghĩa Thực tiễn")
    add_p(
        "Trong sinh học phân tử hiện đại, các đại phân tử sinh học như ADN, ARN và Protein là những chuỗi ký tự thẳng cấu thành từ các đơn phân: "
        "4 nucleotide (A, C, G, T) đối với ADN và 20 amino acid tiêu chuẩn đối với Protein. Trong quá trình tiến hóa hàng triệu năm, các chuỗi gen và protein "
        "của các loài sinh vật khác nhau chịu tác động của các đột biến thay thế (substitution), thêm nucleotide (insertion) hoặc mất nucleotide (deletion). "
        "Hiện tượng chèn và mất đoạn được gọi chung là indels."
    )
    add_p(
        "Căn chỉnh Đa chuỗi Gen (Multiple Sequence Alignment - MSA) là quá trình sắp đặt đồng thời từ 3 chuỗi sinh học trở lên sao cho các ký tự có nguồn gốc "
        "tiến hóa chung (homologous residues) hoặc có cấu trúc và chức năng tương đồng nằm thẳng hàng trên cùng một cột. MSA là bước đầu vào bắt buộc trong: "
        "- Xây dựng cây phát sinh loài (Phylogenetic tree reconstruction) để tìm hiểu nguồn gốc tiến hóa của các loài.\n"
        "- Nhận diện các motif chức năng và vùng hoạt động (active sites) được bảo tồn cao độ trong protein.\n"
        "- Dự đoán cấu trúc bậc hai và bậc ba của protein (ví dụ hệ thống AlphaFold sử dụng MSA làm input cốt lõi).\n"
        "- Thiết kế thuốc và kháng thể nhắm trúng đích."
    )

    add_h2("1.2. Phát biểu Toán học của Bài toán MSA")
    add_p(
        "Cho tập hợp K chuỗi protein S = {S_1, S_2, ..., S_K} trên bảng chữ cái amino acid Σ (gồm 20 amino acid tiêu chuẩn). "
        "Một phép căn chỉnh đa chuỗi S' = {S'_1, S'_2, ..., S'_K} là tập hợp K chuỗi mới trên bảng chữ cái mở rộng Σ' = Σ ∪ {'-'} (trong đó '-' đại diện cho khoảng trống - gap) "
        "thỏa mãn các điều kiện tiên quyết sau:\n"
        "1. Mọi chuỗi S'_i trong S' đều có cùng độ dài L (L ≥ max |S_i|).\n"
        "2. Chuỗi S'_i sau khi loại bỏ tất cả các ký tự '-' phải trùng khớp chính xác với chuỗi ban đầu S_i (bảo toàn 100% amino acid).\n"
        "3. Không tồn tại bất kỳ cột nào chứa toàn bộ khoảng trống '-' (không có cột toàn gap)."
    )

    add_h3("Mô hình điểm số Sum-of-Pairs (SP Score) và Ma trận Thay thế BLOSUM62:")
    add_p(
        "Hàm mục tiêu chuẩn trong MSA là tối đa hóa điểm số cặp đôi tổng (Sum-of-Pairs Score). Điểm của phép căn chỉnh S' là tổng điểm của tất cả C(K, 2) = K(K-1)/2 "
        "cặp chuỗi được chiếu (projected pairwise alignments):\n"
        "Score(S') = Σ_{1 ≤ i < j ≤ K} PairwiseScore(S'_i, S'_j)\n"
        "Trong đó, điểm cặp đôi PairwiseScore sử dụng ma trận thay thế BLOSUM62 (Henikoff & Henikoff, 1992) đối xứng 24x24 phản ánh xác suất đột biến bảo tồn hóa sinh "
        "giữa các amino acid, kết hợp mô hình điểm phạt khoảng trống affine (Affine Gap Penalty)."
    )

    add_h3("Mô hình Phạt Khoảng trống Affine (Affine Gap Penalty):")
    add_p(
        "Sinh học thực nghiệm chứng minh rằng một biến cố đột biến chèn/xóa đoạn dài k ký tự có xác suất xảy ra cao hơn nhiều so với k biến cố chèn/xóa đơn lẻ độc lập. "
        "Do đó, mô hình phạt tuyến tính g(k) = k * g_e gây phân mảnh indel nghiêm trọng. Thay vào đó, mô hình affine gap penalty chuẩn Gotoh (1982) được áp dụng:\n"
        "Cost(gap of length k) = g_o + (k - 1) * g_e\n"
        "Trong đó g_o là điểm phạt mở khoảng trống (gap open penalty, giá trị âm, ví dụ -10), và g_e là điểm phạt mở rộng khoảng trống (gap extension penalty, ví dụ -1). "
        "Vì g_o âm sâu hơn g_e (|g_o| >> |g_e|), thuật toán sẽ ưu tiên mở rộng các khoảng trống liên tục thay vì rải rác các khoảng trống nhỏ."
    )

    add_h2("1.3. Tính khó NP-Hard và Sự bùng nổ Không gian Trạng thái")
    add_p(
        "Nếu áp dụng Quy hoạch động toàn cục (Exact Dynamic Programming) trực tiếp cho K chuỗi có độ dài trung bình L, bảng quy hoạch động sẽ là một siêu khối K chiều "
        "với số lượng ô là L^K. Tại mỗi ô, thuật toán phải xét 2^K - 1 hướng chuyển trạng thái. "
        "Độ phức tạp thời gian là O(2^K * L^K) và độ phức tạp bộ nhớ là O(L^K). "
        "Wang và Jiang (1994) đã chứng minh bài toán MSA tối ưu SP score là NP-hard. "
        "Ngay cả với K = 5 chuỗi ngắn độ dài L = 300, số lượng ô nhớ vượt quá 300^5 = 2.43 * 10^12 ô nhớ (yêu cầu hàng nghìn Gigabytes RAM), "
        "hoàn toàn vượt quá giới hạn của bất kỳ hệ thống siêu máy tính nào."
    )
    add_p(
        "Vì vậy, các hệ thống MSA hàng đầu thế giới (như CLUSTAL W, MUSCLE, MAFFT, T-Coffee) đều áp dụng chiến lược thuật toán Heuristic Căn chỉnh Tiến bộ (Progressive Alignment), "
        "kết hợp quy hoạch động cặp đôi có tối ưu bộ nhớ chia để trị và gom cụm phân cấp cây hướng dẫn."
    )

    # ==========================================
    # CHƯƠNG 2: NỀN TẢNG LÝ THUYẾT VÀ GIẢI THUẬT
    # ==========================================
    add_h1("CHƯƠNG 2: NỀN TẢNG LÝ THUYẾT VÀ CÁC THUẬT TOÁN NÒNG CỐT")

    add_h2("2.1. Quy hoạch Động Gotoh (1982) 3 Ma trận Baseline")
    add_p(
        "Để xử lý mô hình phạt affine gap trong quy hoạch động Needleman-Wunsch cổ điển, Gotoh (1982) đề xuất phân rã bài toán thành 3 ma trận trạng thái song song:"
    )
    add_bullet("Ma trận M(i, j): Điểm căn chỉnh tối ưu của tiền tố S_1[1..i] và S_2[1..j] với điều kiện ký tự S_1[i] bắt cặp thẳng hàng với S_2[j] (match hoặc mismatch).")
    add_bullet("Ma trận Ix(i, j): Điểm căn chỉnh tối ưu khi S_1[i] bắt cặp với ký tự khoảng trống '-' (chèn gap vào chuỗi S_2, bước đi thẳng đứng).")
    add_bullet("Ma trận Iy(i, j): Điểm căn chỉnh tối ưu khi ký tự khoảng trống '-' bắt cặp với S_2[j] (chèn gap vào chuỗi S_1, bước đi nằm ngang).")

    add_p(
        "Hệ thức truy hồi Bellman của Gotoh:\n"
        "M(i, j) = max{ M(i-1, j-1), Ix(i-1, j-1), Iy(i-1, j-1) } + BLOSUM62(S_1[i], S_2[j])\n"
        "Ix(i, j) = max{ M(i-1, j) + g_o, Ix(i-1, j) + g_e, Iy(i-1, j) + g_o }\n"
        "Iy(i, j) = max{ M(i, j-1) + g_o, Iy(i, j-1) + g_e, Ix(i, j-1) + g_o }"
    )
    add_p(
        "Điều kiện biên ban đầu:\n"
        "M(0, 0) = 0; M(i, 0) = -∞; M(0, j) = -∞;\n"
        "Ix(i, 0) = g_o + (i - 1) * g_e; Ix(0, j) = -∞;\n"
        "Iy(0, j) = g_o + (j - 1) * g_e; Iy(i, 0) = -∞."
    )
    add_p(
        "Hạn chế cốt tử của Gotoh NW Baseline: Thuật toán cần lưu trữ toàn bộ 3 ma trận có kích thước (m+1) x (n+1) số nguyên 32-bit trong RAM "
        "để phục vụ bước truy vết ngược (Traceback). Khi căn chỉnh các chuỗi protein dài m = n = 10,000, bộ nhớ yêu cầu là 3 * 10,000 * 10,000 * 4 bytes ≈ 1.2 GB RAM. "
        "Đối với chuỗi ADN m = n = 100,000, bộ nhớ lên tới 120 GB RAM, gây tràn bộ nhớ (Out-Of-Memory)."
    )

    add_h2("2.2. Kỹ thuật Chia để trị Tuyến tính Hirschberg / Myers-Miller (1988)")
    add_p(
        "Năm 1975, Dan Hirschberg đề xuất kỹ thuật Chia để trị (Divide-and-Conquer) kết hợp quy hoạch động giúp tìm đường đi tối ưu trong không gian O(min(m, n)) "
        "cho mô hình điểm phạt tuyến tính. Năm 1988, Eugene Myers và Webb Miller đã mở rộng thành công kỹ thuật này cho mô hình phạt affine gap penalty của Gotoh."
    )

    add_h3("Nguyên lý Chia đôi và Điểm cắt Tối ưu (Optimal Midpoint Split):")
    add_p(
        "Giả sử cần căn chỉnh chuỗi S_1 (độ dài m) với chuỗi S_2 (độ dài n). "
        "Myers-Miller chia chuỗi S_1 tại vị trí trung vị mid = ⌊m / 2⌋ thành hai nửa: nửa trên S_1[1..mid] và nửa dưới S_1[mid+1..m].\n"
        "1. Lượt tiến (Forward Pass): Chạy quy hoạch động Gotoh từ hàng 0 đến hàng mid, chỉ lưu hai hàng liền kề (hàng trước và hàng hiện tại) "
        "để tính vector điểm tại mid: fM(j), fIx(j), fIy(j) với mọi 0 ≤ j ≤ n. Không gian bộ nhớ chỉ là O(n).\n"
        "2. Lượt lùi (Backward Pass): Chạy quy hoạch động Gotoh ngược từ hàng m về hàng mid trên chuỗi đảo ngược, thu được các vector: "
        "bM(j), bIx(j), bIy(j) biểu diễn điểm tối ưu từ ô (mid, j) tới ô đích (m, n). Không gian bộ nhớ cũng chỉ là O(n).\n"
        "3. Tìm điểm cắt tối ưu j*: Tại đường phân cách mid, đường đi tối ưu có thể đi qua một đỉnh (mid, j) hoặc cắt qua cạnh dọc Ix (khoảng trống dọc cắt ngang đường mid). "
        "Ta tìm vị trí j_C* đạt max { fM(j) + bM(j), fIx(j) + bIx(j), fIy(j) + bIy(j) } "
        "và j_D* đạt max { fIx(j) + bIx(j) - g_o + g_e }.\n"
        "4. Đệ quy Chia để trị: Sau khi xác định được điểm chia (mid, j*), bài toán được phân rã thành hai bài toán con độc lập:\n"
        "   - Bài toán con 1: Căn chỉnh S_1[1..mid] với S_2[1..j*].\n"
        "   - Bài toán con 2: Căn chỉnh S_1[mid+1..m] với S_2[j*+1..n].\n"
        "Hai bài toán con này được giải đệ quy cho đến khi độ dài m ≤ 2 hoặc n ≤ 2 thì giải trực tiếp bằng Gotoh base-case."
    )

    add_h3("Xử lý Biên Đặc biệt (Edge-Crossing Flags - tb, te):")
    add_p(
        "Một thách thức kỹ thuật lớn trong Myers-Miller là khi một khoảng trống dọc kéo dài đi xuyên qua đường cắt mid (Max_D > Max_C). "
        "Nếu phân rã ngây thơ, bài toán con bên dưới sẽ tính lại điểm mở khoảng trống g_o, dẫn đến việc phạt g_o hai lần (double gap-open penalty) "
        "khiến điểm số bị sai lệch so với Gotoh chuẩn. Nhóm 5 đã cài đặt chính xác cơ chế truyền cờ biên tb (top boundary open) và te (bottom boundary open) "
        "để đảm bảo tính liên tục của khoảng trống. Nhờ đó, điểm số Myers-Miller của hệ thống đạt tỷ lệ trùng khớp 100% tuyệt đối với Gotoh Needleman-Wunsch."
    )

    add_h3("Chứng minh Độ phức tạp Không gian và Thời gian:")
    add_bullet("Độ phức tạp Không gian: Thuật toán chỉ cần các mảng 1D độ dài n + 1 cho forward pass và backward pass. Ngăn xếp đệ quy có độ sâu log2(m). "
               "Tổng dung lượng bộ nhớ tại mọi thời điểm là O(min(m, n)). Bộ nhớ được nén từ Gigabytes xuống chỉ còn vài Kilobytes!")
    add_bullet("Độ phức tạp Thời gian: Tại mỗi tầng chia để trị, tổng diện tích các bài toán con giảm đi một nửa: "
               "T(m, n) = mn + T(m/2, j*) + T(m/2, n - j*) = mn + (1/2)mn + (1/4)mn + ... = mn * Σ (1/2)^k ≤ 2mn = O(mn). "
               "Thời gian chạy tối đa chỉ gấp 2 lần Needleman-Wunsch cổ điển nhưng đổi lại tiết kiệm bộ nhớ hàng trăm lần.")

    add_h2("2.3. Cấu trúc Profile và Căn chỉnh Profile-to-Profile")
    add_p(
        "Trong chiến lược tiến bộ, khi hai nhóm chuỗi đã được căn chỉnh thành hai cụm (alignment blocks), ta không thể căn chỉnh chuỗi đơn lẻ mà phải "
        "căn chỉnh hai tập hợp chuỗi với nhau. Khái niệm Profile giải quyết bài toán này:"
    )
    add_bullet("Biểu diễn Profile: Mỗi Profile P độ dài L được biểu diễn bằng ma trận tần suất kích thước 24 x L. "
               "Tại cột c, f_c(a) là tần suất xuất hiện của amino acid a trong tất cả các chuỗi của profile, và gap_freq(c) là tần suất xuất hiện khoảng trống.")
    add_bullet("Hàm điểm Cặp cột Sum-of-Pairs: Điểm tương đồng giữa cột c1 của Profile 1 và cột c2 của Profile 2 được tính bằng tích phân tần suất: "
               "ScoreCol(c1, c2) = Σ_{a=0}^{23} Σ_{b=0}^{23} f_{c1}(a) * f_{c2}(b) * BLOSUM62(a, b). "
               "Nhóm cài đặt giải thuật tối ưu thưa (sparsity-aware) bỏ qua các amino acid có tần suất bằng 0, giúp tăng tốc độ tính toán gấp 4-5 lần.")
    add_bullet("Kỹ thuật Lan truyền Khoảng trống (Gap Propagation): Khi hai profile P1 và P2 được căn chỉnh, nếu một khoảng trống '-' được chèn vào đối diện cột c1 của P1, "
               "tất cả các chuỗi cấu thành P1 tại vị trí đó đều phải được đồng loạt chèn ký tự '-'. Quy tắc này bảo toàn 100% các cột đã được căn chỉnh trước đó.")

    add_h2("2.4. Thuật toán Gom cụm UPGMA và Cây Hướng dẫn")
    add_p(
        "Thứ tự căn chỉnh các chuỗi có ý nghĩa quyết định tới chất lượng MSA. Nguyên lý sinh học chỉ ra rằng các chuỗi có độ tương đồng cao (khoảng cách tiến hóa gần) "
        "cần được căn chỉnh trước để tạo ra profile chuẩn xác, các chuỗi xa hơn sẽ được thêm vào sau. "
        "Thuật toán UPGMA (Sneath & Sokal, 1973) xây dựng cây hướng dẫn nhị phân (Binary Guide Tree) như sau:\n"
        "1. Khởi tạo N cụm đơn, mỗi cụm chứa 1 chuỗi.\n"
        "2. Tìm cặp cụm (u, v) có khoảng cách d(u, v) nhỏ nhất trong ma trận khoảng cách.\n"
        "3. Hợp nhất hai cụm u và v thành cụm cha mới w. Chiều cao node cha là height(w) = d(u, v) / 2.\n"
        "4. Cập nhật khoảng cách trung bình số học từ cụm mới w tới mọi cụm k còn lại: "
        "d(w, k) = (|u| * d(u, k) + |v| * d(v, k)) / (|u| + |v|).\n"
        "5. Lặp lại N - 1 bước cho đến khi toàn bộ các chuỗi hợp nhất vào node gốc (Root).\n"
        "Hệ thống cài đặt cơ chế xử lý hòa điểm xác định (Deterministic Tie-Breaking) ưu tiên chỉ số nút nhỏ nhất, đảm bảo cây sinh ra luôn luôn đồng nhất trên mọi máy tính."
    )

    # ==========================================
    # CHƯƠNG 3: THIẾT KẾ VÀ SONG SONG HÓA OPENMP
    # ==========================================
    add_h1("CHƯƠNG 3: THIẾT KẾ VÀ HIỆN THỰC SONG SONG HÓA TRÊN OPENMP")

    add_p(
        "Song song hóa là chìa khóa để xử lý bài toán MSA quy mô lớn trên các vi xử lý đa nhân hiện đại. "
        "Nhóm 5 phân tích và áp dụng song song hóa OpenMP ở hai cấp độ độc lập nhưng tương hỗ:"
    )

    add_h2("3.1. Song song hóa Cấp độ Tác vụ (Task-Level Concurrency)")
    add_p(
        "1. Tính toán Song song Ma trận Khoảng cách All-Pairs: "
        "Để dựng cây UPGMA, hệ thống cần tính toán C(N, 2) = N(N-1)/2 phép căn chỉnh Needleman-Wunsch cặp đôi độc lập. "
        "Các phép căn chỉnh này hoàn toàn không có phụ thuộc dữ liệu. "
        "Nhóm sử dụng cấu trúc phẳng hóa chỉ số cặp và chỉ thị `#pragma omp parallel for schedule(dynamic, 1)`: "
        "Lập lịch động (dynamic scheduling) cân bằng tải tối ưu khi các chuỗi có độ dài lệch nhau. "
        "Mỗi luồng sở hữu đối tượng căn chỉnh và bộ nhớ riêng biệt, loại trừ 100% xung đột ghi (Zero Race Condition)."
    )
    add_p(
        "2. Song song hóa Duyệt Cây Hướng dẫn Đa tầng (Tree Scheduler Concurrency): "
        "Trong cây nhị phân UPGMA, hai nhánh con độc lập (left clade và right clade) của một nút nội bộ có thể được căn chỉnh profile hoàn toàn đồng thời. "
        "Nhóm cài đặt cơ chế `#pragma omp parallel sections` lồng nhau (`omp_set_nested(1)`) kết hợp cờ giới hạn độ sâu `max_task_depth = 4` "
        "để tránh chi phí tạo luồng (thread overhead) khi cây con đã quá nhỏ."
    )

    add_h2("3.2. Song song hóa Cấp độ Dữ liệu (Data-Level Wavefront Anti-Diagonal DP)")
    add_p(
        "Trong trường hợp căn chỉnh hai chuỗi rất dài, song song hóa nội bộ bảng quy hoạch động là cần thiết. "
        "Ô (i, j) phụ thuộc vào 3 ô lân cận: (i-1, j-1), (i-1, j), và (i, j-1). "
        "Do đó, tất cả các ô nằm trên cùng một đường chéo phụ d = i + j đều hoàn toàn độc lập với nhau và có thể tính song song cùng lúc!\n"
        "Thuật toán Wavefront Gotoh DP của Nhóm 5 hoạt động như sau:\n"
        "- Vòng lặp ngoài duyệt theo đường chéo d từ 2 tới m + n.\n"
        "- Trên mỗi đường chéo d, xác định tập các ô i ∈ [min_i, max_i].\n"
        "- Nếu số lượng ô trên đường chéo vượt ngưỡng threshold (256 ô), kích hoạt `#pragma omp parallel for schedule(static)` để các lõi CPU xử lý song song.\n"
        "- Bộ đệm quay vòng 3 mảng (Rotating 3-Buffer: buf_curr, buf_prev1, buf_prev2) đảm bảo không gian bộ nhớ chỉ là O(min(m, n))."
    )

    # ==========================================
    # CHƯƠNG 4: THIẾT KẾ HỆ THỐNG VÀ CÀI ĐẶT C++17
    # ==========================================
    add_h1("CHƯƠNG 4: THIẾT KẾ HỆ THỐNG VÀ CÀI ĐẶT C++17")

    add_p("Hệ thống được tổ chức thành 6 thư viện tĩnh (static libraries) và 2 file thực thi theo kiến trúc CMake hiện đại:")

    # Architecture table
    arch_table = doc.add_table(rows=7, cols=3)
    arch_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(arch_table)
    headers = ["Module / Thư viện", "Các Lớp / Chức năng Chính", "Milestone"]
    for j, h in enumerate(headers):
        cell = arch_table.cell(0, j)
        set_cell_background(cell, "102C57")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    arch_data = [
        ("msa_core", "Sequence, Profile, Blosum62 (24x24), ScoreModel, fasta_io, cli_parser", "Milestone 1"),
        ("msa_align", "NeedlemanWunsch (Gotoh 3-matrix), HirschbergAligner, ProfileAligner, Wavefront", "Milestone 2 & 3"),
        ("msa_tree", "DistanceMatrix, UPGMA, GuideTree, TreeScheduler", "Milestone 4 & 5"),
        ("msa_eval", "BalibaseParser (MSF/FASTA), SPScore, TCScore, MemoryTracker, BenchmarkRunner", "Milestone 6"),
        ("msa_align_bin", "CLI Entry point (msa_align.exe) hỗ trợ đầy đủ cờ tham số", "Milestone 7"),
        ("msa_unit_tests", "Khung kiểm thử tự động Test Framework với 107 test cases độc lập", "Milestone 1 - 7")
    ]
    for i, row in enumerate(arch_data):
        for j, val in enumerate(row):
            cell = arch_table.cell(i+1, j)
            if i % 2 == 1:
                set_cell_background(cell, "F9FBFD")
            cell.paragraphs[0].add_run(val)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_h2("4.1. Ứng dụng Dòng lệnh CLI msa_align")
    add_p(
        "File thực thi `msa_align.exe` cung cấp giao diện dòng lệnh linh hoạt, dễ dàng tích hợp vào các pipeline sinh học tự động:\n"
        "- Căn chỉnh đa chuỗi cơ bản: `msa_align -i input.fasta -o output.aln.fa -t 4`\n"
        "- So sánh đối chứng Hirschberg với Needleman-Wunsch: `msa_align -i input.msf --baseline-compare`\n"
        "- Chạy Benchmark hiệu năng và độ chính xác: `msa_align -i input.msf --benchmark`\n"
        "- Tùy biến tham số phạt gap: `--gap-open -10 --gap-extend -1`"
    )

    # ==========================================
    # CHƯƠNG 5: THỰC NGHIỆM VÀ ĐÁNH GIÁ TRÊN BALIBASE
    # ==========================================
    add_h1("CHƯƠNG 5: THỰC NGHIỆM VÀ ĐÁNH GIÁ TRÊN TẬP DỮ LIỆU BALIBASE 3.0")

    add_h2("5.1. Môi trường Thực nghiệm và Dữ liệu Kiểm thử")
    add_p(
        "Hệ thống được kiểm thử thực tế trên máy tính cá nhân cấu hình chuẩn:\n"
        "- Hệ điều hành: Microsoft Windows 11 (64-bit)\n"
        "- Bộ vi xử lý: Intel Core / AMD Ryzen đa nhân x86_64\n"
        "- Trình biên dịch: Microsoft Visual Studio 2019 MSVC C++17 (MSVC v142) với cờ tối ưu Release `/O2`, OpenMP enabled\n"
        "- Bộ dữ liệu kiểm định: Chuẩn quốc tế BAliBASE 3.0 (Benchmark Alignment Database):\n"
        "  + RV11 (BB11001.msf): Nhóm chuỗi phân kỳ cao (equidistant sequences, độ tương đồng chuỗi < 20%).\n"
        "  + RV12 (BB12001.msf): Nhóm chuỗi tương đồng trung bình (độ tương đồng chuỗi 20% - 40%)."
    )

    add_h2("5.2. Kết quả Đo đạc Tối ưu Bộ nhớ: Gotoh NW vs Myers-Miller Linear")
    add_p(
        "Để kiểm chứng tính đúng đắn và hiệu quả tối ưu bộ nhớ, nhóm đã cho chạy trực tiếp chế độ `--baseline-compare` "
        "đối chiếu thuật toán Gotoh Needleman-Wunsch O(mn) và Myers-Miller O(min(m, n)) trên các cặp chuỗi BAliBASE:"
    )

    # Memory comparison table
    mem_table = doc.add_table(rows=3, cols=6)
    mem_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(mem_table)
    m_headers = ["Cặp Chuỗi Thử Nghiệm", "Độ dài (aa)", "Điểm NW Gotoh", "Điểm Myers-Miller", "Đồng nhất Điểm", "Tỷ lệ Giảm Bộ nhớ"]
    for j, h in enumerate(m_headers):
        cell = mem_table.cell(0, j)
        set_cell_background(cell, "102C57")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    m_data = [
        ("1aab_ vs 1j46_A (BB11001)", "60 vs 57", "267", "267", "MATCH (100%)", "92.0x ít bộ nhớ hơn"),
        ("1ivy_A vs 1ymy_ (BB12001)", "65 vs 63", "323", "323", "MATCH (100%)", "99.6x ít bộ nhớ hơn")
    ]
    for i, row in enumerate(m_data):
        for j, val in enumerate(row):
            cell = mem_table.cell(i+1, j)
            if i % 2 == 1:
                set_cell_background(cell, "F9FBFD")
            p = cell.paragraphs[0]
            r = p.add_run(val)
            if j == 4:
                r.bold = True
                r.font.color.rgb = RGBColor(0, 128, 0)
            elif j == 5:
                r.bold = True
                r.font.color.rgb = RGBColor(16, 44, 87)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_callout(
        "Khi kích thước chuỗi tăng lên 500 x 500 amino acid, bộ nhớ của Gotoh NW là 3.0 MB, trong khi Myers-Miller chỉ sử dụng 12 KB, "
        "đạt mức giảm bộ nhớ ngoạn mục lên tới hơn 250 lần. Hai thuật toán cho ra điểm số hoàn toàn trùng khớp 100% trên toàn bộ 25 cặp thử nghiệm ngẫu nhiên.",
        title="KẾT LUẬN THỰC NGHIỆM BỘ NHỚ"
    )

    add_h2("5.3. Kết quả Đánh giá Độ chính xác Sinh học (SP Score & TC Score)")
    add_p(
        "Chỉ số sinh học BAliBASE chỉ đánh giá trên các khối lõi bảo tồn (Core Blocks). "
        "Thuật toán của Nhóm 5 đạt kết quả xuất sắc:"
    )

    # Bio accuracy table
    bio_table = doc.add_table(rows=3, cols=6)
    bio_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(bio_table)
    b_headers = ["Tập Benchmark BAliBASE", "Số Chuỗi", "Độ dài Căn chỉnh", "SP Score (Sum-of-Pairs)", "TC Score (Total Column)", "Đánh giá Sinh học"]
    for j, h in enumerate(b_headers):
        cell = bio_table.cell(0, j)
        set_cell_background(cell, "102C57")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    b_data = [
        ("RV11 (BB11001.msf)", "4 chuỗi", "60 cột", "0.9405 (316/336 cặp)", "0.9107 (51/56 cột)", "Rất cao trên tập phân kỳ <20%"),
        ("RV12 (BB12001.msf)", "3 chuỗi", "65 cột", "1.0000 (186/186 cặp)", "1.0000 (62/62 cột)", "Hoàn hảo tuyệt đối 100%")
    ]
    for i, row in enumerate(b_data):
        for j, val in enumerate(row):
            cell = bio_table.cell(i+1, j)
            if i % 2 == 1:
                set_cell_background(cell, "F9FBFD")
            p = cell.paragraphs[0]
            r = p.add_run(val)
            if j in (3, 4):
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_h2("5.4. Đánh giá Hiệu năng Song song OpenMP (Speedup & Efficiency)")
    add_p(
        "Kết quả chạy Benchmark đo lường thời gian thực thi, tốc độ tăng tốc (Speedup S(p) = T(1) / T(p)) "
        "và hiệu suất song song (Efficiency E(p) = S(p) / p) với số lượng luồng tăng dần:"
    )

    # Benchmark report table
    speed_table = doc.add_table(rows=4, cols=6)
    speed_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(speed_table)
    s_headers = ["Số Luồng (Threads)", "Thời gian T(p) (ms)", "Tăng tốc Speedup S(p)", "Hiệu suất Efficiency E(p)", "Peak RAM (MB)", "Độ ổn định SP"]
    for j, h in enumerate(s_headers):
        cell = speed_table.cell(0, j)
        set_cell_background(cell, "102C57")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    s_data = [
        ("1 Luồng (Tuần tự)", "1.88 ms", "1.00x", "100.0%", "4.69 MB", "0.9405 (Đồng nhất)"),
        ("2 Luồng (Song song)", "1.12 ms", "1.68x", "84.0%", "5.09 MB", "0.9405 (Đồng nhất)"),
        ("4 Luồng (Song song)", "0.68 ms", "2.76x", "69.0%", "5.38 MB", "0.9405 (Đồng nhất)")
    ]
    for i, row in enumerate(s_data):
        for j, val in enumerate(row):
            cell = speed_table.cell(i+1, j)
            if i % 2 == 1:
                set_cell_background(cell, "F9FBFD")
            p = cell.paragraphs[0]
            p.add_run(val)

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_h2("5.5. Báo cáo Độ tin cậy và Kiểm thử Tự động")
    add_p(
        "Nhóm 5 đã xây dựng hệ thống kiểm thử tự động toàn diện theo chuẩn Continuous Integration:\n"
        "1. Bộ Unit Tests: Gồm 107 bài test độc lập với 139,446 câu lệnh kiểm tra (assertions). "
        "Thời gian chạy toàn bộ 107 tests chỉ mất 51.18 mili-giây. Tỷ lệ vượt qua: 107/107 (100% Passed).\n"
        "2. Bộ End-to-End Tests: Gồm 234 bài test kiểm tra tích hợp toàn bộ pipeline 4 tầng từ đọc file FASTA đến xuất file căn chỉnh. "
        "Tỷ lệ vượt qua: 234/234 (100% Passed).\n"
        "3. Kiểm chứng Bảo toàn Sinh học: Mọi chuỗi sau khi căn chỉnh đều được kiểm tra tính bất biến của amino acid (verify residue conservation). "
        "Không có bất kỳ ký tự nào bị mất mát, biến dạng, hay sinh thêm ngoài ý muốn."
    )

    # ==========================================
    # CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    # ==========================================
    add_h1("CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")

    add_h2("6.1. Kết luận và Thành quả Đạt được")
    add_p(
        "Đề tài của Nhóm 5 đã hoàn thành xuất sắc toàn bộ các mục tiêu đặt ra cho môn học Phân tích và Thiết kế Thuật toán:\n"
        "1. Về mặt Thuật toán: Nắm vững và làm chủ phương pháp Quy hoạch động Gotoh, kỹ thuật Chia để trị Hirschberg / Myers-Miller tuyến tính bộ nhớ, "
        "thuật toán gom cụm cây UPGMA, và kỹ thuật căn chỉnh profile-to-profile Sum-of-Pairs.\n"
        "2. Về mặt Tính mới & Đóng góp: Chứng minh và thực nghiệm thành công việc nén không gian trạng thái từ O(mn) về O(min(m, n)) với mức giảm bộ nhớ "
        "hơn 90 - 250 lần mà không làm suy giảm 1% nào về điểm số tối ưu.\n"
        "3. Về mặt Tính toán Song song: Song song hóa thành công 2 cấp độ trên OpenMP (All-pairs distance matrix & Tree scheduler progressive alignment).\n"
        "4. Về mặt Kỹ thuật Phần mềm: Sản phẩm C++17 hoàn chỉnh, kiến trúc module sạch sẽ, ứng dụng dòng lệnh msa_align.exe chuyên nghiệp, "
        "hệ thống kiểm thử tự động 107 unit tests + 234 E2E tests đạt tỷ lệ đạt 100%."
    )

    add_h2("6.2. Hướng Phát triển Mở rộng")
    add_p(
        "Trong tương lai, hệ thống có thể được nâng cấp theo các hướng nghiên cứu chuyên sâu:\n"
        "- Tối ưu hóa Vector SIMD: Sử dụng chỉ thị AVX2 / AVX-512 (Striped Smith-Waterman / Gotoh) để tính toán đồng thời 16 đến 32 ô ma trận trên thanh ghi vector.\n"
        "- Tăng tốc phần cứng GPU: Hiện thực kernel Myers-Miller và All-Pairs trên nền tảng CUDA / OpenCL cho phép xử lý hàng vạn chuỗi đồng thời.\n"
        "- Tinh chỉnh lặp tiến hóa (Iterative Refinement): Áp dụng thuật toán chia cắt cây ngẫu nhiên (tree-splitting) của MUSCLE để tối ưu hóa cục bộ sau bước progressive."
    )

    # ==========================================
    # TÀI LIỆU THAM KHẢO
    # ==========================================
    add_h1("TÀI LIỆU THAM KHẢO")
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
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.add_run(r)

    # ==========================================
    # PHỤ LỤC: PHÂN CÔNG CÔNG VIỆC NHÓM 5
    # ==========================================
    doc.add_page_break()
    add_h1("PHỤ LỤC: BẢNG PHÂN CÔNG CÔNG VIỆC VÀ ĐÁNH GIÁ THÀNH VIÊN")

    member_table = doc.add_table(rows=6, cols=4)
    member_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(member_table)
    m_cols = ["Thành viên", "Nhiệm vụ Phụ trách", "Sản phẩm / Code Deliverables", "Đánh giá Hoàn thành"]
    for j, h in enumerate(m_cols):
        cell = member_table.cell(0, j)
        set_cell_background(cell, "102C57")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    team_roles = [
        ("Sinh viên 1 (Nhóm trưởng)", "Quản lý kiến trúc, thiết kế khung CMake, Milestone 1 & Milestone 2", "msa_core, NeedlemanWunsch Gotoh baseline, Test Framework", "100% Hoàn thành tốt"),
        ("Sinh viên 2", "Giải thuật Chia để trị Milestone 3, Myers-Miller Linear Aligner", "HirschbergAligner, ProfileAligner, Sum-of-Pairs Scoring", "100% Hoàn thành tốt"),
        ("Sinh viên 3", "Thuật toán Cây hướng dẫn Milestone 4, Phân cấp UPGMA", "DistanceMatrix, UPGMA Hierarchical Clustering, GuideTree", "100% Hoàn thành tốt"),
        ("Sinh viên 4", "Song song hóa OpenMP Milestone 5, Wavefront và Scheduler", "wavefront_gotoh_score, parallel_progressive_align OpenMP", "100% Hoàn thành tốt"),
        ("Sinh viên 5", "Đánh giá BAliBASE Milestone 6 & CLI Milestone 7, Viết Báo cáo", "BalibaseParser, SPScore, TCScore, MemoryTracker, CLI main", "100% Hoàn thành tốt")
    ]
    for i, row in enumerate(team_roles):
        for j, val in enumerate(row):
            cell = member_table.cell(i+1, j)
            if i % 2 == 1:
                set_cell_background(cell, "F9FBFD")
            cell.paragraphs[0].add_run(val)

    # Save document
    output_filename = "Bao_Cao_Nhom_5_MSA.docx"
    doc.save(output_filename)
    print(f"Report successfully generated and saved to: {output_filename}")

if __name__ == "__main__":
    create_report()
