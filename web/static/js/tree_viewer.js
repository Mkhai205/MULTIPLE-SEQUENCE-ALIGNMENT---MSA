/**
 * Interactive UPGMA Guide Tree Visualizer (Dendrogram / Phylogram)
 */
class GuideTreeViewer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.treeData = null;
        this.rawNewick = '';
        this.showBranchLabels = true;
        this.zoomTransform = { x: 40, y: 30, k: 1.0 };
        this.isPanning = false;
        this.startPan = { x: 0, y: 0 };

        this.init();
    }

    init() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div class="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl relative">
                <!-- Toolbar -->
                <div class="flex items-center justify-between px-4 py-2 bg-slate-800/80 border-b border-slate-700/60 text-xs text-slate-300">
                    <div class="flex items-center gap-3">
                        <span class="font-semibold text-slate-200 flex items-center gap-1.5">
                            <i class="fa-solid fa-network-wired text-cyan-400"></i> UPGMA Guide Tree
                        </span>
                        <span id="tree-info-badge" class="px-2 py-0.5 rounded bg-slate-700 text-slate-300 font-mono text-[11px]">No tree loaded</span>
                    </div>

                    <div class="flex items-center gap-2">
                        <!-- Toggle Branch Lengths -->
                        <button id="tree-toggle-branches" class="px-2.5 py-1 rounded bg-slate-700/80 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1 border border-slate-600 transition-colors">
                            <i class="fa-solid fa-ruler-horizontal text-xs"></i> Branch Lengths
                        </button>

                        <!-- Zoom / Pan Controls -->
                        <div class="flex items-center bg-slate-950/60 rounded border border-slate-700 p-0.5">
                            <button id="tree-zoom-in" title="Zoom In" class="px-2 py-0.5 text-slate-300 hover:text-white hover:bg-slate-800 rounded transition-colors"><i class="fa-solid fa-plus text-xs"></i></button>
                            <button id="tree-zoom-out" title="Zoom Out" class="px-2 py-0.5 text-slate-300 hover:text-white hover:bg-slate-800 rounded transition-colors"><i class="fa-solid fa-minus text-xs"></i></button>
                            <button id="tree-zoom-reset" title="Reset View" class="px-2 py-0.5 text-slate-300 hover:text-white hover:bg-slate-800 rounded transition-colors"><i class="fa-solid fa-arrows-rotate text-xs"></i></button>
                        </div>

                        <!-- Export Buttons -->
                        <button id="tree-export-svg" title="Export SVG Image" class="px-2.5 py-1 rounded bg-blue-600/80 hover:bg-blue-600 text-white text-xs flex items-center gap-1 transition-colors">
                            <i class="fa-solid fa-file-image"></i> SVG
                        </button>
                        <button id="tree-export-nwk" title="Download Newick Format" class="px-2.5 py-1 rounded bg-emerald-600/80 hover:bg-emerald-600 text-white text-xs flex items-center gap-1 transition-colors">
                            <i class="fa-solid fa-file-code"></i> NWK
                        </button>
                    </div>
                </div>

                <!-- Tree SVG Canvas Viewport -->
                <div id="tree-viewport" class="flex-1 w-full h-[400px] min-h-[350px] relative overflow-hidden bg-slate-950 cursor-grab active:cursor-grabbing">
                    <svg id="tree-svg" class="w-full h-full block">
                        <g id="tree-canvas-group"></g>
                    </svg>
                </div>
            </div>

            <!-- Tree Tooltip -->
            <div id="tree-tooltip" class="tooltip-custom bg-slate-800 border border-slate-700 text-slate-200 text-xs px-3 py-2 rounded-lg shadow-2xl pointer-events-none"></div>
        `;

        this.bindEvents();
    }

    bindEvents() {
        document.getElementById('tree-toggle-branches')?.addEventListener('click', () => {
            this.showBranchLabels = !this.showBranchLabels;
            this.render();
        });

        document.getElementById('tree-zoom-in')?.addEventListener('click', () => {
            this.zoomTransform.k = Math.min(3.0, this.zoomTransform.k * 1.25);
            this.applyTransform();
        });

        document.getElementById('tree-zoom-out')?.addEventListener('click', () => {
            this.zoomTransform.k = Math.max(0.3, this.zoomTransform.k / 1.25);
            this.applyTransform();
        });

        document.getElementById('tree-zoom-reset')?.addEventListener('click', () => {
            this.fitToScreen();
        });

        document.getElementById('tree-export-nwk')?.addEventListener('click', () => {
            this.downloadNewick();
        });

        document.getElementById('tree-export-svg')?.addEventListener('click', () => {
            this.downloadSvg();
        });

        // Mouse Pan & Wheel Zoom
        const viewport = document.getElementById('tree-viewport');
        if (viewport) {
            viewport.addEventListener('mousedown', (e) => {
                if (e.button !== 0) return;
                this.isPanning = true;
                this.startPan = { x: e.clientX - this.zoomTransform.x, y: e.clientY - this.zoomTransform.y };
            });

            window.addEventListener('mousemove', (e) => {
                if (!this.isPanning) return;
                this.zoomTransform.x = e.clientX - this.startPan.x;
                this.zoomTransform.y = e.clientY - this.startPan.y;
                this.applyTransform();
            });

            window.addEventListener('mouseup', () => {
                this.isPanning = false;
            });

            viewport.addEventListener('wheel', (e) => {
                e.preventDefault();
                const factor = e.deltaY < 0 ? 1.1 : 0.9;
                this.zoomTransform.k = Math.max(0.3, Math.min(4.0, this.zoomTransform.k * factor));
                this.applyTransform();
            }, { passive: false });
        }
    }

    loadTree(treeJson, newickStr = '') {
        this.treeData = treeJson;
        this.rawNewick = newickStr;

        if (!this.treeData) {
            this.clear();
            return;
        }

        const badge = document.getElementById('tree-info-badge');
        if (badge) {
            badge.textContent = `${this.treeData.clade_size || 0} Taxa (Leaves)`;
        }

        this.fitToScreen();
        this.render();
    }

    clear() {
        this.treeData = null;
        this.rawNewick = '';
        this.contentBounds = null;
        const badge = document.getElementById('tree-info-badge');
        if (badge) badge.textContent = `No tree loaded`;
        const group = document.getElementById('tree-canvas-group');
        if (group) group.innerHTML = '';
    }

    fitToScreen() {
        const viewport = document.getElementById('tree-viewport');
        const vpW = viewport && viewport.clientWidth > 0 ? viewport.clientWidth : 700;
        const vpH = viewport && viewport.clientHeight > 0 ? viewport.clientHeight : 450;

        const treeW = this.contentBounds ? this.contentBounds.width : 600;
        const treeH = this.contentBounds ? this.contentBounds.height : 250;

        const scaleX = (vpW - 80) / Math.max(100, treeW);
        const scaleY = (vpH - 80) / Math.max(100, treeH);
        const k = Math.min(1.25, Math.max(0.3, Math.min(scaleX, scaleY)));

        this.zoomTransform = {
            x: 40,
            y: Math.max(25, (vpH - treeH * k) / 2),
            k: k
        };
        this.applyTransform();
    }

    applyTransform() {
        const group = document.getElementById('tree-canvas-group');
        if (group) {
            group.setAttribute('transform', `translate(${this.zoomTransform.x}, ${this.zoomTransform.y}) scale(${this.zoomTransform.k})`);
        }
    }

    render() {
        if (!this.treeData) return;

        const group = document.getElementById('tree-canvas-group');
        if (!group) return;
        group.innerHTML = '';

        // Layout the tree in ultrametric rectangular dendrogram coordinates
        const leafSpacing = 48;
        let currentLeafIndex = 0;
        const rootHeight = Math.max(0.0, this.treeData.height || 0.0);
        const totalWidth = 500; // Available horizontal layout width for branches

        // Scale factor: tree height -> pixels
        const scaleX = rootHeight > 0.0001 ? (totalWidth / rootHeight) : 200;

        // Recursive traversal to compute node coordinates (x, y)
        // Root is at x = 0 (or leftmost). In UPGMA, leaves have height = 0, root has max height.
        let maxNodeX = 0;
        const computeCoords = (node, depth = 0) => {
            if (rootHeight > 0.0001) {
                node.x = (rootHeight - (node.height || 0.0)) * scaleX;
            } else {
                // If all heights are zero (e.g. identical sequences), lay out by depth
                node.x = node.is_leaf ? 200 : (depth * 80);
            }
            maxNodeX = Math.max(maxNodeX, node.x);

            if (node.is_leaf || !node.children || node.children.length === 0) {
                node.y = currentLeafIndex * leafSpacing;
                currentLeafIndex++;
            } else {
                node.children.forEach(child => computeCoords(child, depth + 1));
                // Internal node y is vertical midpoint of children
                const ySum = node.children.reduce((acc, c) => acc + c.y, 0);
                node.y = ySum / node.children.length;
            }
        };

        computeCoords(this.treeData);

        const totalTreeHeight = Math.max(80, (currentLeafIndex - 1) * leafSpacing);
        this.contentBounds = {
            width: maxNodeX + 220,
            height: totalTreeHeight + 40
        };

        // Render branches (links) and nodes
        let linksHtml = '';
        let nodesHtml = '';
        let labelsHtml = '';

        const renderSubtree = (node) => {
            if (node.children && node.children.length > 0) {
                const childYs = node.children.map(c => c.y);
                const minY = Math.min(...childYs);
                const maxY = Math.max(...childYs);

                // Vertical bracket link at node.x connecting minY to maxY
                linksHtml += `
                    <line class="tree-link" x1="${node.x}" y1="${minY}" x2="${node.x}" y2="${maxY}" stroke="#475569" stroke-width="2"/>
                `;

                // Horizontal links from node.x to child.x at child.y
                node.children.forEach(child => {
                    linksHtml += `
                        <line class="tree-link" x1="${node.x}" y1="${child.y}" x2="${child.x}" y2="${child.y}" stroke="#475569" stroke-width="2"/>
                    `;

                    // Branch length label
                    if (this.showBranchLabels && child.branch_length !== undefined) {
                        const midX = (node.x + child.x) / 2;
                        labelsHtml += `
                            <text class="tree-branch-label" x="${midX}" y="${child.y - 4}" text-anchor="middle">
                                ${child.branch_length.toFixed(4)}
                            </text>
                        `;
                    }

                    renderSubtree(child);
                });
            }

            // Node marker and label
            if (node.is_leaf) {
                // Leaf Node: sequence ID
                nodesHtml += `
                    <g class="tree-node cursor-pointer" data-id="${node.id}" data-name="${node.name}" data-height="${node.height || 0}">
                        <circle cx="${node.x}" cy="${node.y}" r="4.5" fill="#38bdf8" stroke="#0284c7" stroke-width="1.5"/>
                        <text x="${node.x + 12}" y="${node.y + 4}" font-family="JetBrains Mono, monospace" font-size="12" font-weight="600" fill="#f8fafc">
                            ${node.name}
                        </text>
                    </g>
                `;
            } else {
                // Internal Node: clade marker
                nodesHtml += `
                    <g class="tree-node cursor-pointer" data-id="${node.id}" data-name="${node.name}" data-height="${node.height}" data-clade="${node.clade_size}">
                        <circle cx="${node.x}" cy="${node.y}" r="3.5" fill="#64748b" stroke="#334155" stroke-width="1.5"/>
                    </g>
                `;
            }
        };

        renderSubtree(this.treeData);

        group.innerHTML = linksHtml + labelsHtml + nodesHtml;
        this.setupNodeTooltips();
        this.applyTransform();
    }

    setupNodeTooltips() {
        const tooltip = document.getElementById('tree-tooltip');
        if (!tooltip) return;

        const nodes = this.container.querySelectorAll('.tree-node');
        nodes.forEach(node => {
            node.addEventListener('mouseenter', (e) => {
                const name = node.dataset.name;
                const height = parseFloat(node.dataset.height || '0').toFixed(4);
                const clade = node.dataset.clade;

                tooltip.innerHTML = `
                    <div class="font-bold text-cyan-300">${name}</div>
                    <div class="text-[11px] text-slate-300">Height: <span class="font-mono text-white">${height}</span></div>
                    ${clade ? `<div class="text-[11px] text-slate-400">Leaves in Clade: <span class="font-mono text-white">${clade}</span></div>` : ''}
                `;

                const rect = node.getBoundingClientRect();
                tooltip.style.left = `${rect.left + window.scrollX + 15}px`;
                tooltip.style.top = `${rect.top + window.scrollY - 30}px`;
                tooltip.style.opacity = '1';
            });

            node.addEventListener('mouseleave', () => {
                tooltip.style.opacity = '0';
            });
        });
    }

    downloadNewick() {
        if (!this.rawNewick) {
            if (window.showAppToast) window.showAppToast('No Newick tree data available.', true);
            return;
        }
        const blob = new Blob([this.rawNewick], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'msa_guide_tree.nwk';
        a.click();
        URL.revokeObjectURL(url);
    }

    downloadSvg() {
        const group = document.getElementById('tree-canvas-group');
        if (!group || !this.treeData) {
            if (window.showAppToast) window.showAppToast('No guide tree to export as SVG.', true);
            return;
        }

        const treeW = this.contentBounds ? Math.ceil(this.contentBounds.width) : 700;
        const treeH = this.contentBounds ? Math.ceil(this.contentBounds.height) : 400;
        const padX = 40;
        const padY = 30;
        const svgW = treeW + padX * 2;
        const svgH = treeH + padY * 2;

        const innerContent = group.innerHTML;

        const fullSvg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}">
  <style>
    .tree-node circle { fill: #38bdf8; stroke: #0284c7; stroke-width: 1.5px; }
    .tree-node text { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 12px; font-weight: 600; fill: #f8fafc; }
    .tree-link { fill: none; stroke: #475569; stroke-width: 2px; }
    .tree-branch-label { font-family: 'JetBrains Mono', Consolas, monospace; font-size: 9px; fill: #94a3b8; }
  </style>
  <rect width="100%" height="100%" fill="#070d18"/>
  <g transform="translate(${padX}, ${padY})">
    ${innerContent}
  </g>
</svg>`;

        const blob = new Blob([fullSvg], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'msa_guide_tree.svg';
        a.click();
        URL.revokeObjectURL(url);
    }
}

window.GuideTreeViewer = GuideTreeViewer;
