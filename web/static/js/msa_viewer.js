/**
 * Interactive Color-Coded MSA Matrix Viewer (Jalview / ClustalX style)
 */
class MsaViewer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = Object.assign({
            cellSize: 20, // px width and height
            colorScheme: 'clustal', // 'clustal', 'hydrophobic', 'conservation', 'mono'
            fontSize: 12
        }, options);

        this.sequences = []; // [{ id, description, sequence }]
        this.alignmentLength = 0;
        this.consensus = [];
        this.conservation = []; // array of floats 0..1
        this.searchPattern = '';
        this.activeHighlightCol = -1;

        this.init();
    }

    init() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
                <!-- Toolbar -->
                <div class="flex flex-wrap items-center justify-between px-4 py-2 bg-slate-800/80 border-b border-slate-700/60 text-xs text-slate-300 gap-3">
                    <div class="flex items-center gap-4">
                        <span class="font-semibold text-slate-200 flex items-center gap-1.5">
                            <i class="fa-solid fa-table-cells text-indigo-400"></i> Alignment Matrix
                        </span>
                        <span id="msa-stats-badge" class="px-2 py-0.5 rounded bg-slate-700 text-slate-300 font-mono">0 seqs × 0 cols</span>
                    </div>

                    <div class="flex items-center flex-wrap gap-3">
                        <!-- Search Motif -->
                        <div class="relative">
                            <input id="msa-search-input" type="text" placeholder="Find motif (e.g. WKTM)..."
                                class="bg-slate-900 text-slate-200 text-xs px-2.5 py-1 pl-7 rounded border border-slate-700 focus:outline-none focus:border-blue-500 font-mono uppercase w-44" />
                            <i class="fa-solid fa-magnifying-glass absolute left-2 top-2 text-slate-500 text-xs"></i>
                        </div>

                        <!-- Color Scheme Select -->
                        <div class="flex items-center gap-1.5">
                            <label class="text-slate-400 font-medium">Palette:</label>
                            <select id="msa-scheme-select" class="bg-slate-900 text-slate-200 text-xs px-2 py-1 rounded border border-slate-700 focus:outline-none focus:border-blue-500">
                                <option value="clustal">ClustalX / Biochemical</option>
                                <option value="hydrophobic">Hydrophobicity</option>
                                <option value="conservation">Conservation Highlight</option>
                                <option value="mono">Monochrome</option>
                            </select>
                        </div>

                        <!-- Zoom Slider -->
                        <div class="flex items-center gap-1.5">
                            <label class="text-slate-400 font-medium"><i class="fa-solid fa-magnifying-glass-plus"></i></label>
                            <input id="msa-zoom-slider" type="range" min="14" max="28" value="20" class="w-20 accent-blue-500 cursor-pointer" />
                        </div>
                    </div>
                </div>

                <!-- Biochemical Legend Strip -->
                <div id="msa-legend-bar" class="flex items-center gap-4 px-4 py-1.5 bg-slate-950/60 border-b border-slate-800 text-[11px] text-slate-400 overflow-x-auto">
                    <span class="font-semibold text-slate-300">Residue Types:</span>
                    <span class="inline-flex items-center gap-1"><span class="w-3 h-3 rounded aa-hydrophobic"></span> Hydrophobic (A,I,L,M,F,W,V)</span>
                    <span class="inline-flex items-center gap-1"><span class="w-3 h-3 rounded aa-polar"></span> Polar (N,Q,S,T,Y,C)</span>
                    <span class="inline-flex items-center gap-1"><span class="w-3 h-3 rounded aa-positive"></span> Positive (K,R,H)</span>
                    <span class="inline-flex items-center gap-1"><span class="w-3 h-3 rounded aa-negative"></span> Negative (D,E)</span>
                    <span class="inline-flex items-center gap-1"><span class="w-3 h-3 rounded aa-gly-pro"></span> Gly/Pro (G,P)</span>
                    <span class="inline-flex items-center gap-1"><span class="w-3 h-3 rounded aa-gap"></span> Gap (-)</span>
                </div>

                <!-- Main Viewport Area -->
                <div class="relative flex-1 flex overflow-hidden">
                    <!-- Sticky Sequence Names Column -->
                    <div id="msa-names-col" class="w-48 flex-shrink-0 bg-slate-950/90 border-r border-slate-800 overflow-y-hidden z-20 select-none">
                        <!-- Top left corner spacer (matches ruler height, sticky) -->
                        <div class="sticky top-0 h-8 border-b border-slate-800 bg-slate-900/95 px-3 flex items-center justify-between text-[11px] font-semibold text-slate-400 z-10">
                            <span>Sequence ID</span>
                            <span>Len</span>
                        </div>
                        <!-- Sequence IDs list -->
                        <div id="msa-names-list" class="flex flex-col text-xs text-slate-300 font-mono-seq"></div>
                        <!-- Consensus label spacer -->
                        <div class="h-7 border-t border-b border-slate-800 bg-slate-900/95 px-3 flex items-center text-[11px] font-semibold text-amber-400">
                            <span>Consensus</span>
                        </div>
                        <!-- Histogram label spacer -->
                        <div class="h-10 border-b border-slate-800 bg-slate-900/95 px-3 flex items-center text-[11px] font-semibold text-cyan-400">
                            <span>Conservation</span>
                        </div>
                    </div>

                    <!-- Scrollable Alignment Matrix Grid -->
                    <div id="msa-grid-scroll" class="flex-1 overflow-auto bg-slate-950 font-mono-seq">
                        <div id="msa-grid-inner" class="relative inline-block min-w-full">
                            <!-- Position Ruler (Sticky Top) -->
                            <div id="msa-ruler-row" class="sticky top-0 h-8 bg-slate-900/95 border-b border-slate-800 flex items-end select-none z-10 text-[10px] text-slate-400"></div>

                            <!-- Alignment Sequences Rows -->
                            <div id="msa-matrix-rows" class="flex flex-col"></div>

                            <!-- Consensus Row -->
                            <div id="msa-consensus-row" class="h-7 bg-slate-900/95 border-t border-b border-slate-800 flex items-center select-none text-xs font-bold text-amber-400"></div>

                            <!-- Conservation Histogram Row -->
                            <div id="msa-histogram-row" class="h-10 bg-slate-900/60 border-b border-slate-800 flex items-end select-none"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Floating Hover Tooltip -->
            <div id="msa-tooltip" class="tooltip-custom bg-slate-800 border border-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg shadow-xl pointer-events-none"></div>
        `;

        this.bindEvents();
    }

    bindEvents() {
        const schemeSelect = document.getElementById('msa-scheme-select');
        if (schemeSelect) {
            schemeSelect.addEventListener('change', (e) => {
                this.options.colorScheme = e.target.value;
                this.render();
            });
        }

        const zoomSlider = document.getElementById('msa-zoom-slider');
        if (zoomSlider) {
            zoomSlider.addEventListener('input', (e) => {
                this.options.cellSize = parseInt(e.target.value, 10);
                this.options.fontSize = Math.max(9, Math.round(this.options.cellSize * 0.6));
                this.render();
            });
        }

        const searchInput = document.getElementById('msa-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchPattern = e.target.value.trim().toUpperCase();
                this.render();
            });
        }

        // Synchronize vertical scroll between names column and grid
        const gridScroll = document.getElementById('msa-grid-scroll');
        const namesCol = document.getElementById('msa-names-col');
        if (gridScroll && namesCol) {
            gridScroll.addEventListener('scroll', () => {
                namesCol.scrollTop = gridScroll.scrollTop;
            });
            namesCol.addEventListener('wheel', (e) => {
                gridScroll.scrollTop += e.deltaY;
                e.preventDefault();
            }, { passive: false });
        }
    }

    loadAlignment(sequences) {
        this.sequences = sequences || [];
        if (this.sequences.length === 0) {
            this.clear();
            return;
        }

        this.alignmentLength = Math.max(...this.sequences.map(s => s.sequence.length));
        this.computeConsensusAndConservation();

        const badge = document.getElementById('msa-stats-badge');
        if (badge) {
            badge.textContent = `${this.sequences.length} seqs × ${this.alignmentLength} cols`;
        }

        this.render();
    }

    clear() {
        this.sequences = [];
        this.alignmentLength = 0;
        this.consensus = [];
        this.conservation = [];

        const badge = document.getElementById('msa-stats-badge');
        if (badge) badge.textContent = `0 seqs × 0 cols`;

        document.getElementById('msa-names-list').innerHTML = '';
        document.getElementById('msa-ruler-row').innerHTML = '';
        document.getElementById('msa-matrix-rows').innerHTML = '';
        document.getElementById('msa-consensus-row').innerHTML = '';
        document.getElementById('msa-histogram-row').innerHTML = '';
    }

    computeConsensusAndConservation() {
        const numSeqs = this.sequences.length;
        this.consensus = [];
        this.conservation = [];

        if (numSeqs === 0 || this.alignmentLength === 0) return;

        for (let col = 0; col < this.alignmentLength; col++) {
            const counts = {};
            let nonGapCount = 0;

            for (let i = 0; i < numSeqs; i++) {
                const char = (this.sequences[i].sequence[col] || '-').toUpperCase();
                counts[char] = (counts[char] || 0) + 1;
                if (char !== '-') {
                    nonGapCount++;
                }
            }

            let bestChar = '-';
            let bestCount = 0;

            for (const [char, count] of Object.entries(counts)) {
                if (char !== '-' && count > bestCount) {
                    bestCount = count;
                    bestChar = char;
                }
            }

            // Conservation score: proportion of the most common residue among non-gaps
            let consScore = 0;
            if (nonGapCount > 0) {
                consScore = bestCount / numSeqs;
            }

            // Consensus symbol
            let consSymbol = '-';
            if (nonGapCount === 0) {
                consSymbol = '-';
            } else if (consScore === 1.0) {
                consSymbol = bestChar; // 100% invariant
            } else if (consScore >= 0.6) {
                consSymbol = bestChar.toLowerCase(); // strongly conserved
            } else if (consScore >= 0.4) {
                consSymbol = '+'; // moderately conserved
            } else {
                consSymbol = '.'; // variable
            }

            this.consensus.push({ char: consSymbol, dominant: bestChar, score: consScore });
            this.conservation.push(consScore);
        }
    }

    getResidueClass(char, colIdx = -1) {
        char = (char || '-').toUpperCase();

        if (char === '-') return 'aa-gap';

        if (this.options.colorScheme === 'mono') {
            return 'bg-slate-800 text-slate-200 border-slate-700';
        }

        if (this.options.colorScheme === 'conservation') {
            const cons = this.conservation[colIdx] || 0;
            if (cons >= 0.9) return 'bg-cyan-500 text-slate-950 font-bold';
            if (cons >= 0.6) return 'bg-sky-700 text-sky-100 font-semibold';
            if (cons >= 0.4) return 'bg-slate-700 text-slate-200';
            return 'bg-slate-800 text-slate-400';
        }

        if (this.options.colorScheme === 'hydrophobic') {
            // Kyte-Doolittle hydrophobic scale approximation
            if ('IVLF'.includes(char)) return 'aa-hydro-high';
            if ('MCWA'.includes(char)) return 'aa-hydro-med';
            return 'aa-hydro-low';
        }

        // Default: ClustalX / Biochemical groups
        if ('AILMFWV'.includes(char)) return 'aa-hydrophobic';
        if ('NQSTYC'.includes(char)) return 'aa-polar';
        if ('KRH'.includes(char)) return 'aa-positive';
        if ('DE'.includes(char)) return 'aa-negative';
        if ('GP'.includes(char)) return 'aa-gly-pro';

        return 'aa-polar';
    }

    setColumnHighlight(col) {
        if (this.activeHighlightCol === col) return;
        this.clearColumnHighlight();
        if (!col || col < 1) return;
        this.activeHighlightCol = col;
        const targets = this.container.querySelectorAll(`[data-col="${col}"]`);
        targets.forEach(el => el.classList.add('col-highlight'));
    }

    clearColumnHighlight() {
        if (this.activeHighlightCol !== -1) {
            const targets = this.container.querySelectorAll('.col-highlight');
            targets.forEach(el => el.classList.remove('col-highlight'));
            this.activeHighlightCol = -1;
        }
    }

    render() {
        if (this.sequences.length === 0) return;

        const cellW = this.options.cellSize;
        const cellH = this.options.cellSize;
        const fSize = this.options.fontSize;
        const totalW = this.alignmentLength * cellW;

        // Precompute motif search match intervals (highlights all letters of match)
        const matchIntervals = [];
        let totalMatches = 0;
        if (this.searchPattern && this.searchPattern.length > 0) {
            const pat = this.searchPattern;
            const patLen = pat.length;
            this.sequences.forEach((seq, sIdx) => {
                const seqUpper = seq.sequence.toUpperCase();
                let startPos = 0;
                while ((startPos = seqUpper.indexOf(pat, startPos)) !== -1) {
                    matchIntervals.push({ seqIdx: sIdx, start: startPos, end: startPos + patLen });
                    totalMatches++;
                    startPos++;
                }
            });
        }

        const badge = document.getElementById('msa-stats-badge');
        if (badge) {
            if (this.searchPattern) {
                badge.textContent = `${this.sequences.length} seqs × ${this.alignmentLength} cols (${totalMatches} match${totalMatches === 1 ? '' : 'es'})`;
            } else {
                badge.textContent = `${this.sequences.length} seqs × ${this.alignmentLength} cols`;
            }
        }

        // 1. Render Sticky Names Column
        const namesList = document.getElementById('msa-names-list');
        let namesHtml = '';
        this.sequences.forEach((seq, idx) => {
            const unalignedLen = seq.sequence.replace(/-/g, '').length;
            namesHtml += `
                <div class="px-3 flex items-center justify-between border-b border-slate-800/80 hover:bg-slate-800/50 transition-colors"
                     style="height: ${cellH}px;">
                    <span class="truncate max-w-[120px] text-slate-200 font-medium" title="${seq.id} ${seq.description}">
                        ${seq.id}
                    </span>
                    <span class="text-[10px] text-slate-500 font-mono">${unalignedLen}</span>
                </div>
            `;
        });
        namesList.innerHTML = namesHtml;

        // 2. Render Position Ruler
        const rulerRow = document.getElementById('msa-ruler-row');
        rulerRow.style.width = `${totalW}px`;
        let rulerHtml = '';
        for (let col = 0; col < this.alignmentLength; col++) {
            const pos = col + 1;
            const isMajor = (pos === 1 || pos % 10 === 0);
            const isMid = (pos % 5 === 0);

            rulerHtml += `
                <div class="relative flex-shrink-0 flex items-end justify-center border-r border-slate-800/40 cursor-pointer"
                     data-col="${pos}"
                     style="width: ${cellW}px; height: 100%;">
                    ${isMajor ? `
                        <span class="absolute bottom-2 text-[9px] font-mono text-slate-400 font-bold whitespace-nowrap"
                              style="left: 50%; transform: translateX(-50%);">
                            ${pos}
                        </span>
                        <div class="w-0.5 h-2 bg-slate-500"></div>
                    ` : (isMid ? `
                        <div class="w-0.5 h-1.5 bg-slate-700"></div>
                    ` : `
                        <div class="w-0.5 h-1 bg-slate-800"></div>
                    `)}
                </div>
            `;
        }
        rulerRow.innerHTML = rulerHtml;

        // 3. Render Matrix Rows
        const matrixRows = document.getElementById('msa-matrix-rows');
        matrixRows.style.width = `${totalW}px`;

        let matrixHtml = '';
        this.sequences.forEach((seq, seqIdx) => {
            matrixHtml += `<div class="flex flex-row border-b border-slate-900/80" style="height: ${cellH}px;">`;

            for (let col = 0; col < this.alignmentLength; col++) {
                const char = (seq.sequence[col] || '-').toUpperCase();
                const colorClass = this.getResidueClass(char, col);

                // Check search highlight (all characters in match interval)
                const isSearchMatch = matchIntervals.some(m => m.seqIdx === seqIdx && col >= m.start && col < m.end);
                const searchClass = isSearchMatch ? 'ring-2 ring-yellow-400 z-10' : '';

                matrixHtml += `
                    <div class="msa-cell ${colorClass} ${searchClass}"
                         data-seq-id="${seq.id}"
                         data-char="${char}"
                         data-col="${col + 1}"
                         style="width: ${cellW}px; height: ${cellH}px; font-size: ${fSize}px;">
                        ${char}
                    </div>
                `;
            }

            matrixHtml += `</div>`;
        });
        matrixRows.innerHTML = matrixHtml;

        // 4. Render Consensus Row
        const consRow = document.getElementById('msa-consensus-row');
        consRow.style.width = `${totalW}px`;
        let consHtml = '';
        for (let col = 0; col < this.alignmentLength; col++) {
            const item = this.consensus[col] || { char: '-', score: 0 };
            const isIdentical = item.score === 1.0;
            const style = isIdentical ? 'text-emerald-400 font-extrabold' : (item.score >= 0.6 ? 'text-amber-300 font-bold' : 'text-slate-500');

            consHtml += `
                <div class="msa-cell ${style}"
                     data-col="${col + 1}"
                     style="width: ${cellW}px; height: 100%; font-size: ${fSize}px;"
                     title="Consensus: ${item.char} (${Math.round(item.score * 100)}% conserved)">
                    ${item.char}
                </div>
            `;
        }
        consRow.innerHTML = consHtml;

        // 5. Render Conservation Histogram Row
        const histRow = document.getElementById('msa-histogram-row');
        histRow.style.width = `${totalW}px`;
        let histHtml = '';
        for (let col = 0; col < this.alignmentLength; col++) {
            const score = this.conservation[col] || 0; // 0..1
            const heightPercent = Math.max(4, Math.round(score * 100));

            let barColor = '#ef4444'; // Red < 40%
            if (score >= 0.75) {
                barColor = '#10b981'; // Green >= 75%
            } else if (score >= 0.4) {
                barColor = '#f59e0b'; // Amber >= 40%
            }

            histHtml += `
                <div class="flex items-end justify-center group relative cursor-pointer"
                     data-col="${col + 1}"
                     style="width: ${cellW}px; height: 100%;">
                    <div class="histogram-bar w-full mx-0.5 rounded-t-sm"
                         style="height: ${heightPercent}%; background-color: ${barColor};"
                         title="Col ${col + 1}: ${Math.round(score * 100)}% conservation">
                    </div>
                </div>
            `;
        }
        histRow.innerHTML = histHtml;

        this.setupCellTooltips();
        this.setupColumnHighlightListeners();
    }

    setupColumnHighlightListeners() {
        const rulerTicks = this.container.querySelectorAll('#msa-ruler-row [data-col]');
        rulerTicks.forEach(tick => {
            tick.addEventListener('mouseenter', () => {
                const col = parseInt(tick.dataset.col, 10);
                this.setColumnHighlight(col);
            });
            tick.addEventListener('mouseleave', () => {
                this.clearColumnHighlight();
            });
        });
    }

    setupCellTooltips() {
        const tooltip = document.getElementById('msa-tooltip');
        if (!tooltip) return;

        const cells = this.container.querySelectorAll('.msa-cell[data-seq-id]');
        cells.forEach(cell => {
            cell.addEventListener('mouseenter', (e) => {
                const seqId = cell.dataset.seqId;
                const char = cell.dataset.char;
                const col = parseInt(cell.dataset.col, 10);
                this.setColumnHighlight(col);

                const cons = Math.round((this.conservation[col - 1] || 0) * 100);

                let propName = 'Gap';
                if ('AILMFWV'.includes(char)) propName = 'Hydrophobic';
                else if ('NQSTYC'.includes(char)) propName = 'Polar / Neutral';
                else if ('KRH'.includes(char)) propName = 'Positively Charged';
                else if ('DE'.includes(char)) propName = 'Negatively Charged';
                else if ('GP'.includes(char)) propName = 'Conformational (Gly/Pro)';

                tooltip.innerHTML = `
                    <div class="font-bold text-slate-100">${seqId}</div>
                    <div class="text-xs text-slate-300">Residue: <span class="font-mono text-cyan-400 font-bold">${char}</span> (${propName})</div>
                    <div class="text-[11px] text-slate-400">Position: Col ${col} | Conservation: ${cons}%</div>
                `;

                const rect = cell.getBoundingClientRect();
                tooltip.style.left = `${rect.left + window.scrollX + 15}px`;
                tooltip.style.top = `${rect.top + window.scrollY - 30}px`;
                tooltip.style.opacity = '1';
            });

            cell.addEventListener('mouseleave', () => {
                this.clearColumnHighlight();
                tooltip.style.opacity = '0';
            });
        });
    }
}

window.MsaViewer = MsaViewer;
