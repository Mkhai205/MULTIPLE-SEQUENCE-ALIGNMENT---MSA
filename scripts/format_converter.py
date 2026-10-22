#!/usr/bin/env python3
"""
Format Converter for Multiple Sequence Alignment (MSA)
Group 5 - Algorithm Analysis and Design

Converts biological sequence alignments between standard formats:
  - FASTA (Aligned / Unaligned)
  - MSF (GCG / BAliBASE 3.0 benchmark format)
  - ClustalW / ALN (European Bioinformatics Institute format)

Features:
  - Extract unaligned raw sequences from reference alignments (stripping gaps).
  - Convert aligned FASTA to Clustal format with conservation consensus symbols (*, :, .).
  - Batch conversion of BAliBASE MSF suites to unaligned FASTA.
"""

import sys
import os
import argparse
from typing import List, Tuple, Dict, Optional

def read_fasta(file_path: str) -> List[Tuple[str, str]]:
    """Reads a FASTA file and returns list of (id, sequence)."""
    sequences = []
    current_id = ""
    current_seq = []
    
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current_id:
                    sequences.append((current_id, "".join(current_seq)))
                    current_seq = []
                current_id = line[1:].split()[0]
            else:
                current_seq.append(line.replace(" ", "").upper())
        if current_id:
            sequences.append((current_id, "".join(current_seq)))
    return sequences

def read_msf(file_path: str) -> List[Tuple[str, str]]:
    """Reads an MSF file (BAliBASE 3.0 format) and returns list of (id, aligned_sequence)."""
    names = []
    seq_map: Dict[str, List[str]] = {}
    in_data = False
    
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line_str = line.strip()
            if not in_data:
                if line_str.startswith("//"):
                    in_data = True
                    for name in names:
                        seq_map[name] = []
                elif "Name:" in line_str:
                    parts = line_str.split()
                    try:
                        idx = parts.index("Name:")
                        name = parts[idx + 1]
                        if name not in names:
                            names.append(name)
                    except (ValueError, IndexError):
                        pass
            else:
                if not line_str:
                    continue
                parts = line_str.split()
                if len(parts) >= 2:
                    name = parts[0]
                    if name in seq_map:
                        seq_chunk = "".join(parts[1:]).replace(" ", "")
                        seq_map[name].append(seq_chunk)
                        
    return [(name, "".join(seq_map[name])) for name in names if name in seq_map]

def read_clustal(file_path: str) -> List[Tuple[str, str]]:
    """Reads a Clustal alignment (.aln) file and returns list of (id, sequence)."""
    seq_map: Dict[str, List[str]] = {}
    names = []
    
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        first_line = True
        for line in f:
            line_clean = line.rstrip()
            if first_line:
                first_line = False
                continue  # skip CLUSTAL header
            if not line_clean.strip():
                continue
            if line_clean.startswith(" ") or line_clean.startswith("\t"):
                continue  # consensus conservation line (*, :, .)
            
            parts = line_clean.split()
            if len(parts) >= 2:
                name = parts[0]
                seq_chunk = parts[1].replace(" ", "")
                if name not in seq_map:
                    names.append(name)
                    seq_map[name] = []
                seq_map[name].append(seq_chunk)
                
    return [(name, "".join(seq_map[name])) for name in names]

def write_fasta(sequences: List[Tuple[str, str]], out_path: str, ungap: bool = False, wrap: int = 60) -> None:
    """Writes sequences to FASTA format."""
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for seq_id, seq in sequences:
            f.write(f">{seq_id}\n")
            out_seq = seq
            if ungap:
                out_seq = "".join(c for c in seq if c not in "-.~ \t\r\n")
            for i in range(0, len(out_seq), wrap):
                f.write(out_seq[i:i+wrap] + "\n")

def compute_clustal_consensus(sequences: List[Tuple[str, str]]) -> str:
    """Computes standard Clustal conservation line (* for 100% match, : for strong group, . for weak)."""
    if not sequences:
        return ""
    length = len(sequences[0][1])
    num_seqs = len(sequences)
    
    # Strong groups in ClustalW
    strong_groups = [
        {"S", "T", "A"}, {"N", "E", "Q", "K"}, {"N", "H", "Q", "K"},
        {"N", "D", "E", "Q"}, {"Q", "H", "R", "K"}, {"M", "I", "L", "V"},
        {"M", "I", "L", "F"}, {"H", "Y"}, {"F", "Y", "W"}
    ]
    # Weak groups
    weak_groups = [
        {"C", "S", "A"}, {"A", "T", "V"}, {"S", "A", "G"}, {"S", "T", "N", "K"},
        {"S", "T", "P", "A"}, {"S", "G", "N", "D"}, {"S", "N", "D", "E", "Q", "K"},
        {"N", "D", "E", "Q", "H", "K"}, {"N", "E", "Q", "H", "R", "K"},
        {"F", "V", "L", "I", "M"}, {"H", "F", "Y"}
    ]
    
    symbols = []
    for c in range(length):
        col_chars = [sequences[i][1][c].upper() for i in range(num_seqs)]
        if any(ch in "-.~" for ch in col_chars):
            symbols.append(" ")
            continue
        first_ch = col_chars[0]
        if all(ch == first_ch for ch in col_chars):
            symbols.append("*")
        elif any(set(col_chars).issubset(grp) for grp in strong_groups):
            symbols.append(":")
        elif any(set(col_chars).issubset(grp) for grp in weak_groups):
            symbols.append(".")
        else:
            symbols.append(" ")
            
    return "".join(symbols)

