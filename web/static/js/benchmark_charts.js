/**
 * Benchmark & Analytics Dashboard Controller (Chart.js & Metrics Cards)
 */
class BenchmarkDashboard {
    constructor() {
        this.speedupChart = null;
        this.efficiencyChart = null;
    }

    renderBenchmark(benchData, baselineData, metricsData) {
        this.renderSpeedupAndEfficiencyCharts(benchData);
        this.renderBenchmarkTable(benchData);
        this.renderMemoryComparisonCard(baselineData);
        this.renderAccuracyCard(metricsData, benchData);
    }

    renderSpeedupAndEfficiencyCharts(benchData) {
        if (!benchData || !benchData.results || benchData.results.length === 0) {
            return;
        }

        const results = benchData.results;
        const threadLabels = results.map(r => `${r.threads} Thread${r.threads > 1 ? 's' : ''}`);
        const threads = results.map(r => r.threads);
        const speedups = results.map(r => Number(r.speedup.toFixed(2)));
        const idealSpeedups = threads.map(t => t);
        const efficiencies = results.map(r => Number((r.efficiency * 100).toFixed(1)));

        // 1. Speedup S(p) Line Chart
        const speedupCtx = document.getElementById('chart-speedup')?.getContext('2d');
        if (speedupCtx) {
            if (this.speedupChart) this.speedupChart.destroy();
            this.speedupChart = new Chart(speedupCtx, {
                type: 'line',
                data: {
                    labels: threadLabels,
                    datasets: [
                        {
                            label: 'Measured Speedup S(p)',
                            data: speedups,
                            borderColor: '#38bdf8',
                            backgroundColor: 'rgba(56, 189, 248, 0.15)',
                            borderWidth: 3,
                            pointBackgroundColor: '#0284c7',
                            pointRadius: 5,
                            fill: true,
                            tension: 0.2
                        },
                        {
                            label: 'Ideal Linear S(p) = p',
                            data: idealSpeedups,
                            borderColor: '#94a3b8',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            pointRadius: 0,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#cbd5e1', font: { family: 'JetBrains Mono', size: 11 } } },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => ` ${ctx.dataset.label}: ${ctx.raw}x`
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: '#334155' },
                            ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } }
                        },
                        y: {
                            beginAtZero: true,
                            grid: { color: '#334155' },
                            ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } },
                            title: { display: true, text: 'Speedup Factor', color: '#94a3b8' }
                        }
                    }
                }
            });
        }

        // 2. Efficiency E(p) Bar Chart
        const effCtx = document.getElementById('chart-efficiency')?.getContext('2d');
        if (effCtx) {
            if (this.efficiencyChart) this.efficiencyChart.destroy();
            this.efficiencyChart = new Chart(effCtx, {
                type: 'bar',
                data: {
                    labels: threadLabels,
                    datasets: [
                        {
                            label: 'Parallel Efficiency E(p) %',
                            data: efficiencies,
                            backgroundColor: efficiencies.map(e => e >= 70 ? '#10b981' : (e >= 40 ? '#f59e0b' : '#ef4444')),
                            borderRadius: 4,
                            borderWidth: 0
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#cbd5e1', font: { family: 'JetBrains Mono', size: 11 } } },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => ` Efficiency: ${ctx.raw}%`
                            }
                        }
                    },
                    scales: {
                        x: {
                            grid: { color: '#334155' },
                            ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } }
                        },
                        y: {
                            beginAtZero: true,
                            max: 110,
                            grid: { color: '#334155' },
                            ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } },
                            title: { display: true, text: 'Efficiency (%)', color: '#94a3b8' }
                        }
                    }
                }
            });
        }
    }

    clear() {
        if (this.speedupChart) {
            this.speedupChart.destroy();
            this.speedupChart = null;
        }
        if (this.efficiencyChart) {
            this.efficiencyChart.destroy();
            this.efficiencyChart = null;
        }
        const tbody = document.getElementById('bench-table-body');
        if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-slate-500 text-xs">Run a benchmark to populate metrics table.</td></tr>`;
        const memCard = document.getElementById('memory-comparison-card');
        if (memCard) memCard.innerHTML = `<div class="p-5 text-center text-slate-500 text-xs">Run with Baseline Comparison to view memory complexity analysis.</div>`;
        const accCard = document.getElementById('accuracy-metrics-card');
        if (accCard) accCard.innerHTML = `<div class="p-5 text-center text-slate-500 text-xs">Select BAliBASE presets to evaluate SP & TC Scores.</div>`;
    }

    renderBenchmarkTable(benchData) {
        const tbody = document.getElementById('bench-table-body');
        if (!tbody) return;

        if (!benchData || !benchData.results || benchData.results.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-slate-500">Run a benchmark to populate scalability metrics.</td></tr>`;
            return;
        }

        let html = '';
        benchData.results.forEach(r => {
            const memMB = (r.peak_memory_bytes / (1024 * 1024)).toFixed(2);
            const hasRef = (r.sp_score > 0 || r.tc_score > 0);
            const spStr = hasRef ? r.sp_score.toFixed(4) : 'N/A';
            const tcStr = hasRef ? r.tc_score.toFixed(4) : 'N/A';

            html += `
                <tr class="border-b border-slate-800 hover:bg-slate-800/40 font-mono text-xs">
                    <td class="py-2.5 px-3 font-semibold text-slate-200">${r.threads}</td>
                    <td class="py-2.5 px-3 text-cyan-400 font-bold">${r.runtime_ms.toFixed(2)} ms</td>
                    <td class="py-2.5 px-3 text-sky-400">${r.speedup.toFixed(2)}x</td>
                    <td class="py-2.5 px-3 ${r.efficiency >= 0.7 ? 'text-emerald-400' : 'text-amber-400'}">${(r.efficiency * 100).toFixed(1)}%</td>
                    <td class="py-2.5 px-3 text-slate-400">${memMB} MB</td>
                    <td class="py-2.5 px-3 text-purple-400">${spStr}</td>
                    <td class="py-2.5 px-3 text-purple-400">${tcStr}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    }

    renderMemoryComparisonCard(baselineData) {
        const card = document.getElementById('memory-comparison-card');
        if (!card) return;

        if (!baselineData) {
            card.innerHTML = `
                <div class="p-5 text-center text-slate-500 text-xs">
                    <i class="fa-solid fa-microchip text-2xl mb-2 text-slate-600 block"></i>
                    Run with <strong class="text-slate-400">Baseline Comparison</strong> to test Gotoh O(mn) vs Myers-Miller O(min(m, n)).
                </div>
            `;
            return;
        }

        const gotoh = baselineData.gotoh;
        const mm = baselineData.myers_miller;
        const reduction = baselineData.memory_reduction_ratio || (gotoh.peak_memory_bytes / Math.max(1, mm.peak_memory_bytes));

        const gotohMemStr = gotoh.peak_memory_bytes > 1024 * 1024
            ? `${(gotoh.peak_memory_bytes / (1024 * 1024)).toFixed(2)} MB`
            : `${(gotoh.peak_memory_bytes / 1024).toFixed(1)} KB`;

        const mmMemStr = mm.peak_memory_bytes > 1024 * 1024
            ? `${(mm.peak_memory_bytes / (1024 * 1024)).toFixed(2)} MB`
            : `${(mm.peak_memory_bytes / 1024).toFixed(1)} KB`;

        card.innerHTML = `
            <div class="p-5 space-y-4">
                <div class="flex items-center justify-between">
                    <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Pairwise Memory Complexity</span>
                    <span class="px-2.5 py-1 rounded-full text-xs font-extrabold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                        ${reduction.toFixed(1)}x Less Memory
                    </span>
                </div>

                <div class="text-xs text-slate-300 font-mono bg-slate-950/80 p-2.5 rounded border border-slate-800">
                    <i class="fa-solid fa-dna text-indigo-400 mr-1.5"></i> ${baselineData.pair || 'Pairwise Sequences'}
                </div>

                <!-- Comparison Grid -->
                <div class="grid grid-cols-2 gap-3 font-mono text-xs">
                    <div class="bg-slate-900/90 p-3 rounded-lg border border-slate-800">
                        <div class="text-slate-400 text-[11px] mb-1 font-sans font-semibold">Gotoh NW Matrix</div>
                        <div class="text-[10px] text-slate-500 mb-2 font-mono">Complexity: O(mn) Quadratic</div>
                        <div class="text-base font-bold text-rose-400">${gotohMemStr}</div>
                        <div class="text-[11px] text-slate-400 mt-1">${gotoh.time_ms.toFixed(2)} ms (Score: ${gotoh.score})</div>
                    </div>

                    <div class="bg-slate-900/90 p-3 rounded-lg border border-emerald-900/50">
                        <div class="text-emerald-400 text-[11px] mb-1 font-sans font-semibold">Myers-Miller Hirschberg</div>
                        <div class="text-[10px] text-slate-500 mb-2 font-mono">Complexity: O(min(m, n)) Linear</div>
                        <div class="text-base font-bold text-emerald-400">${mmMemStr}</div>
                        <div class="text-[11px] text-slate-400 mt-1">${mm.time_ms.toFixed(2)} ms (Score: ${mm.score})</div>
                    </div>
                </div>

                <!-- Mathematical identity confirmation -->
                <div class="flex items-center gap-2 text-xs p-2 rounded bg-slate-950/60 border border-slate-800/80">
                    <i class="fa-solid fa-circle-check text-emerald-400"></i>
                    <span class="text-slate-300">Score Identity:</span>
                    <span class="font-bold text-emerald-300">${baselineData.score_identity ? '100% IDENTICAL (Gotoh == Myers-Miller)' : 'MISMATCH'}</span>
                </div>
            </div>
        `;
    }

    renderAccuracyCard(metricsData, benchData) {
        const card = document.getElementById('accuracy-metrics-card');
        if (!card) return;

        let sp = metricsData?.sp_score;
        let tc = metricsData?.tc_score;

        // If not in standard metrics, check benchmark results
        if (sp === undefined && benchData && benchData.results && benchData.results.length > 0) {
            sp = benchData.results[0].sp_score;
            tc = benchData.results[0].tc_score;
        }

        if (sp === undefined && tc === undefined) {
            card.innerHTML = `
                <div class="p-5 text-center text-slate-500 text-xs">
                    <i class="fa-solid fa-chart-line text-2xl mb-2 text-slate-600 block"></i>
                    Select <strong class="text-slate-400">BAliBASE RV11 or RV12</strong> presets to evaluate biological accuracy against gold-standard references.
                </div>
            `;
            return;
        }

        const spPct = (sp * 100).toFixed(1);
        const tcPct = (tc * 100).toFixed(1);

        card.innerHTML = `
            <div class="p-5 space-y-4">
                <div class="flex items-center justify-between">
                    <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">BAliBASE Benchmark Accuracy</span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">Gold Standard</span>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <!-- SP Score -->
                    <div class="bg-slate-900/90 p-3 rounded-lg border border-slate-800 flex flex-col justify-between">
                        <div>
                            <div class="text-slate-400 text-xs font-semibold">SP Score (Sum-of-Pairs)</div>
                            <div class="text-[10px] text-slate-500 mt-0.5">Fraction of correctly aligned residue pairs</div>
                        </div>
                        <div class="mt-3">
                            <div class="flex items-baseline justify-between mb-1">
                                <span class="text-xl font-bold font-mono text-purple-400">${sp.toFixed(4)}</span>
                                <span class="text-xs font-mono text-slate-400">${spPct}%</span>
                            </div>
                            <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                                <div class="bg-purple-500 h-full rounded-full transition-all" style="width: ${spPct}%"></div>
                            </div>
                        </div>
                    </div>

                    <!-- TC Score -->
                    <div class="bg-slate-900/90 p-3 rounded-lg border border-slate-800 flex flex-col justify-between">
                        <div>
                            <div class="text-slate-400 text-xs font-semibold">TC Score (Total Column)</div>
                            <div class="text-[10px] text-slate-500 mt-0.5">Fraction of entirely preserved columns</div>
                        </div>
                        <div class="mt-3">
                            <div class="flex items-baseline justify-between mb-1">
                                <span class="text-xl font-bold font-mono text-cyan-400">${tc.toFixed(4)}</span>
                                <span class="text-xs font-mono text-slate-400">${tcPct}%</span>
                            </div>
                            <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                                <div class="bg-cyan-500 h-full rounded-full transition-all" style="width: ${tcPct}%"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="text-[11px] text-slate-400 bg-slate-950/60 p-2.5 rounded border border-slate-800 leading-relaxed">
                    Evaluated against official BAliBASE Core Blocks. SP verifies pairwise homology accuracy; TC measures strict multialignment column fidelity.
                </div>
            </div>
        `;
    }
}

window.BenchmarkDashboard = BenchmarkDashboard;
