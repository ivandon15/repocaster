# MCP Server User Guide (`repo_source`)

## Introduction

This MCP server provides a command-line interface to ProteinMPNN for structure-based protein sequence design with flexible constraints.

**Core capabilities:**
- Parse PDB structures into model-ready JSONL format
- Specify which chains or residues to design vs. fix
- Enforce symmetry via tied residue positions across chains
- Apply global or per-residue amino acid biases
- Generate or score sequences using trained ProteinMPNN models

---

## Tool Reference

### `parse_chains`
**Purpose:** Converts PDB files into standardized JSONL with backbone coordinates and chain metadata.  
**Input:**  
- `input_path`: Folder containing `.pdb` files  
- `output_path`: Output `.jsonl` file path  
- `ca_only` (optional): `"true"` for Cα-only parsing  
**Output:** JSONL file with parsed structure data

### `assign_designable_chains`
**Purpose:** Defines which chains are designable vs. fixed during inference.  
**Input:**  
- `input_path`: Parsed `.jsonl` file  
- `output_path`: Output dictionary path  
- `chain_list`: Space-separated list of designable chain IDs (e.g., `"A B"`)  
**Output:** JSONL file mapping PDBs to designable chains

### `define_fixed_positions`
**Purpose:** Specifies fixed residue positions (or designable positions if `specify_non_fixed=true`).  
**Input:**  
- `input_path`: Parsed `.jsonl` file  
- `output_path`: Output dictionary path  
- `chain_list`: Chain IDs (e.g., `"A B"`)  
- `position_list`: Space-separated positions per chain (e.g., `"10 12, 5 7"`)  
- `specify_non_fixed` (optional): `"true"` to define designable instead of fixed positions  
**Output:** JSONL file with fixed/designable residue masks

### `define_tied_positions`
**Purpose:** Enforces identical amino acids at specified positions across chains (e.g., for symmetry).  
**Input:**  
- `input_path`: Parsed `.jsonl` file  
- `output_path`: Output dictionary path  
- `chain_list`: Chain IDs (e.g., `"A B"`)  
- `position_list`: Positions per chain (e.g., `"10 12, 10 12"`)  
- `homooligomer` (optional): `1` to auto-generate symmetric ties  
**Output:** JSONL file with tied position groups

### `create_aa_bias`
**Purpose:** Creates global amino acid composition bias.  
**Input:**  
- `output_path`: Output dictionary path  
- `AA_list`: Amino acid codes (e.g., `"K R E D"`)  
- `bias_list`: Bias values (e.g., `"2.0 2.0 -1.0 -1.0"`)  
**Output:** JSONL file with global AA bias weights

### `run_inference`
**Purpose:** Generates or scores sequences using ProteinMPNN with optional constraints.  
**Input:**  
- `out_folder`: Output directory  
- `num_seq_per_target`: Number of sequences per structure  
- `sampling_temp`: Sampling temperatures (e.g., `"0.1 0.5"`)  
- `batch_size`: Inference batch size  
- One of: `pdb_path` (single PDB) **or** `jsonl_path` (parsed batch)  
- Optional constraint paths: `chain_id_jsonl`, `fixed_positions_jsonl`, `tied_positions_jsonl`, `bias_AA_jsonl`, `pssm_jsonl`  
- Optional flags: `omit_AAs`, `score_only` (`0`/`1`), `use_soluble_model`, `model_name`  
**Output:** FASTA files with designed/scored sequences

### `make_pssm_input_dict`
**Purpose:** Combines PSSM data with parsed structures for position-specific scoring matrix bias.  
**Input:**  
- `PSSM_input_path`: Folder with `.npz` PSSM files  
- `jsonl_input_path`: Parsed `.jsonl` file  
- `output_path`: Output `.jsonl` path  
**Output:** JSONL file with PSSM bias per residue

### `make_bias_per_res_dict`
**Purpose:** Generates per-residue bias placeholder from parsed structures.  
**Input:**  
- `input_path`: Parsed `.jsonl` file  
- `output_path`: Output dictionary path  
**Output:** JSONL file with zero-initialized per-residue bias

---

## Workflow Examples

### 1. Basic Design of All Chains in a PDB Directory
**Problem:** Generate sequences for all chains in multiple PDBs without constraints.  
**Steps:**
1. **Parse PDBs**  
   ```bash
   parse_chains --input_path /pdbs/ --output_path parsed.jsonl
   ```
2. **Run inference**  
   ```bash
   run_inference --jsonl_path parsed.jsonl --out_folder /out/ --num_seq_per_target 8 --sampling_temp "0.1" --batch_size 1
   ```

### 2. Constrained Design with Fixed Residues and Symmetry
**Problem:** Design chains A and B while fixing catalytic residues and enforcing symmetry.  
**Steps:**
1. **Parse PDBs**  
   ```bash
   parse_chains --input_path /pdbs/ --output_path parsed.jsonl
   ```
2. **Assign designable chains**  
   ```bash
   assign_designable_chains --input_path parsed.jsonl --output_path chains.jsonl --chain_list "A B"
   ```
3. **Fix catalytic residues (e.g., A:50, B:50)**  
   ```bash
   define_fixed_positions --input_path parsed.jsonl --output_path fixed.jsonl --chain_list "A B" --position_list "50, 50"
   ```
4. **Tie symmetric positions (e.g., A:10-20 ↔ B:10-20)**  
   ```bash
   define_tied_positions --input_path parsed.jsonl --output_path tied.jsonl --chain_list "A B" --position_list "10 11 12 13 14 15 16 17 18 19 20, 10 11 12 13 14 15 16 17 18 19 20"
   ```
5. **Run inference with constraints**  
   ```bash
   run_inference --jsonl_path parsed.jsonl --out_folder /out/ --num_seq_per_target 4 --sampling_temp "0.2" --batch_size 1 \
     --chain_id_jsonl chains.jsonl --fixed_positions_jsonl fixed.jsonl --tied_positions_jsonl tied.jsonl
   ```

### 3. Single-PDB Design with Global AA Bias
**Problem:** Design a single PDB favoring charged residues.  
**Steps:**
1. **Create AA bias (favor K/R, disfavor A/V)**  
   ```bash
   create_aa_bias --output_path bias.jsonl --AA_list "K R A V" --bias_list "1.5 1.5 -1.0 -1.0"
   ```
2. **Run inference directly on PDB**  
   ```bash
   run_inference --pdb_path target.pdb --out_folder /out/ --num_seq_per_target 10 --sampling_temp "0.3" --batch_size 1 \
     --bias_AA_jsonl bias.jsonl
   ```