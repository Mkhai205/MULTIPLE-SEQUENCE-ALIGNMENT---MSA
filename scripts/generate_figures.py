#!/usr/bin/env python3
"""
Scientific Figure Generator for MSA Group 5 Report, Slides, and Poster
Uses matplotlib to generate high-resolution (300 DPI) publication-quality figures:
  1. fig1_memory_scaling.png: Gotoh NW vs Myers-Miller Hirschberg RAM usage (Log scale & Reduction ratio)
  2. fig2_speedup_scaling.png: Multi-threading OpenMP Speedup vs Ideal Linear & Amdahl's Law
  3. fig3_balibase_accuracy.png: SP & TC scores across BAliBASE 3.0 suites (RV11, RV12, RV20)
  4. fig4_tools_comparison.png: Benchmark comparison (Our Pipeline vs ClustalW vs MUSCLE vs Gotoh)
  5. fig5_parallel_architecture.png: Multi-tier OpenMP + MPI hybrid pipeline diagram
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
FIGURES_DIR = ROOT_DIR / "results" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Set global academic style
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.7

def generate_fig1_memory():
    """Figure 1: Peak RAM Gotoh O(N^2) vs Hirschberg O(N)"""
    cases = ['RV11 (85 aa)', 'Hemoglobin (147 aa)', 'RV20 (74 aa)', 'RV12 (421 aa)', 'Long Seq (897 aa)']
    gotoh_kb = [87038 / 1024, 254574 / 1024, 75918 / 1024, 2452798 / 1024, 9723566 / 1024]
    hirschberg_kb = [672 / 1024, 1144 / 1024, 600 / 1024, 3376 / 1024, 7184 / 1024]
    reductions = [129.5, 222.5, 126.5, 726.5, 1353.5]

    x = np.arange(len(cases))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(9, 5.2), dpi=300)

    rects1 = ax1.bar(x - width/2, gotoh_kb, width, label='Gotoh NW (O(N²))', color='#E11D48', alpha=0.9, edgecolor='#9F1239')
    rects2 = ax1.bar(x + width/2, hirschberg_kb, width, label='Myers-Miller Hirschberg (O(N))', color='#0284C7', alpha=0.9, edgecolor='#0369A1')

    ax1.set_ylabel('Peak Matrix Memory (KB) [Log Scale]', fontsize=11, fontweight='bold', color='#0F172A')
    ax1.set_yscale('log')
    ax1.set_xticks(x)
    ax1.set_xticklabels(cases, fontsize=9.5, fontweight='bold', color='#1E293B')
    ax1.legend(loc='upper left', framealpha=0.95, fontsize=10)
    ax1.grid(True, axis='y')

    # Secondary axis for reduction factor
    ax2 = ax1.twinx()
    line = ax2.plot(x, reductions, color='#D97706', marker='o', linewidth=2.5, markersize=8, label='Memory Reduction Factor')
    ax2.set_ylabel('Memory Reduction Factor (×)', fontsize=11, fontweight='bold', color='#D97706')
    ax2.tick_params(axis='y', labelcolor='#D97706')
    ax2.set_ylim(0, 1500)

    for i, txt in enumerate(reductions):
        ax2.annotate(f"{txt:.1f}×", (x[i], reductions[i] + 45), ha='center', fontsize=9.5, fontweight='bold', color='#B45309')

    plt.title('Memory Optimization: Traditional DP Gotoh O(N²) vs Hirschberg O(N)', fontsize=12.5, fontweight='bold', pad=15, color='#0F172A')
    fig.tight_layout()
    out_path = FIGURES_DIR / "fig1_memory_scaling.png"
    plt.savefig(out_path)
    plt.close()
    print(f"[GENERATED] {out_path.name}")

def generate_fig2_speedup():
    """Figure 2: Multi-threading OpenMP Speedup vs Ideal Linear & Amdahl's Law"""
    threads = [1, 2, 4, 8]
    ideal = [1.0, 2.0, 4.0, 8.0]
    
    # Amdahl theoretical with parallel fraction f = 0.85
    f = 0.85
    amdahl = [1.0 / ((1 - f) + f / p) for p in threads]

    # Actual measurements
    bb20001 = [1.0, 1.45, 1.73, 1.68]
    bench40 = [1.0, 1.38, 1.61, 1.55]
    bb12001 = [1.0, 1.20, 1.26, 1.22]

    plt.figure(figsize=(8.5, 5.2), dpi=300)
    plt.plot(threads, ideal, 'k--', label='Ideal Linear Speedup S(p)=p', linewidth=1.8, alpha=0.7)
    plt.plot(threads, amdahl, 'r-.', label="Amdahl's Upper Bound (f=85%)", linewidth=2.0)
    plt.plot(threads, bb20001, 'o-', color='#2563EB', label='BB20001 (16 seqs, RV20)', linewidth=2.5, markersize=7)
    plt.plot(threads, bench40, 's-', color='#10B981', label='Benchmark 40 seqs (780 pairs)', linewidth=2.5, markersize=7)
    plt.plot(threads, bb12001, '^-', color='#8B5CF6', label='BB12001 (11 long seqs, RV12)', linewidth=2.2, markersize=7)

    plt.xlabel('Number of OpenMP Worker Threads (p)', fontsize=11, fontweight='bold')
    plt.ylabel('Observed Speedup Ratio S(p)', fontsize=11, fontweight='bold')
    plt.title('Multi-Threaded Parallel Speedup across Concurrency Scales', fontsize=12.5, fontweight='bold', pad=15)
    plt.xticks(threads)
    plt.ylim(0.8, 4.5)
    plt.grid(True)
    plt.legend(loc='upper left', framealpha=0.95, fontsize=9.5)
    plt.tight_layout()

    out_path = FIGURES_DIR / "fig2_speedup_scaling.png"
    plt.savefig(out_path)
    plt.close()
    print(f"[GENERATED] {out_path.name}")

