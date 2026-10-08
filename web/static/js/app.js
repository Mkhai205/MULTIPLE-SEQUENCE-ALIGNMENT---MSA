/**
 * MSA Pipeline Studio - Main Application Controller
 */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Core Viewers
    const msaViewer = new MsaViewer('msa-matrix-container');
    const treeViewer = new GuideTreeViewer('tree-visualizer-container');
    const benchDashboard = new BenchmarkDashboard();

    // App State
    let currentAlignedFasta = '';
    let currentNewick = '';
    let currentTreeJson = null;
    let currentBenchmarkJson = null;
    let selectedPresetId = null;

    // UI Elements
    const rawTextInput = document.getElementById('raw-seq-input');
    const dropZone = document.getElementById('file-drop-zone');
    const fileUploadInput = document.getElementById('file-upload-input');
    const runBtn = document.getElementById('run-align-btn');
    const resetBtn = document.getElementById('reset-btn');
    const statusDot = document.getElementById('engine-status-dot');
    const statusText = document.getElementById('engine-status-text');

    // Parameter Elements
    const threadsSlider = document.getElementById('threads-slider');
    const threadsVal = document.getElementById('threads-val');
    const gapOpenSlider = document.getElementById('gap-open-slider');
    const gapOpenVal = document.getElementById('gap-open-val');
    const gapExtendSlider = document.getElementById('gap-extend-slider');
    const gapExtendVal = document.getElementById('gap-extend-val');
    const modeSelects = document.querySelectorAll('input[name="align-mode"]');

    // Metrics Elements
    const metricTime = document.getElementById('metric-time');
    const metricMem = document.getElementById('metric-mem');
    const metricSeqs = document.getElementById('metric-seqs');
    const metricLen = document.getElementById('metric-len');
    const metricSp = document.getElementById('metric-sp');

    // 2. Health Check
    async function checkEngineHealth() {
        try {
            const res = await fetch('/api/health');
            const data = await res.json();
            if (data.executable_found) {
                statusDot.className = 'w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse';
                statusText.textContent = 'Engine Online (C++17 Release)';
            } else {
                statusDot.className = 'w-2.5 h-2.5 rounded-full bg-rose-500';
                statusText.textContent = 'Engine Offline (Binary not found)';
            }
        } catch (e) {
            statusDot.className = 'w-2.5 h-2.5 rounded-full bg-rose-500';
            statusText.textContent = 'Backend Offline';
        }
    }
    checkEngineHealth();

    // 3. Load Presets
    async function loadPresets() {
        const presetsContainer = document.getElementById('presets-list');
        if (!presetsContainer) return;

        try {
            const res = await fetch('/api/presets');
            const presets = await res.json();

            presetsContainer.innerHTML = '';
            presets.forEach(p => {
                const btn = document.createElement('button');
                btn.className = `preset-btn p-3 rounded-lg border text-left transition-all flex flex-col justify-between bg-slate-900/90 border-slate-700/80 hover:border-blue-500 hover:bg-slate-800/80 group`;
                btn.dataset.id = p.id;
                btn.innerHTML = `
                    <div class="flex items-center justify-between w-full mb-1">
                        <span class="text-xs font-bold text-slate-200 group-hover:text-blue-400 transition-colors">${p.name}</span>
                        <span class="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">${p.format.toUpperCase()}</span>
                    </div>
                    <p class="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">${p.description}</p>
                `;

                btn.addEventListener('click', () => selectPreset(p.id));
                presetsContainer.appendChild(btn);
            });
        } catch (e) {
            console.error('Failed to load presets:', e);
        }
    }
    loadPresets();

    async function selectPreset(presetId) {
        selectedPresetId = presetId;

        // Highlight preset button
        document.querySelectorAll('.preset-btn').forEach(b => {
            if (b.dataset.id === presetId) {
                b.classList.add('border-blue-500', 'bg-blue-950/30', 'ring-1', 'ring-blue-500');
            } else {
                b.classList.remove('border-blue-500', 'bg-blue-950/30', 'ring-1', 'ring-blue-500');
            }
        });

        try {
            const res = await fetch(`/api/preset/${presetId}`);
            const data = await res.json();
            rawTextInput.value = data.content;
            updateInputStats();

            // Set appropriate mode recommendation only for long_seq stress test
            if (presetId === 'long_seq') {
                const baselineRadio = document.querySelector('input[name="align-mode"][value="baseline"]');
                if (baselineRadio) baselineRadio.checked = true;
            }

            showToast(`Loaded preset: ${data.name}`);
        } catch (e) {
            showToast(`Failed to load preset ${presetId}`, true);
        }
    }

    // 4. Input Stats Counter
    function updateInputStats() {
        const text = rawTextInput.value.trim();
        const statsEl = document.getElementById('input-seq-count-badge');
        if (!statsEl) return;

        if (!text) {
            statsEl.textContent = '0 sequences detected';
            return;
        }

        let seqCount = 0;
        if (text.includes('PileUp') || text.includes('MSF:')) {
            const matches = text.match(/Name:\s+([^\s]+)/g);
            seqCount = matches ? matches.length : 0;
        } else {
            const matches = text.match(/^>[^\n\r]+/gm);
            seqCount = matches ? matches.length : 0;
        }

        statsEl.textContent = `${seqCount} sequence${seqCount === 1 ? '' : 's'} detected`;
    }
    rawTextInput.addEventListener('input', () => {
        selectedPresetId = null;
        document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('border-blue-500', 'bg-blue-950/30', 'ring-1', 'ring-blue-500'));
        updateInputStats();
    });

    // 5. Drag and Drop File Handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('border-blue-500', 'bg-slate-800/80'));
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('border-blue-500', 'bg-slate-800/80'));
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    dropZone.addEventListener('click', () => fileUploadInput.click());
    fileUploadInput.addEventListener('change', () => {
        if (fileUploadInput.files && fileUploadInput.files.length > 0) {
            handleFileUpload(fileUploadInput.files[0]);
        }
    });

    function handleFileUpload(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            rawTextInput.value = e.target.result;
            selectedPresetId = null;
            document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('border-blue-500', 'bg-blue-950/30', 'ring-1', 'ring-blue-500'));
            updateInputStats();
            showToast(`Uploaded file: ${file.name}`);
        };
        reader.readAsText(file);
    }

    // 6. Parameter Controls
    threadsSlider.addEventListener('input', () => {
        threadsVal.textContent = `${threadsSlider.value} T`;
    });

    gapOpenSlider.addEventListener('input', () => {
        gapOpenVal.textContent = gapOpenSlider.value;
    });

    gapExtendSlider.addEventListener('input', () => {
        gapExtendVal.textContent = gapExtendSlider.value;
    });

    // Quick thread pills
    document.querySelectorAll('.thread-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            threadsSlider.value = pill.dataset.val;
            threadsVal.textContent = `${pill.dataset.val} T`;
        });
    });

    // 7. Tab Switching
    const tabs = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active', 'border-blue-500', 'text-blue-400'));
            tabPanels.forEach(p => p.classList.add('hidden'));

            tab.classList.add('active', 'border-blue-500', 'text-blue-400');
            const targetId = tab.dataset.target;
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.remove('hidden');
                // Trigger chart or tree resize if active
                if (targetId === 'tab-tree') {
                    setTimeout(() => {
                        treeViewer.fitToScreen();
                        treeViewer.render();
                    }, 30);
                }
            }
        });
    });

    function switchTab(tabId) {
        const tabBtn = document.querySelector(`.tab-btn[data-target="${tabId}"]`);
        if (tabBtn) tabBtn.click();
    }

    // 8. Run Alignment Action
    runBtn.addEventListener('click', async () => {
        const text = rawTextInput.value.trim();
        if (!text && !selectedPresetId) {
            showToast('Please paste sequences, drop a file, or pick a demo preset.', true);
            return;
        }

        // Get Mode
        let mode = 'standard';
        modeSelects.forEach(radio => {
            if (radio.checked) mode = radio.value;
        });

        const threads = parseInt(threadsSlider.value, 10);
        const gapOpen = parseInt(gapOpenSlider.value, 10);
        const gapExtend = parseInt(gapExtendSlider.value, 10);

        // UI Loading state
        setRunningState(true);

        const payload = {
            raw_content: text,
            preset_id: selectedPresetId,
            threads: threads,
            gap_open: gapOpen,
            gap_extend: gapExtend,
            mode: mode,
            export_tree: true
        };

        try {
            const res = await fetch('/api/align', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Alignment failed on server.');
            }

            const data = await res.json();
            handleAlignmentResults(data);
            showToast('Alignment execution completed successfully!');
        } catch (e) {
            console.error('Execution error:', e);
            showToast(e.message, true);
        } finally {
            setRunningState(false);
        }
    });

    function setRunningState(isRunning) {
        if (isRunning) {
            runBtn.disabled = true;
            runBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-2"></i> Computing Alignment...`;
            runBtn.classList.add('opacity-75');
        } else {
            runBtn.disabled = false;
            runBtn.innerHTML = `<i class="fa-solid fa-play mr-2"></i> Run Alignment Pipeline`;
            runBtn.classList.remove('opacity-75');
        }
    }

    function handleAlignmentResults(data) {
        currentAlignedFasta = data.aligned_fasta || '';
        currentNewick = data.tree_newick || '';
        currentTreeJson = data.tree || null;
        currentBenchmarkJson = data.benchmark_data || null;

        // 1. Update Metrics Strip
        const metrics = data.metrics || {};
        metricTime.textContent = metrics.execution_time_ms ? `${metrics.execution_time_ms.toFixed(2)} ms` : '--';
        metricMem.textContent = metrics.peak_memory_mb ? `${metrics.peak_memory_mb.toFixed(2)} MB` : '--';
        metricSeqs.textContent = metrics.num_sequences ? `${metrics.num_sequences} seqs` : `${data.aligned_sequences?.length || '--'}`;
        metricLen.textContent = metrics.alignment_length ? `${metrics.alignment_length} cols` : '--';

        if (metrics.sp_score !== undefined) {
            metricSp.textContent = `${metrics.sp_score.toFixed(4)}`;
        } else if (data.baseline_comparison) {
            metricSp.textContent = `${data.baseline_comparison.memory_reduction_ratio?.toFixed(1)}x mem`;
        } else {
            metricSp.textContent = '--';
        }

        // 2. Load Alignment Matrix
        if (data.aligned_sequences && data.aligned_sequences.length > 0) {
            msaViewer.loadAlignment(data.aligned_sequences);
        }

        // 3. Load Guide Tree
        if (data.tree) {
            treeViewer.loadTree(data.tree, data.tree_newick);
        }

        // 4. Render Benchmark and Analytics
        benchDashboard.renderBenchmark(data.benchmark_data, data.baseline_comparison, metrics);

        // 5. Update Raw Logs
        const logsEl = document.getElementById('raw-stdout-output');
        if (logsEl) {
            logsEl.textContent = data.stdout + (data.stderr ? `\n--- STDERR ---\n${data.stderr}` : '');
        }

        // Automatic smart tab switch
        if (data.mode === 'benchmark') {
            switchTab('tab-benchmarks');
        } else if (data.mode === 'baseline') {
            switchTab('tab-benchmarks');
        } else {
            switchTab('tab-matrix');
        }
    }

    // 9. Reset Handler
    resetBtn.addEventListener('click', () => {
        rawTextInput.value = '';
        selectedPresetId = null;
        currentAlignedFasta = '';
        currentNewick = '';
        currentTreeJson = null;
        currentBenchmarkJson = null;

        document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('border-blue-500', 'bg-blue-950/30', 'ring-1', 'ring-blue-500'));
        updateInputStats();

        metricTime.textContent = '--';
        metricMem.textContent = '--';
        metricSeqs.textContent = '--';
        metricLen.textContent = '--';
        metricSp.textContent = '--';

        msaViewer.clear();
        treeViewer.clear();
        benchDashboard.clear();
        document.getElementById('raw-stdout-output').textContent = 'No logs yet.';

        showToast('Reset workspace state.');
    });

    // 10. Export Studio Handlers
    document.getElementById('export-download-fasta')?.addEventListener('click', () => {
        if (!currentAlignedFasta) return showToast('No aligned sequences to download.', true);
        downloadFile('msa_aligned.fasta', currentAlignedFasta, 'text/plain');
    });

    document.getElementById('export-download-nwk')?.addEventListener('click', () => {
        if (!currentNewick) return showToast('No guide tree to download.', true);
        downloadFile('msa_guide_tree.nwk', currentNewick, 'text/plain');
    });

    document.getElementById('export-download-svg')?.addEventListener('click', () => {
        if (!treeViewer || !treeViewer.treeData) return showToast('No guide tree to export as SVG.', true);
        treeViewer.downloadSvg();
    });

    document.getElementById('export-download-json')?.addEventListener('click', () => {
        if (!currentBenchmarkJson && !currentTreeJson && msaViewer.sequences.length === 0) {
            return showToast('No benchmark or alignment data to download.', true);
        }
        const report = {
            benchmark: currentBenchmarkJson,
            tree: currentTreeJson,
            alignment_sequences_count: msaViewer.sequences.length,
            alignment_length: msaViewer.alignmentLength
        };
        downloadFile('msa_benchmark_report.json', JSON.stringify(report, null, 2), 'application/json');
    });

    document.getElementById('export-copy-fasta')?.addEventListener('click', () => {
        if (!currentAlignedFasta) return showToast('No aligned sequences to copy.', true);
        navigator.clipboard.writeText(currentAlignedFasta);
        showToast('Aligned FASTA copied to clipboard!');
    });

    document.getElementById('export-copy-nwk')?.addEventListener('click', () => {
        if (!currentNewick) return showToast('No Newick tree to copy.', true);
        navigator.clipboard.writeText(currentNewick);
        showToast('Newick tree copied to clipboard!');
    });

    function downloadFile(filename, text, mimeType) {
        const blob = new Blob([text], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    // 11. Toast Notifications
    function showToast(message, isError = false) {
        const toast = document.getElementById('app-toast');
        if (!toast) return;

        toast.className = `fixed bottom-5 right-5 z-50 px-4 py-2.5 rounded-lg shadow-2xl text-xs font-semibold flex items-center gap-2 border transition-all duration-300 transform translate-y-0 opacity-100 ${
            isError ? 'bg-rose-900/90 text-rose-100 border-rose-700' : 'bg-emerald-900/90 text-emerald-100 border-emerald-700'
        }`;
        toast.innerHTML = `<i class="fa-solid ${isError ? 'fa-circle-exclamation' : 'fa-circle-check'} text-sm"></i> ${message}`;

        setTimeout(() => {
            toast.className = 'fixed bottom-5 right-5 z-50 px-4 py-2.5 rounded-lg shadow-2xl text-xs font-semibold flex items-center gap-2 border transition-all duration-300 transform translate-y-10 opacity-0 pointer-events-none';
        }, 3500);
    }
    window.showAppToast = showToast;

    // Auto-load default RV11 preset on first visit
    setTimeout(() => {
        selectPreset('rv11');
    }, 400);
});
