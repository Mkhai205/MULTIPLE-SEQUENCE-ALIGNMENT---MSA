/**
 * MSA Pipeline Studio - Streamlined Main Controller
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
    let currentMode = 'standard';

    // UI Elements
    const rawTextInput = document.getElementById('raw-seq-input');
    const dropIndicator = document.getElementById('drop-indicator');
    const fileUploadInput = document.getElementById('file-upload-input');
    const runBtn = document.getElementById('run-align-btn');
    const resetBtn = document.getElementById('reset-btn');
    const statusDot = document.getElementById('engine-status-dot');
    const statusText = document.getElementById('engine-status-text');

    // Export Buttons
    const exportFastaBtn = document.getElementById('export-download-fasta');
    const exportNwkBtn = document.getElementById('export-download-nwk');
    const exportSvgBtn = document.getElementById('export-download-svg');

    // Parameter Elements
    const threadsSlider = document.getElementById('threads-slider');
    const threadsVal = document.getElementById('threads-val');
    const gapOpenSlider = document.getElementById('gap-open-slider');
    const gapOpenVal = document.getElementById('gap-open-val');
    const gapExtendSlider = document.getElementById('gap-extend-slider');
    const gapExtendVal = document.getElementById('gap-extend-val');

    // Mode Buttons
    const modeBtnStandard = document.getElementById('mode-btn-standard');
    const modeBtnBenchmark = document.getElementById('mode-btn-benchmark');

    // Drawer Elements
    const logsDrawer = document.getElementById('logs-drawer');
    const logsBackdrop = document.getElementById('logs-drawer-backdrop');
    const logsContent = document.getElementById('logs-drawer-content');
    const btnOpenLogs = document.getElementById('btn-open-logs');
    const btnCloseLogs = document.getElementById('btn-close-logs');
    const btnCopyLogs = document.getElementById('btn-copy-logs');
    const stdoutOutput = document.getElementById('raw-stdout-output');

    // 2. Health Check
    async function checkEngineHealth() {
        try {
            const res = await fetch('/api/health');
            const data = await res.json();
            if (data.executable_found) {
                statusDot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
                statusText.textContent = 'Engine Online';
            } else {
                statusDot.className = 'w-2 h-2 rounded-full bg-rose-500';
                statusText.textContent = 'Binary Missing';
            }
        } catch (e) {
            statusDot.className = 'w-2 h-2 rounded-full bg-rose-500';
            statusText.textContent = 'Offline';
        }
    }
    checkEngineHealth();

    // 3. Load Presets as Compact Chips
    async function loadPresets() {
        const presetsContainer = document.getElementById('presets-chips');
        if (!presetsContainer) return;

        try {
            const res = await fetch('/api/presets');
            const presets = await res.json();

            presetsContainer.innerHTML = '';
            presets.forEach(p => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `preset-chip py-1.5 px-2 rounded-lg text-xs font-medium border text-left transition-all bg-slate-950/70 border-slate-800 hover:border-blue-500 hover:bg-slate-800/80 text-slate-300 flex items-center justify-between group`;
                btn.dataset.id = p.id;
                btn.title = p.description;

                // Short chip label
                let shortName = p.name;
                if (p.id === 'rv11') shortName = 'RV11 (BAliBASE)';
                else if (p.id === 'rv12') shortName = 'RV12 (BAliBASE)';
                else if (p.id === 'hemoglobin') shortName = 'Hemoglobin';
                else if (p.id === 'long_seq') shortName = 'Long Seq (Stress)';
                else if (p.id === 'large_20') shortName = '20-Seq Benchmark';
                else if (p.id === 'large_40') shortName = '40-Seq Benchmark';

                btn.innerHTML = `
                    <span class="truncate font-semibold text-[11px] group-hover:text-blue-400">${shortName}</span>
                    <span class="text-[9px] font-mono text-slate-500 ml-1 uppercase">${p.format}</span>
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

        // Highlight active preset chip
        document.querySelectorAll('.preset-chip').forEach(b => {
            if (b.dataset.id === presetId) {
                b.classList.add('border-blue-500', 'bg-blue-950/40', 'text-blue-300');
            } else {
                b.classList.remove('border-blue-500', 'bg-blue-950/40', 'text-blue-300');
            }
        });

        try {
            const res = await fetch(`/api/preset/${presetId}`);
            const data = await res.json();
            rawTextInput.value = data.content;
            updateInputStats();

            // Set recommended mode for long_seq, large_20, and large_40
            if (presetId === 'long_seq' || presetId === 'large_20' || presetId === 'large_40') {
                setMode('benchmark');
            }

            showToast(`Loaded ${data.name}`);
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
            statsEl.textContent = '0 seqs';
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

        statsEl.textContent = `${seqCount} seq${seqCount === 1 ? '' : 's'}`;
    }

    rawTextInput.addEventListener('input', () => {
        selectedPresetId = null;
        document.querySelectorAll('.preset-chip').forEach(b => {
            b.classList.remove('border-blue-500', 'bg-blue-950/40', 'text-blue-300');
        });
        updateInputStats();
    });

    // 5. Drag and Drop directly on Textarea
    if (rawTextInput && dropIndicator) {
        ['dragenter', 'dragover'].forEach(eventName => {
            rawTextInput.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropIndicator.classList.remove('opacity-0');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            rawTextInput.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropIndicator.classList.add('opacity-0');
            });
        });

        rawTextInput.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                loadFile(files[0]);
            }
        });
    }

    fileUploadInput?.addEventListener('change', () => {
        if (fileUploadInput.files && fileUploadInput.files.length > 0) {
            loadFile(fileUploadInput.files[0]);
        }
    });

    function loadFile(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            rawTextInput.value = e.target.result;
            selectedPresetId = null;
            document.querySelectorAll('.preset-chip').forEach(b => {
                b.classList.remove('border-blue-500', 'bg-blue-950/40', 'text-blue-300');
            });
            updateInputStats();
            showToast(`Uploaded: ${file.name}`);
        };
        reader.readAsText(file);
    }

    // 6. Mode Switcher (Standard vs Benchmark)
    function setMode(mode) {
        currentMode = mode;
        if (mode === 'standard') {
            modeBtnStandard.classList.add('active');
            modeBtnBenchmark.classList.remove('active');
        } else {
            modeBtnBenchmark.classList.add('active');
            modeBtnStandard.classList.remove('active');
        }
        // Sync radio input for backward compatibility
        const radio = document.querySelector(`input[name="align-mode"][value="${mode}"]`);
        if (radio) radio.checked = true;
    }

    modeBtnStandard?.addEventListener('click', () => setMode('standard'));
    modeBtnBenchmark?.addEventListener('click', () => setMode('benchmark'));

    // 7. Parameters Sliders
    threadsSlider?.addEventListener('input', () => {
        const val = threadsSlider.value;
        threadsVal.textContent = `${val} Thread${val > 1 ? 's' : ''}`;
    });

    gapOpenSlider?.addEventListener('input', () => {
        gapOpenVal.textContent = gapOpenSlider.value;
    });

    gapExtendSlider?.addEventListener('input', () => {
        gapExtendVal.textContent = gapExtendSlider.value;
    });

    // 8. Tab Navigation (3 Tabs)
    const tabs = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => {
                t.classList.remove('active', 'border-blue-500', 'text-blue-400');
                t.classList.add('border-transparent', 'text-slate-400');
            });
            tabPanels.forEach(p => p.classList.add('hidden'));

            tab.classList.add('active', 'border-blue-500', 'text-blue-400');
            tab.classList.remove('border-transparent', 'text-slate-400');

            const targetId = tab.dataset.target;
            const targetPanel = document.getElementById(targetId);
            if (targetPanel) {
                targetPanel.classList.remove('hidden');
                if (targetId === 'tab-tree') {
                    setTimeout(() => {
                        treeViewer.fitToScreen();
                        treeViewer.render();
                    }, 40);
                }
            }
        });
    });

    function switchTab(tabId) {
        const tabBtn = document.querySelector(`.tab-btn[data-target="${tabId}"]`);
        if (tabBtn) tabBtn.click();
    }

    // 9. Run Alignment Pipeline
    runBtn.addEventListener('click', async () => {
        const text = rawTextInput.value.trim();
        if (!text && !selectedPresetId) {
            showToast('Please enter sequences or select a quick preset.', true);
            return;
        }

        const threads = parseInt(threadsSlider.value, 10);
        const gapOpen = parseInt(gapOpenSlider.value, 10);
        const gapExtend = parseInt(gapExtendSlider.value, 10);

        setRunningState(true);

        const payload = {
            raw_content: text,
            preset_id: selectedPresetId,
            threads: threads,
            gap_open: gapOpen,
            gap_extend: gapExtend,
            mode: currentMode,
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
            showToast('Alignment completed successfully!');
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
            runBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1.5"></i> Running...`;
            runBtn.classList.add('opacity-75');
        } else {
            runBtn.disabled = false;
            runBtn.innerHTML = `<i class="fa-solid fa-play mr-1.5"></i> Run Alignment`;
            runBtn.classList.remove('opacity-75');
        }
    }

    function handleAlignmentResults(data) {
        currentAlignedFasta = data.aligned_fasta || '';
        currentNewick = data.tree_newick || '';
        currentTreeJson = data.tree || null;
        currentBenchmarkJson = data.benchmark_data || null;

        // 1. Load Alignment Matrix
        if (data.aligned_sequences && data.aligned_sequences.length > 0) {
            msaViewer.loadAlignment(data.aligned_sequences);
            // Update time and memory in matrix toolbar
            const timeMs = data.metrics?.execution_time_ms;
            const memMb = data.metrics?.peak_memory_mb;
            msaViewer.setExecutionMetrics(timeMs, memMb);
        }

        // 2. Load Guide Tree
        if (data.tree) {
            treeViewer.loadTree(data.tree, data.tree_newick);
        }

        // 3. Render Benchmark Dashboard
        benchDashboard.renderBenchmark(data.benchmark_data, data.baseline_comparison, data.metrics);

        // 4. Update Logs in Drawer
        if (stdoutOutput) {
            stdoutOutput.textContent = data.stdout + (data.stderr ? `\n--- STDERR ---\n${data.stderr}` : '');
        }

        // 5. Enable 1-Click Header Export buttons
        setExportButtonsEnabled(true);

        // 6. Automatic Smart Tab Switch
        if (data.mode === 'benchmark' || data.mode === 'baseline') {
            switchTab('tab-benchmarks');
        } else {
            switchTab('tab-matrix');
        }
    }

    function setExportButtonsEnabled(enabled) {
        if (exportFastaBtn) exportFastaBtn.disabled = !enabled;
        if (exportNwkBtn) exportNwkBtn.disabled = !enabled;
        if (exportSvgBtn) exportSvgBtn.disabled = !enabled;
    }

    // 10. Reset Workspace
    resetBtn.addEventListener('click', () => {
        rawTextInput.value = '';
        selectedPresetId = null;
        currentAlignedFasta = '';
        currentNewick = '';
        currentTreeJson = null;
        currentBenchmarkJson = null;

        document.querySelectorAll('.preset-chip').forEach(b => {
            b.classList.remove('border-blue-500', 'bg-blue-950/40', 'text-blue-300');
        });
        updateInputStats();

        msaViewer.clear();
        treeViewer.clear();
        benchDashboard.clear();

        if (stdoutOutput) stdoutOutput.textContent = 'No logs yet. Run an alignment to view output.';
        setExportButtonsEnabled(false);

        showToast('Workspace reset.');
    });

    // 11. 1-Click Header Export Downloads
    exportFastaBtn?.addEventListener('click', () => {
        if (!currentAlignedFasta) return showToast('No alignment data available.', true);
        downloadFile('aligned.fasta', currentAlignedFasta, 'text/plain');
        showToast('Downloaded aligned.fasta');
    });

    exportNwkBtn?.addEventListener('click', () => {
        if (!currentNewick) return showToast('No guide tree available.', true);
        downloadFile('guide_tree.nwk', currentNewick, 'text/plain');
        showToast('Downloaded guide_tree.nwk');
    });

    exportSvgBtn?.addEventListener('click', () => {
        if (!treeViewer || !treeViewer.treeData) return showToast('No tree image available.', true);
        treeViewer.downloadSvg();
        showToast('Downloaded guide_tree.svg');
    });

    function downloadFile(filename, content, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    // 12. Console Logs Slide-over Drawer Handlers
    function openLogsDrawer() {
        if (!logsDrawer) return;
        logsDrawer.classList.remove('pointer-events-none');
        logsBackdrop.classList.remove('opacity-0', 'pointer-events-none');
        logsContent.classList.remove('translate-x-full');
    }

    function closeLogsDrawer() {
        if (!logsDrawer) return;
        logsContent.classList.add('translate-x-full');
        logsBackdrop.classList.add('opacity-0', 'pointer-events-none');
        setTimeout(() => {
            logsDrawer.classList.add('pointer-events-none');
        }, 250);
    }

    btnOpenLogs?.addEventListener('click', openLogsDrawer);
    btnCloseLogs?.addEventListener('click', closeLogsDrawer);
    logsBackdrop?.addEventListener('click', closeLogsDrawer);

    btnCopyLogs?.addEventListener('click', () => {
        const text = stdoutOutput?.textContent || '';
        if (!text || text.includes('No logs yet')) return showToast('No logs to copy.', true);
        navigator.clipboard.writeText(text);
        showToast('Logs copied to clipboard!');
    });

    // Close drawer on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !logsContent.classList.contains('translate-x-full')) {
            closeLogsDrawer();
        }
    });

    // 13. Toast Notifications
    function showToast(message, isError = false) {
        const toast = document.getElementById('app-toast');
        if (!toast) return;

        toast.className = `fixed bottom-4 right-4 z-50 px-3.5 py-2 rounded-lg shadow-2xl text-xs font-semibold flex items-center gap-2 border transition-all duration-300 transform translate-y-0 opacity-100 ${
            isError ? 'bg-rose-900/90 text-rose-100 border-rose-700' : 'bg-emerald-900/90 text-emerald-100 border-emerald-700'
        }`;
        toast.innerHTML = `<i class="fa-solid ${isError ? 'fa-circle-exclamation' : 'fa-circle-check'} text-xs"></i> ${message}`;

        setTimeout(() => {
            toast.className = 'fixed bottom-4 right-4 z-50 px-3.5 py-2 rounded-lg shadow-2xl text-xs font-semibold flex items-center gap-2 border transition-all duration-300 transform translate-y-10 opacity-0 pointer-events-none';
        }, 3200);
    }
    window.showAppToast = showToast;

    // Auto-load default RV11 preset on first visit
    setTimeout(() => {
        selectPreset('rv11');
    }, 350);
});