def generate_fig3_accuracy():
    """Figure 3: Biological Accuracy SP and TC Scores across BAliBASE 3.0 Suites"""
    suites = ['RV11 (<20% ID)\nDifficult Divergent', 'RV12 (20-40% ID)\nMedium Identity', 'RV20\nLarge Families']
    
    # Average SP and TC scores computed from experimental benchmark
    sp_means = [0.5311, 0.8684, 0.5556]
    tc_means = [0.2941, 0.6806, 0.0000]

    x = np.arange(len(suites))
    width = 0.32

    fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=300)
    rects1 = ax.bar(x - width/2, sp_means, width, label='Sum-of-Pairs (SP Score)', color='#059669', edgecolor='#047857', alpha=0.9)
    rects2 = ax.bar(x + width/2, tc_means, width, label='Total Column (TC Score)', color='#3B82F6', edgecolor='#1D4ED8', alpha=0.9)

    ax.set_ylabel('Biological Alignment Score (0.0 - 1.0)', fontsize=11, fontweight='bold')
    ax.set_title('Biological Accuracy Evaluation on BAliBASE 3.0 Reference Suites', fontsize=12.5, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(suites, fontsize=10, fontweight='bold')
    ax.set_ylim(0, 1.1)
    ax.grid(True, axis='y')
    ax.legend(loc='upper right', framealpha=0.95, fontsize=10)

    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f'{h:.3f}', (rect.get_x() + rect.get_width()/2, h + 0.02),
                    ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#047857')

    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f'{h:.3f}', (rect.get_x() + rect.get_width()/2, h + 0.02),
                    ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1D4ED8')

    plt.tight_layout()
    out_path = FIGURES_DIR / "fig3_balibase_accuracy.png"
    plt.savefig(out_path)
    plt.close()
    print(f"[GENERATED] {out_path.name}")

def generate_fig4_comparison():
    """Figure 4: Comparative Evaluation against ClustalW and MUSCLE"""
    tools = ['Traditional Gotoh DP', 'ClustalW 2.1', 'MUSCLE v3.8', 'Group 5 (Parallel Hirschberg)']
    ram_mb = [320.0, 48.5, 52.0, 26.8]  # Representative RAM on BB20001
    sp_score = [0.488, 0.472, 0.495, 0.488]

    x = np.arange(len(tools))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=300)

    # Subplot 1: RAM consumption
    colors_ram = ['#E11D48', '#F59E0B', '#3B82F6', '#10B981']
    bars1 = ax1.bar(x, ram_mb, color=colors_ram, edgecolor='#334155', alpha=0.9, width=0.55)
    ax1.set_ylabel('Peak RAM Usage (MB)', fontsize=10.5, fontweight='bold')
    ax1.set_title('(A) Peak RAM Footprint on BB20001', fontsize=11, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(tools, rotation=22, ha='right', fontsize=9, fontweight='bold')
    ax1.grid(True, axis='y')
    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(f'{h:.1f} MB', (bar.get_x() + bar.get_width()/2, h + 8),
                     ha='center', fontsize=9, fontweight='bold')

    # Subplot 2: Alignment SP Score
    colors_sp = ['#64748B', '#F59E0B', '#3B82F6', '#10B981']
    bars2 = ax2.bar(x, sp_score, color=colors_sp, edgecolor='#334155', alpha=0.9, width=0.55)
    ax2.set_ylabel('Sum-of-Pairs (SP Score)', fontsize=10.5, fontweight='bold')
    ax2.set_title('(B) Biological Accuracy (SP Score)', fontsize=11, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(tools, rotation=22, ha='right', fontsize=9, fontweight='bold')
    ax2.set_ylim(0, 0.65)
    ax2.grid(True, axis='y')
    for bar in bars2:
        h = bar.get_height()
        ax2.annotate(f'{h:.3f}', (bar.get_x() + bar.get_width()/2, h + 0.015),
                     ha='center', fontsize=9, fontweight='bold')

    plt.suptitle('Comparative Benchmark: Memory Footprint vs Biological Accuracy', fontsize=12.5, fontweight='bold', y=0.98)
    plt.tight_layout()
    out_path = FIGURES_DIR / "fig4_tools_comparison.png"
    plt.savefig(out_path)
    plt.close()
    print(f"[GENERATED] {out_path.name}")

from matplotlib.patches import FancyBboxPatch

def generate_fig5_architecture():
    """Figure 5: Parallel Multi-Tier Architecture Diagram"""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    ax.axis('off')

    # Draw boxes
    boxes = [
        ("Input Raw Sequences\nS = {S1, S2, ..., Sk}\n(FASTA format)", 0.05, 0.68, 0.22, 0.22, '#E0F2FE', '#0284C7'),
        ("Stage 1: All-Pairs Distance Matrix\n• MPI: Block-Cyclic across Nodes\n• OpenMP: Dynamic multi-threading\nO(k²·N² / P)", 0.38, 0.68, 0.26, 0.22, '#FEF3C7', '#D97706'),
        ("Stage 2: Guide Tree Construction\n• UPGMA Hierarchical Clustering\n• Branch Independence Detection", 0.72, 0.68, 0.24, 0.22, '#F3E8FF', '#9333EA'),
        ("Stage 3: Wavefront Tree Scheduler\n• Level-by-Level parallel execution\n• Non-overlapping subtree profiles", 0.72, 0.15, 0.24, 0.24, '#DCFCE7', '#16A34A'),
        ("Stage 4: Progressive Profile Alignment\n• Myers-Miller Hirschberg O(N)\n• Forward/Backward DP vectors\n• Optimal memory bound: O(k·N)", 0.38, 0.15, 0.26, 0.24, '#FEE2E2', '#DC2626'),
        ("Final Aligned Sequences\n• Sum-of-Pairs Optimized\n• Output: FASTA / Clustal / MSF", 0.05, 0.15, 0.22, 0.24, '#F1F5F9', '#475569'),
    ]

    for text, bx, by, bw, bh, bg, border in boxes:
        rect = FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.01,rounding_size=0.02",
                              facecolor=bg, edgecolor=border, linewidth=2.0)
        ax.add_patch(rect)
        ax.text(bx + bw/2, by + bh/2, text, ha='center', va='center', fontsize=9.2, fontweight='bold', color='#0F172A')

    # Draw arrows
    arrows = [
        ((0.27, 0.79), (0.38, 0.79)),
        ((0.64, 0.79), (0.72, 0.79)),
        ((0.84, 0.68), (0.84, 0.39)),
        ((0.72, 0.27), (0.64, 0.27)),
        ((0.38, 0.27), (0.27, 0.27)),
    ]
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='#0F172A', lw=2.2))

    plt.title('Hybrid Multi-Tier Parallel Architecture (MPI + OpenMP + Hirschberg D&C)', fontsize=12.5, fontweight='bold', pad=10)
    plt.tight_layout()
    out_path = FIGURES_DIR / "fig5_parallel_architecture.png"
    plt.savefig(out_path)
    plt.close()
    print(f"[GENERATED] {out_path.name}")

if __name__ == '__main__':
    print("="*60)
    print("  GENERATING SCIENTIFIC BENCHMARK FIGURES")
    print("="*60)
    generate_fig1_memory()
    generate_fig2_speedup()
    generate_fig3_accuracy()
    generate_fig4_comparison()
    generate_fig5_architecture()
    print("All figures successfully created in results/figures/")
