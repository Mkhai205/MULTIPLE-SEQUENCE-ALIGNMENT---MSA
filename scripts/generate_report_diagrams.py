"""
Generate High-Quality Academic Diagrams for Multiple Sequence Alignment (MSA) Report
Group 5 - MSA C++17 Pipeline
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

docs_img = Path('docs/images')
docs_img.mkdir(parents=True, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Calibri']
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

def generate_fig_2_1():
    fig, ax = plt.subplots(figsize=(9.5, 6.2), dpi=300)
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.6, 8.5)
    ax.axis('off')

    # Bounding box for DP Matrix
    rect_dp = patches.Rectangle((1, 1), 8, 6, linewidth=1.5, edgecolor='#3b82f6', facecolor='#f8fafc', zorder=1)
    ax.add_patch(rect_dp)

    # Grid lines
    for y in range(2, 7):
        ax.axhline(y, xmin=0.14, xmax=0.86, color='#e2e8f0', linestyle='--', linewidth=0.7, zorder=2)
    for x in range(2, 9):
        ax.axvline(x, ymin=0.17, ymax=0.83, color='#e2e8f0', linestyle='--', linewidth=0.7, zorder=2)

    # Mid-row split line (i = m/2)
    ax.plot([1, 9], [4, 4], color='#dc2626', linewidth=2.5, linestyle='-', zorder=4)
    ax.text(9.2, 4, 'Đường chia giữa: i = m/2', color='#dc2626', fontsize=10, fontweight='bold', va='center')

    # Forward pass arrows
    ax.annotate('', xy=(4.8, 3.9), xytext=(1.2, 6.8),
                arrowprops=dict(arrowstyle="->", color='#2563eb', lw=2.2, connectionstyle="arc3,rad=-0.15"), zorder=5)
    ax.text(2.6, 5.8, 'Forward Pass: F(mid, j)\n(Quét tiến 2 hàng Gotoh)', color='#1d4ed8', fontsize=9, fontweight='bold')

    # Backward pass arrows
    ax.annotate('', xy=(5.2, 4.1), xytext=(8.8, 1.2),
                arrowprops=dict(arrowstyle="->", color='#059669', lw=2.2, connectionstyle="arc3,rad=-0.15"), zorder=5)
    ax.text(5.5, 2.2, 'Backward Pass: B(mid, j)\n(Quét lùi trên chuỗi đảo)', color='#047857', fontsize=9, fontweight='bold')

    # Optimal Midpoint Cut (j*)
    cut_point = patches.Circle((5.0, 4.0), 0.22, edgecolor='#b91c1c', facecolor='#fef08a', linewidth=2, zorder=6)
    ax.add_patch(cut_point)
    ax.plot(5.0, 4.0, marker='*', markersize=10, color='#dc2626', zorder=7)
    ax.annotate('Điểm cắt tối ưu: j* = argmax_j (F + B)', xy=(5.0, 4.0), xytext=(3.5, 4.8),
                arrowprops=dict(arrowstyle="->", color='#991b1b', lw=1.5),
                bbox=dict(boxstyle="round,pad=0.4", fc="#fef9c3", ec="#ca8a04", lw=1),
                fontsize=9.5, fontweight='bold', color='#854d0e', zorder=8)

    # Sub-problems rectangles
    sub1 = patches.Rectangle((1.05, 4.05), 3.9, 2.9, linewidth=1.2, edgecolor='#3b82f6', facecolor='#dbeafe', alpha=0.35, linestyle=':', zorder=3)
    sub2 = patches.Rectangle((5.05, 1.05), 3.9, 2.9, linewidth=1.2, edgecolor='#10b981', facecolor='#d1fae5', alpha=0.35, linestyle=':', zorder=3)
    ax.add_patch(sub1)
    ax.add_patch(sub2)
    ax.text(2.5, 4.5, 'Bài toán con 1:\n[0..m/2, 0..j*]', fontsize=8.5, color='#1e40af', ha='center', style='italic')
    ax.text(7.2, 3.2, 'Bài toán con 2:\n[m/2..m, j*..n]', fontsize=8.5, color='#065f46', ha='center', style='italic')

    # Axis labels
    ax.text(5, 7.3, 'Chuỗi 2: S2 (Chiều dài n cột)', fontsize=11, fontweight='bold', color='#1e293b', ha='center')
    ax.text(0.3, 4, 'Chuỗi 1: S1 (Chiều dài m hàng)', fontsize=11, fontweight='bold', color='#1e293b', va='center', rotation=90)
    ax.text(1, 7.15, '(0, 0)', fontsize=9, color='#64748b')
    ax.text(9, 0.75, '(m, n)', fontsize=9, color='#64748b', ha='right')

    # Complexity Box
    info_text = (
        'ĐẶC TRƯNG ĐỘ PHỨC TẠP MYERS-MILLER:\n'
        '• Không gian (Bộ nhớ RAM): O(min(m, n)) - Tuyến tính (Chỉ lưu 2 hàng tạm thời)\n'
        '• Thời gian (Tính toán CPU): O(m * n) - Tối đa 2x phép tính so với Gotoh chuẩn\n'
        '• Độ chính xác sinh học: 100% Đồng nhất tuyệt đối với ma trận Gotoh'
    )
    ax.text(5, -0.15, info_text, fontsize=8.5, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.5", fc="#f1f5f9", ec="#94a3b8", lw=1), color='#0f172a')

    plt.title('Hình 2.1: Nguyên lý Chia để trị và Tìm điểm cắt tối ưu của Thuật toán Myers-Miller (1988)',
              fontsize=11.5, fontweight='bold', pad=15, color='#0f172a')
    plt.tight_layout()
    plt.savefig(docs_img / 'fig_2_1_myers_miller_cut.png', dpi=300)
    plt.close()
    print('Generated fig_2_1_myers_miller_cut.png')

def generate_fig_2_2():
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Clade A Profile box
    ax.add_patch(patches.FancyBboxPatch((0.5, 3.2), 3.8, 2.2, boxstyle="round,pad=0.1",
                                        fc="#eff6ff", ec="#3b82f6", lw=1.5))
    ax.text(2.4, 5.1, 'CLADE A (Profile 1)', fontsize=10.5, fontweight='bold', color='#1e40af', ha='center')
    ax.text(2.4, 4.4, 'Seq 1: M - K V I L L ...\nSeq 2: M V K - I L L ...',
            fontsize=9.5, fontfamily='monospace', color='#1e293b', ha='center')
    ax.text(2.4, 3.6, 'PSSM: Tần suất 20 aa tại mỗi cột\n[20 x L1] Frequency Matrix',
            fontsize=8.5, color='#475569', ha='center', style='italic')

    # Clade B Profile box
    ax.add_patch(patches.FancyBboxPatch((5.7, 3.2), 3.8, 2.2, boxstyle="round,pad=0.1",
                                        fc="#ecfdf5", ec="#10b981", lw=1.5))
    ax.text(7.6, 5.1, 'CLADE B (Profile 2)', fontsize=10.5, fontweight='bold', color='#065f46', ha='center')
    ax.text(7.6, 4.4, 'Seq 3: M - R V I L F ...\nSeq 4: M K R V - L F ...',
            fontsize=9.5, fontfamily='monospace', color='#1e293b', ha='center')
    ax.text(7.6, 3.6, 'PSSM: Tần suất 20 aa tại mỗi cột\n[20 x L2] Frequency Matrix',
            fontsize=8.5, color='#475569', ha='center', style='italic')

    # Center Alignment Operation
    ax.annotate('', xy=(5.0, 2.8), xytext=(2.4, 3.1),
                arrowprops=dict(arrowstyle="->", color='#3b82f6', lw=2))
    ax.annotate('', xy=(5.0, 2.8), xytext=(7.6, 3.1),
                arrowprops=dict(arrowstyle="->", color='#10b981', lw=2))

    # Profile-Profile Score formula box
    formula_box = patches.FancyBboxPatch((2.2, 1.8), 5.6, 0.9, boxstyle="round,pad=0.1",
                                         fc="#fef9c3", ec="#eab308", lw=1.5)
    ax.add_patch(formula_box)
    ax.text(5.0, 2.25, 'Score(Col_i, Col_j) = SUM_a SUM_b  f_A(a) * f_B(b) * BLOSUM62(a, b)',
            fontsize=9.5, fontweight='bold', fontfamily='monospace', color='#854d0e', ha='center')

    # Merged MSA Box
    ax.annotate('', xy=(5.0, 1.4), xytext=(5.0, 1.8),
                arrowprops=dict(arrowstyle="->", color='#64748b', lw=2))
    ax.add_patch(patches.FancyBboxPatch((1.5, 0.2), 7.0, 1.1, boxstyle="round,pad=0.1",
                                        fc="#f8fafc", ec="#64748b", lw=1.5))
    ax.text(5.0, 0.95, 'KẾT QUẢ GỘP MSA (Merged Clade Alignment)', fontsize=10, fontweight='bold', color='#0f172a', ha='center')
    ax.text(5.0, 0.5, 'Bảo toàn vị trí gap cũ ("Once a gap, always a gap") + Chèn gap đồng bộ',
            fontsize=8.5, color='#334155', ha='center', style='italic')

    plt.title('Hình 2.2: Cơ chế Biểu diễn Profile PSSM và Căn chỉnh Profile-to-Profile bằng BLOSUM62',
              fontsize=11.5, fontweight='bold', pad=15, color='#0f172a')
    plt.tight_layout()
    plt.savefig(docs_img / 'fig_2_2_profile_alignment.png', dpi=300)
    plt.close()
    print('Generated fig_2_2_profile_alignment.png')

def generate_fig_2_3():
    fig, ax = plt.subplots(figsize=(9.5, 5.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Stage 1: Distance Matrix
    ax.add_patch(patches.FancyBboxPatch((0.5, 1.5), 2.5, 3.5, boxstyle="round,pad=0.1",
                                        fc="#f8fafc", ec="#3b82f6", lw=1.5))
    ax.text(1.75, 4.6, 'BƯỚC 1:\nMa trận Khoảng cách', fontsize=9.5, fontweight='bold', color='#1e40af', ha='center')
    matrix_str = "    S1   S2   S3   S4\nS1   0  .12  .45  .50\nS2 .12    0  .48  .52\nS3 .45  .48    0  .18\nS4 .50  .52  .18    0"
    ax.text(1.75, 2.7, matrix_str, fontsize=8.5, fontfamily='monospace', color='#1e293b', ha='center')

    # Arrow 1 -> 2
    ax.annotate('', xy=(3.4, 3.2), xytext=(3.1, 3.2),
                arrowprops=dict(arrowstyle="->", color='#64748b', lw=2))

    # Stage 2: Hierarchical Clustering
    ax.add_patch(patches.FancyBboxPatch((3.5, 1.5), 2.8, 3.5, boxstyle="round,pad=0.1",
                                        fc="#f0fdf4", ec="#10b981", lw=1.5))
    ax.text(4.9, 4.6, 'BƯỚC 2:\nGom cụm UPGMA', fontsize=9.5, fontweight='bold', color='#065f46', ha='center')
    algo_str = "1. Tìm min D(u, v)\n   -> Ghép (S1, S2)\n2. Chiều cao nhánh:\n   h = D(u, v) / 2\n3. Cập nhật TB:\n   D(C, k) = TB số học\n4. Lặp lại N-1 lần"
    ax.text(4.9, 2.7, algo_str, fontsize=8.5, color='#1e293b', ha='center')

    # Arrow 2 -> 3
    ax.annotate('', xy=(6.7, 3.2), xytext=(6.4, 3.2),
                arrowprops=dict(arrowstyle="->", color='#64748b', lw=2))

    # Stage 3: Rooted Guide Tree
    ax.add_patch(patches.FancyBboxPatch((6.8, 1.5), 2.8, 3.5, boxstyle="round,pad=0.1",
                                        fc="#faf5ff", ec="#8b5cf6", lw=1.5))
    ax.text(8.2, 4.6, 'BƯỚC 3:\nCây Hướng dẫn UPGMA', fontsize=9.5, fontweight='bold', color='#6b21a8', ha='center')

    # Simple tree drawing inside Box 3
    # Root
    ax.plot([7.2, 8.2], [3.2, 3.8], color='#7c3aed', lw=2)
    ax.plot([9.2, 8.2], [3.2, 3.8], color='#7c3aed', lw=2)
    # Left branch
    ax.plot([7.0, 7.2], [2.4, 3.2], color='#7c3aed', lw=1.8)
    ax.plot([7.4, 7.2], [2.4, 3.2], color='#7c3aed', lw=1.8)
    ax.text(7.0, 2.1, 'S1', fontsize=9, fontweight='bold', ha='center', color='#1e293b')
    ax.text(7.4, 2.1, 'S2', fontsize=9, fontweight='bold', ha='center', color='#1e293b')
    # Right branch
    ax.plot([9.0, 9.2], [2.4, 3.2], color='#7c3aed', lw=1.8)
    ax.plot([9.4, 9.2], [2.4, 3.2], color='#7c3aed', lw=1.8)
    ax.text(9.0, 2.1, 'S3', fontsize=9, fontweight='bold', ha='center', color='#1e293b')
    ax.text(9.4, 2.1, 'S4', fontsize=9, fontweight='bold', ha='center', color='#1e293b')

    ax.text(8.2, 1.8, 'Newick: ((S1,S2),(S3,S4));', fontsize=8, fontfamily='monospace', color='#4c1d95', ha='center')

    # Bottom summary
    ax.text(5.0, 0.6, 'Độ phức tạp thuật toán: O(N^2) thời gian tính toán và không gian lưu trữ ma trận đối xứng N x N',
            fontsize=9, ha='center', bbox=dict(boxstyle="round,pad=0.4", fc="#f1f5f9", ec="#94a3b8", lw=1), color='#334155')

    plt.title('Hình 2.3: Quy trình Gom cụm Phân cấp UPGMA Xây dựng Cây Dẫn đường Tiến hóa (Guide Tree)',
              fontsize=11.5, fontweight='bold', pad=15, color='#0f172a')
    plt.tight_layout()
    plt.savefig(docs_img / 'fig_2_3_upgma_clustering.png', dpi=300)
    plt.close()
    print('Generated fig_2_3_upgma_clustering.png')

def generate_fig_3_1():
    fig, ax = plt.subplots(figsize=(8.5, 6), dpi=300)
    ax.set_xlim(-0.5, 8.5)
    ax.set_ylim(-0.5, 7.5)
    ax.axis('off')

    # Grid of cells
    for i in range(6):
        for j in range(7):
            k = i + j
            # Highlight anti-diagonal k = 5
            if k == 5:
                fc = '#bbf7d0'  # Active anti-diagonal (green)
                ec = '#16a34a'
                lw = 2
            elif k < 5:
                fc = '#e2e8f0'  # Calculated
                ec = '#94a3b8'
                lw = 1
            else:
                fc = '#ffffff'  # Not yet calculated
                ec = '#cbd5e1'
                lw = 1
            rect = patches.Rectangle((j + 0.5, 5.5 - i), 0.8, 0.8, facecolor=fc, edgecolor=ec, linewidth=lw)
            ax.add_patch(rect)
            ax.text(j + 0.9, 5.9 - i, f"{k}", fontsize=8, ha='center', va='center', color='#334155')

    # Anti-diagonal line
    ax.plot([0.5, 6.3], [6.3, 0.5], color='#16a34a', linestyle='--', linewidth=2.5, zorder=5)
    ax.text(6.5, 1.2, 'Wavefront k = 5\n(Đường chéo phụ)', color='#15803d', fontsize=9.5, fontweight='bold')

    # Concurrency arrows
    ax.annotate('', xy=(1.5, 4.5), xytext=(2.5, 3.5),
                arrowprops=dict(arrowstyle="<->", color='#047857', lw=2), zorder=6)
    ax.text(4.2, 6.8, 'Các ô trên cùng một đường chéo (k = i + j) độc lập dữ liệu\n-> Có thể tính toán SONG SONG đồng thời trên các luồng OpenMP',
            fontsize=9.5, fontweight='bold', color='#065f46', ha='center',
            bbox=dict(boxstyle="round,pad=0.4", fc="#dcfce7", ec="#86efac", lw=1))

    # Legend / Dependencies
    ax.text(4.0, -0.1, 'Phụ thuộc dữ liệu quy hoạch động: Ô (i, j) phụ thuộc vào 3 ô lân cận (i-1, j), (i, j-1) và (i-1, j-1)\n'
                       'Thời gian tính toán song song: O((m + n) + (m * n) / p)',
            fontsize=8.5, ha='center', bbox=dict(boxstyle="round,pad=0.4", fc="#f8fafc", ec="#cbd5e1", lw=1), color='#475569')

    plt.title('Hình 3.1: Song song hóa Ma trận Quy hoạch Động Wavefront theo Đường chéo phụ (Anti-Diagonal)',
              fontsize=11.5, fontweight='bold', pad=15, color='#0f172a')
    plt.tight_layout()
    plt.savefig(docs_img / 'fig_3_1_wavefront_antidiagonal.png', dpi=300)
    plt.close()
    print('Generated fig_3_1_wavefront_antidiagonal.png')

def generate_fig_4_1():
    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Layer 1: Frontend SPA (Top)
    box_fe = patches.FancyBboxPatch((0.5, 6.0), 11.0, 2.5, boxstyle="round,pad=0.15",
                                    fc="#eff6ff", ec="#3b82f6", lw=2)
    ax.add_patch(box_fe)
    ax.text(6.0, 8.2, 'TẦNG GIAO DIỆN NGƯỜI DÙNG: MODERN WEB GUI STUDIO (SPA)',
            fontsize=11, fontweight='bold', color='#1d4ed8', ha='center')
    
    # 3 FE Cards
    fe_card1 = patches.Rectangle((0.8, 6.3), 3.2, 1.6, fc="#ffffff", ec="#93c5fd", lw=1.2)
    fe_card2 = patches.Rectangle((4.4, 6.3), 3.2, 1.6, fc="#ffffff", ec="#93c5fd", lw=1.2)
    fe_card3 = patches.Rectangle((8.0, 6.3), 3.2, 1.6, fc="#ffffff", ec="#93c5fd", lw=1.2)
    ax.add_patch(fe_card1)
    ax.add_patch(fe_card2)
    ax.add_patch(fe_card3)

    ax.text(2.4, 7.5, 'Quick Presets & Controls', fontsize=9.5, fontweight='bold', color='#1e3a8a', ha='center')
    ax.text(2.4, 6.8, '• 6 Presets (RV11, RV12, 20/40 seq)\n• Sliders: OpenMP Threads (1..8)\n• Affine Gap Penalties',
            fontsize=8, color='#334155', ha='center')

    ax.text(6.0, 7.5, 'Alignment Matrix & Tree', fontsize=9.5, fontweight='bold', color='#1e3a8a', ha='center')
    ax.text(6.0, 6.8, '• ClustalX/Jalview Color Residues\n• Consensus & Conservation Bar\n• Interactive SVG Dendrogram',
            fontsize=8, color='#334155', ha='center')

    ax.text(9.6, 7.5, 'Analytics & Export Studio', fontsize=9.5, fontweight='bold', color='#1e3a8a', ha='center')
    ax.text(9.6, 6.8, '• Speedup S(p) & Efficiency E(p)\n• Gotoh vs Myers-Miller Card\n• Download FASTA, NWK, SVG',
            fontsize=8, color='#334155', ha='center')

    # IPC Connector between FE and Backend
    ax.annotate('', xy=(6.0, 5.3), xytext=(6.0, 6.0),
                arrowprops=dict(arrowstyle="<->", color='#2563eb', lw=2.5))
    ax.text(6.0, 5.65, 'HTTP REST API (JSON) + 100% Offline Static Hosting (Port 8000)',
            fontsize=8.5, fontweight='bold', color='#1e40af', ha='center',
            bbox=dict(boxstyle="round,pad=0.2", fc="#dbeafe", ec="#93c5fd", lw=1))

    # Layer 2: Python Backend (Middle)
    box_be = patches.FancyBboxPatch((1.5, 4.0), 9.0, 1.3, boxstyle="round,pad=0.15",
                                    fc="#f0fdf4", ec="#16a34a", lw=2)
    ax.add_patch(box_be)
    ax.text(6.0, 4.9, 'TẦNG DỊCH VỤ TRUNG GIAN: FASTAPI BACKEND SERVER (Python 3.13)',
            fontsize=10.5, fontweight='bold', color='#15803d', ha='center')
    ax.text(6.0, 4.3, '• Quản lý Endpoint: /api/align, /api/presets, /api/health\n'
                       '• Subprocess IPC Executor: Khởi chạy và giám sát tiến trình C++ msa_align.exe\n'
                       '• Windows Launcher: run_gui.bat tự động khởi động và mở trình duyệt mặc định',
            fontsize=8.5, color='#14532d', ha='center')

    # IPC Connector between Backend and C++ Engine
    ax.annotate('', xy=(6.0, 3.3), xytext=(6.0, 4.0),
                arrowprops=dict(arrowstyle="<->", color='#16a34a', lw=2.5))
    ax.text(6.0, 3.65, 'Subprocess IPC CLI Invocations (Standard Output, Temp Files & JSON Pipes)',
            fontsize=8.5, fontweight='bold', color='#166534', ha='center',
            bbox=dict(boxstyle="round,pad=0.2", fc="#dcfce7", ec="#86efac", lw=1))

    # Layer 3: C++17 Engine Core (Bottom)
    box_cpp = patches.FancyBboxPatch((0.5, 0.4), 11.0, 2.9, boxstyle="round,pad=0.15",
                                     fc="#f8fafc", ec="#475569", lw=2)
    ax.add_patch(box_cpp)
    ax.text(6.0, 2.9, 'TẦNG TÍNH TOÁN HIỆU NĂNG CAO: C++17 ENGINE NATIVE (msa_align.exe)',
            fontsize=11, fontweight='bold', color='#0f172a', ha='center')

    # 4 C++ Sub-modules
    cpp1 = patches.Rectangle((0.8, 0.7), 2.4, 1.9, fc="#ffffff", ec="#94a3b8", lw=1.2)
    cpp2 = patches.Rectangle((3.5, 0.7), 2.4, 1.9, fc="#ffffff", ec="#94a3b8", lw=1.2)
    cpp3 = patches.Rectangle((6.2, 0.7), 2.4, 1.9, fc="#ffffff", ec="#94a3b8", lw=1.2)
    cpp4 = patches.Rectangle((8.9, 0.7), 2.4, 1.9, fc="#ffffff", ec="#94a3b8", lw=1.2)
    ax.add_patch(cpp1)
    ax.add_patch(cpp2)
    ax.add_patch(cpp3)
    ax.add_patch(cpp4)

    ax.text(2.0, 2.2, 'IO & Core', fontsize=9, fontweight='bold', color='#1e293b', ha='center')
    ax.text(2.0, 1.4, '• FastaParser/Writer\n• BalibaseParser (.msf)\n• ScoreModel & BLOSUM62\n• Validation Rules',
            fontsize=7.5, color='#475569', ha='center')

    ax.text(4.7, 2.2, 'Pairwise Align', fontsize=9, fontweight='bold', color='#1e293b', ha='center')
    ax.text(4.7, 1.4, '• Myers-Miller Linear O(min)\n• Gotoh NW Quadratic O(mn)\n• Wavefront Anti-Diagonal\n• Affine Penalties',
            fontsize=7.5, color='#475569', ha='center')

    ax.text(7.4, 2.2, 'Tree & Progressive', fontsize=9, fontweight='bold', color='#1e293b', ha='center')
    ax.text(7.4, 1.4, '• DistanceMatrix O(N^2*L^2)\n• UPGMA Clustering O(N^2)\n• ProfilePSSM (20xL)\n• Profile-Profile Align',
            fontsize=7.5, color='#475569', ha='center')

    ax.text(10.1, 2.2, 'Parallel & Eval', fontsize=9, fontweight='bold', color='#1e293b', ha='center')
    ax.text(10.1, 1.4, '• OpenMP Dynamic Scheduler\n• TreeScheduler Sections\n• SP Score & TC Score\n• MemoryTracker Win32',
            fontsize=7.5, color='#475569', ha='center')

    plt.title('Hình 4.1: Sơ đồ Kiến trúc Tổng thể Hệ thống Căn chỉnh Đa chuỗi MSA Nhóm 5 (C++17 + FastAPI + Web SPA)',
              fontsize=11.5, fontweight='bold', pad=15, color='#0f172a')
    plt.tight_layout()
    plt.savefig(docs_img / 'fig_4_1_system_architecture.png', dpi=300)
    plt.close()
    print('Generated fig_4_1_system_architecture.png')

if __name__ == '__main__':
    generate_fig_2_1()
    generate_fig_2_2()
    generate_fig_2_3()
    generate_fig_3_1()
    generate_fig_4_1()
    print('All diagrams generated successfully!')
