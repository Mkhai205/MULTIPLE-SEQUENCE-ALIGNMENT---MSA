import os
import sys
import re
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

# Determine project paths
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
BUILD_DIR = BASE_DIR / "build" / "Release"
EXE_PATH = BUILD_DIR / "msa_align.exe"
DATA_DIR = BASE_DIR / "data"

app = FastAPI(
    title="Multiple Sequence Alignment (MSA) C++17 Pipeline API",
    description="High-Performance Progressive Multiple Sequence Alignment with OpenMP Concurrency",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Data Models
# -----------------------------------------------------------------------------
class AlignRequest(BaseModel):
    raw_content: Optional[str] = Field(None, description="Raw FASTA or MSF string")
    preset_id: Optional[str] = Field(None, description="Preset identifier")
    filename: Optional[str] = Field("input.fa", description="Filename hint for format detection")
    threads: int = Field(1, ge=1, le=16, description="Number of OpenMP worker threads")
    gap_open: int = Field(-10, description="Affine gap open penalty (negative)")
    gap_extend: int = Field(-1, description="Affine gap extension penalty (negative)")
    mode: str = Field("standard", description="'standard', 'baseline', or 'benchmark'")
    export_tree: bool = Field(True, description="Whether to export UPGMA guide tree")

class PresetInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    filename: str
    format: str

# -----------------------------------------------------------------------------
# Presets Configuration
# -----------------------------------------------------------------------------
PRESETS_MAP: Dict[str, Dict[str, Any]] = {
    "rv11": {
        "id": "rv11",
        "name": "BAliBASE RV11 (BB11001)",
        "description": "Equidistant divergent sequences (<20% identity). Classic benchmark case.",
        "category": "BAliBASE Benchmark",
        "path": DATA_DIR / "balibase" / "BB11001.msf",
        "filename": "BB11001.msf",
        "format": "msf"
    },
    "rv12": {
        "id": "rv12",
        "name": "BAliBASE RV12 (BB12001)",
        "description": "Medium divergent sequences (20-40% identity) with variable gap insertions.",
        "category": "BAliBASE Benchmark",
        "path": DATA_DIR / "balibase" / "BB12001.msf",
        "filename": "BB12001.msf",
        "format": "msf"
    },
    "hemoglobin": {
        "id": "hemoglobin",
        "name": "Hemoglobin Family",
        "description": "Authentic globin chains (Alpha, Beta, Myoglobin from Human, Chimpanzee, Horse).",
        "category": "Biological Protein Family",
        "path": DATA_DIR / "presets" / "hemoglobin.fa",
        "filename": "hemoglobin.fa",
        "format": "fasta"
    },
    "long_seq": {
        "id": "long_seq",
        "name": "Long-Sequence Memory Test",
        "description": "Multidomain proteins (~900 aa). Demonstrates Gotoh O(mn) vs Myers-Miller O(min(m,n)) ~1,350x memory reduction.",
        "category": "High-Scalability Stress Test",
        "path": DATA_DIR / "presets" / "long_sequence.fa",
        "filename": "long_sequence.fa",
        "format": "fasta"
    },
    "large_20": {
        "id": "large_20",
        "name": "Bacterial 20-Seq Benchmark",
        "description": "20 homologous bacterial protein sequences (~450 aa) from eggNOG. Ideal for multi-thread OpenMP benchmark.",
        "category": "Scalability & OpenMP Benchmark",
        "path": DATA_DIR / "presets" / "benchmark_20seqs.fa",
        "filename": "benchmark_20seqs.fa",
        "format": "fasta"
    },
    "large_40": {
        "id": "large_40",
        "name": "Bacterial 40-Seq Benchmark",
        "description": "40 homologous bacterial protein sequences (~450 aa) from eggNOG. 780 pairwise alignments demonstrating strong multi-core scalability.",
        "category": "Scalability & OpenMP Benchmark",
        "path": DATA_DIR / "presets" / "benchmark_40seqs.fa",
        "filename": "benchmark_40seqs.fa",
        "format": "fasta"
    }
}

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def parse_aligned_fasta(fasta_str: str) -> List[Dict[str, str]]:
    sequences = []
    current_id = None
    current_desc = ""
    current_seq_parts = []

    for line in fasta_str.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_id is not None:
                sequences.append({
                    "id": current_id,
                    "description": current_desc,
                    "sequence": "".join(current_seq_parts)
                })
            header = line[1:].strip()
            parts = header.split(maxsplit=1)
            current_id = parts[0]
            current_desc = parts[1] if len(parts) > 1 else ""
            current_seq_parts = []
        else:
            current_seq_parts.append(line)

    if current_id is not None:
        sequences.append({
            "id": current_id,
            "description": current_desc,
            "sequence": "".join(current_seq_parts)
        })

    return sequences

def parse_baseline_output(stdout: str) -> Optional[Dict[str, Any]]:
    """Extract Gotoh vs Myers-Miller comparison from stdout."""
    res = {}
    m_pair = re.search(r"Pair:\s+([^\n\r]+)", stdout)
    if m_pair:
        res["pair"] = m_pair.group(1).strip()

    m_gotoh = re.search(r"Gotoh NW Score:\s+(-?\d+)\s+\(Time:\s+([\d.]+)\s+ms,\s+Peak Mem:\s+(\d+)\s+B\)", stdout)
    if m_gotoh:
        res["gotoh"] = {
            "score": int(m_gotoh.group(1)),
            "time_ms": float(m_gotoh.group(2)),
            "peak_memory_bytes": int(m_gotoh.group(3))
        }

    m_hb = re.search(r"Myers-Miller Score:\s+(-?\d+)\s+\(Time:\s+([\d.]+)\s+ms,\s+Peak Mem:\s+(\d+)\s+B\)", stdout)
    if m_hb:
        res["myers_miller"] = {
            "score": int(m_hb.group(1)),
            "time_ms": float(m_hb.group(2)),
            "peak_memory_bytes": int(m_hb.group(3))
        }

    m_match = re.search(r"Score Identity:\s+([^\n\r]+)", stdout)
    if m_match:
        res["score_identity"] = "MATCH" in m_match.group(1)

    m_red = re.search(r"Memory Reduction:\s+([\d.]+)x less memory", stdout)
    if m_red:
        res["memory_reduction_ratio"] = float(m_red.group(1))

    return res if ("gotoh" in res and "myers_miller" in res) else None

def parse_metrics_output(stdout: str) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {}
    
    m_seqs = re.search(r"Number of sequences:\s+(\d+)", stdout)
    if m_seqs:
        metrics["num_sequences"] = int(m_seqs.group(1))

    m_len = re.search(r"Alignment length:\s+(\d+)\s+columns", stdout)
    if m_len:
        metrics["alignment_length"] = int(m_len.group(1))

    m_time = re.search(r"Execution time:\s+([\d.]+)\s+ms", stdout)
    if m_time:
        metrics["execution_time_ms"] = float(m_time.group(1))

    m_mem = re.search(r"Peak Working Set:\s+([\d.]+)\s+MB", stdout)
    if m_mem:
        metrics["peak_memory_mb"] = float(m_mem.group(1))

    m_sp = re.search(r"BAliBASE SP Score:\s+([\d.]+)\s+\((\d+)\s+/\s+(\d+)\s+pairs\)", stdout)
    if m_sp:
        metrics["sp_score"] = float(m_sp.group(1))
        metrics["sp_correct_pairs"] = int(m_sp.group(2))
        metrics["sp_total_pairs"] = int(m_sp.group(3))

    m_tc = re.search(r"BAliBASE TC Score:\s+([\d.]+)\s+\((\d+)\s+/\s+(\d+)\s+columns\)", stdout)
    if m_tc:
        metrics["tc_score"] = float(m_tc.group(1))
        metrics["tc_correct_columns"] = int(m_tc.group(2))
        metrics["tc_total_columns"] = int(m_tc.group(3))

    return metrics

# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------
@app.get("/api/health")
def get_health():
    exe_exists = EXE_PATH.exists()
    return {
        "status": "healthy" if exe_exists else "degraded",
        "executable_found": exe_exists,
        "executable_path": str(EXE_PATH),
        "python_version": sys.version,
        "platform": sys.platform,
        "version": "1.0.0"
    }

@app.get("/api/presets")
def get_presets():
    result = []
    for p_id, p_info in PRESETS_MAP.items():
        exists = p_info["path"].exists()
        result.append({
            "id": p_info["id"],
            "name": p_info["name"],
            "description": p_info["description"],
            "category": p_info["category"],
            "filename": p_info["filename"],
            "format": p_info["format"],
            "available": exists
        })
    return result

@app.get("/api/preset/{preset_id}")
def get_preset_content(preset_id: str):
    if preset_id not in PRESETS_MAP:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found.")
    p_info = PRESETS_MAP[preset_id]
    if not p_info["path"].exists():
        raise HTTPException(status_code=404, detail=f"Preset file '{p_info['path']}' does not exist.")
    
    with open(p_info["path"], "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    return {
        "id": p_info["id"],
        "name": p_info["name"],
        "filename": p_info["filename"],
        "format": p_info["format"],
        "content": content
    }

@app.post("/api/align")
def run_alignment(req: AlignRequest):
    if not EXE_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"C++ binary msa_align.exe not found at '{EXE_PATH}'. Please compile the project first."
        )

    # 1. Prepare input content
    content_to_align = ""
    target_ext = ".fa"
    
    if req.preset_id and req.preset_id in PRESETS_MAP:
        p_info = PRESETS_MAP[req.preset_id]
        if not p_info["path"].exists():
            raise HTTPException(status_code=404, detail=f"Preset file for '{req.preset_id}' not found.")
        with open(p_info["path"], "r", encoding="utf-8", errors="replace") as f:
            content_to_align = f.read()
        target_ext = p_info["path"].suffix.lower()
    elif req.raw_content and req.raw_content.strip():
        content_to_align = req.raw_content.strip()
        # Auto-detect MSF
        if "PileUp" in content_to_align or "MSF:" in content_to_align or (req.filename and req.filename.endswith(".msf")):
            target_ext = ".msf"
        else:
            target_ext = ".fa"
    else:
        raise HTTPException(status_code=400, detail="No input protein sequence content or preset selected.")

    # Normalize gap penalties (must be negative)
    gap_open = -abs(req.gap_open)
    gap_extend = -abs(req.gap_extend)
    threads = max(1, min(16, req.threads))

    # 2. Run in a temporary directory
    with tempfile.TemporaryDirectory(prefix="msa_gui_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        in_file = tmp_path / f"input{target_ext}"
        out_aln_file = tmp_path / "aligned.fa"
        tree_prefix = tmp_path / "guide_tree"
        bench_json_file = tmp_path / "benchmark.json"

        with open(in_file, "w", encoding="utf-8") as f:
            f.write(content_to_align)

        response_data: Dict[str, Any] = {
            "success": False,
            "mode": req.mode,
            "threads": threads,
            "gap_open": gap_open,
            "gap_extend": gap_extend,
            "stdout": "",
            "stderr": "",
            "aligned_fasta": "",
            "aligned_sequences": [],
            "tree": None,
            "tree_newick": "",
            "metrics": {},
            "baseline_comparison": None,
            "benchmark_data": None
        }

        try:
            # Mode A: Benchmark mode
            if req.mode == "benchmark":
                cmd_bench = [
                    str(EXE_PATH),
                    "-i", str(in_file),
                    "-o", str(bench_json_file),
                    "--benchmark",
                    "--gap-open", str(gap_open),
                    "--gap-extend", str(gap_extend)
                ]
                proc_bench = subprocess.run(
                    cmd_bench,
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                response_data["stdout"] += proc_bench.stdout
                response_data["stderr"] += proc_bench.stderr

                if proc_bench.returncode != 0:
                    err = proc_bench.stderr.strip() or proc_bench.stdout.strip() or "Benchmark process failed"
                    raise HTTPException(status_code=400, detail=f"Benchmark error: {err}")

                if bench_json_file.exists():
                    try:
                        with open(bench_json_file, "r", encoding="utf-8") as f:
                            response_data["benchmark_data"] = json.load(f)
                    except Exception as e:
                        response_data["stderr"] += f"\nFailed to parse benchmark JSON: {e}"

                # In benchmark mode, also execute alignment with baseline comparison to get matrix, tree, and Gotoh vs Myers-Miller memory analysis
                cmd_align = [
                    str(EXE_PATH),
                    "-i", str(in_file),
                    "-o", str(out_aln_file),
                    "--baseline-compare",
                    "--export-tree", str(tree_prefix.with_suffix(".json")),
                    "-t", str(threads),
                    "--gap-open", str(gap_open),
                    "--gap-extend", str(gap_extend)
                ]
                proc_align = subprocess.run(
                    cmd_align,
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                response_data["stdout"] += "\n" + proc_align.stdout
                if proc_align.stderr:
                    response_data["stderr"] += "\n" + proc_align.stderr

                if proc_align.returncode != 0:
                    err = proc_align.stderr.strip() or proc_align.stdout.strip() or "Alignment process failed"
                    raise HTTPException(status_code=400, detail=f"Alignment error: {err}")

                response_data["baseline_comparison"] = parse_baseline_output(proc_align.stdout)

            # Mode B: Baseline Comparison mode
            elif req.mode == "baseline":
                cmd = [
                    str(EXE_PATH),
                    "-i", str(in_file),
                    "-o", str(out_aln_file),
                    "--baseline-compare",
                    "--export-tree", str(tree_prefix.with_suffix(".json")),
                    "-t", str(threads),
                    "--gap-open", str(gap_open),
                    "--gap-extend", str(gap_extend)
                ]
                proc = subprocess.run(
                    cmd,
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                response_data["stdout"] = proc.stdout
                response_data["stderr"] = proc.stderr
                if proc.returncode != 0:
                    err = proc.stderr.strip() or proc.stdout.strip() or "Baseline comparison process failed"
                    raise HTTPException(status_code=400, detail=f"Baseline error: {err}")
                response_data["baseline_comparison"] = parse_baseline_output(proc.stdout)

            # Mode C: Standard alignment
            else:
                cmd = [
                    str(EXE_PATH),
                    "-i", str(in_file),
                    "-o", str(out_aln_file),
                    "--export-tree", str(tree_prefix.with_suffix(".json")),
                    "-t", str(threads),
                    "--gap-open", str(gap_open),
                    "--gap-extend", str(gap_extend)
                ]
                proc = subprocess.run(
                    cmd,
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                response_data["stdout"] = proc.stdout
                response_data["stderr"] = proc.stderr
                if proc.returncode != 0:
                    err = proc.stderr.strip() or proc.stdout.strip() or "Alignment process failed"
                    raise HTTPException(status_code=400, detail=f"Alignment error: {err}")

            # Parse common metrics from stdout
            response_data["metrics"] = parse_metrics_output(response_data["stdout"])

            # Read aligned FASTA output
            if out_aln_file.exists():
                with open(out_aln_file, "r", encoding="utf-8") as f:
                    aln_str = f.read()
                response_data["aligned_fasta"] = aln_str
                response_data["aligned_sequences"] = parse_aligned_fasta(aln_str)

            if not response_data["aligned_sequences"]:
                raise HTTPException(status_code=400, detail="Alignment output contains no valid aligned sequences.")

            # Read Guide Tree outputs (.json and .nwk)
            json_tree_path = tree_prefix.with_suffix(".json")
            nwk_tree_path = tree_prefix.with_suffix(".nwk")

            if json_tree_path.exists():
                try:
                    with open(json_tree_path, "r", encoding="utf-8") as f:
                        response_data["tree"] = json.load(f)
                except Exception as e:
                    response_data["stderr"] += f"\nFailed to parse tree JSON: {e}"

            if nwk_tree_path.exists():
                try:
                    with open(nwk_tree_path, "r", encoding="utf-8") as f:
                        response_data["tree_newick"] = f.read().strip()
                except Exception as e:
                    response_data["stderr"] += f"\nFailed to read tree NWK: {e}"

            response_data["success"] = True
            return response_data

        except HTTPException:
            raise
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=504, detail="Execution timed out after 60 seconds.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Alignment execution failed: {str(e)}")

# Mount static frontend
STATIC_DIR = BASE_DIR / "web" / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    uvicorn.run(app, host="127.0.0.1", port=8000)