def write_clustal(sequences: List[Tuple[str, str]], out_path: str, block_size: int = 60) -> None:
    """Writes sequences to standard Clustal format (.aln / .clustal)."""
    if not sequences:
        return
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    length = len(sequences[0][1])
    consensus = compute_clustal_consensus(sequences)
    max_id_len = max(len(seq_id) for seq_id, _ in sequences)
    id_col_width = max(max_id_len + 4, 16)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("CLUSTAL W (1.83) multiple sequence alignment\n\n\n")
        
        for start in range(0, length, block_size):
            end = min(start + block_size, length)
            for seq_id, seq in sequences:
                f.write(f"{seq_id.ljust(id_col_width)}{seq[start:end]}\n")
            # Write consensus line
            cons_block = consensus[start:end]
            f.write(f"{''.ljust(id_col_width)}{cons_block}\n\n")

def write_msf(sequences: List[Tuple[str, str]], out_path: str, block_size: int = 50) -> None:
    """Writes sequences to GCG / MSF format."""
    if not sequences:
        return
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    length = len(sequences[0][1])
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(" PileUp\n\n")
        f.write(f"   MSF:  {length}  Type: P    Check:  5432   ..\n\n")
        for seq_id, seq in sequences:
            f.write(f" Name: {seq_id.ljust(15)} Len:    {len(seq)}  Check:   1234  Weight:  1.00\n")
        f.write("\n//\n\n")
        
        for start in range(0, length, block_size):
            end = min(start + block_size, length)
            for seq_id, seq in sequences:
                chunk = seq[start:end].lower()
                # Split chunk into 10-char space-separated blocks
                sub_blocks = [chunk[j:j+10] for j in range(0, len(chunk), 10)]
                f.write(f"{seq_id.ljust(12)} {' '.join(sub_blocks)}\n")
            f.write("\n")

def detect_and_read(file_path: str) -> List[Tuple[str, str]]:
    """Detects format by content and reads sequences."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(512)
    if content.strip().startswith(">"):
        return read_fasta(file_path)
    if "PileUp" in content or "MSF:" in content or "//" in content:
        return read_msf(file_path)
    if content.startswith("CLUSTAL") or content.startswith("MUSCLE"):
        return read_clustal(file_path)
    # Default fallback
    return read_fasta(file_path)

def main():
    parser = argparse.ArgumentParser(
        description="Format Converter for Biological Sequence Alignments (FASTA / MSF / Clustal)"
    )
    parser.add_argument("-i", "--input", help="Path to input alignment file")
    parser.add_argument("-o", "--output", help="Path to output file")
    parser.add_argument("--to", choices=["fasta", "unaligned_fasta", "clustal", "msf"], default="fasta",
                        help="Target format (default: fasta)")
    parser.add_argument("--batch-unalign", nargs=2, metavar=("MSF_DIR", "OUT_DIR"),
                        help="Batch convert all MSF files in a directory to unaligned FASTA files")
    
    args = parser.parse_args()
    
    if args.batch_unalign:
        msf_dir, out_dir = args.batch_unalign
        os.makedirs(out_dir, exist_ok=True)
        count = 0
        for fname in os.listdir(msf_dir):
            if fname.lower().endswith(".msf"):
                in_path = os.path.join(msf_dir, fname)
                base = os.path.splitext(fname)[0]
                out_path = os.path.join(out_dir, f"{base}.fa")
                seqs = read_msf(in_path)
                if seqs:
                    write_fasta(seqs, out_path, ungap=True)
                    print(f"Extracted {len(seqs)} unaligned sequences: {fname} -> {base}.fa")
                    count += 1
        print(f"[SUCCESS] Batch unaligned conversion completed: {count} files converted to {out_dir}")
        return

    if not args.input or not args.output:
        parser.print_help()
        sys.exit(1)
        
    seqs = detect_and_read(args.input)
    if not seqs:
        print(f"[ERROR] No sequences found in {args.input}", file=sys.stderr)
        sys.exit(1)
        
    if args.to == "fasta":
        write_fasta(seqs, args.output, ungap=False)
    elif args.to == "unaligned_fasta":
        write_fasta(seqs, args.output, ungap=True)
    elif args.to == "clustal":
        write_clustal(seqs, args.output)
    elif args.to == "msf":
        write_msf(seqs, args.output)
        
    print(f"[SUCCESS] Converted {len(seqs)} sequences to {args.to.upper()} -> {args.output}")

if __name__ == "__main__":
    main()
