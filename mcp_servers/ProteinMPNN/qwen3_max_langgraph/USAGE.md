# repo_source MCP Server User Guide

## 1. Introduction

This MCP server provides a command-line interface to ProteinMPNN for protein sequence design and scoring based on 3D backbone structures. It supports flexible constraint specification (fixed/tied positions, chain designability, amino acid biases) and batch processing of PDB files.

**Core capabilities:**
- Parse PDB files into standardized JSONL format
- Define which chains or residues to design vs. fix
- Enforce symmetry via tied residue positions
- Apply global or per-residue amino acid biases
- Generate or score sequences with configurable sampling

---

## 2. Tool Reference

### `parse_chains`
**Purpose:** Converts PDB files to JSONL with backbone coordinates and metadata.  
**Inputs:** `input_path` (dir), `output_path` (file), `ca_only` (bool)  
**Outputs:** JSONL file (`output_path`)

### `assign_designable_chains`
**Purpose:** Specifies which chains are designable vs. fixed.  
**Inputs:** `input_path` (JSONL), `output_path` (file), `chain_list` (str list)  
**Outputs:** Chain assignment JSONL (`output_path`)

### `define_fixed_positions`
**Purpose:** Marks specific residue positions as fixed (or designable if `specify_non_fixed`).  
**Inputs:** `input_path` (JSONL), `output_path` (file), `chain_list` (str list), `position_list` (str list), `specify_non_fixed` (bool)  
**Outputs:** Fixed positions JSONL (`output_path`)

### `define_tied_positions`
**Purpose:** Links residue positions across chains for joint sampling (e.g., symmetry).  
**Inputs:** `input_path` (JSONL), `output_path` (file), `chain_list` (str list), `position_list` (str list), `homooligomer` (int)  
**Outputs:** Tied positions JSONL (`output_path`)

### `define_aa_bias`
**Purpose:** Sets global amino acid composition bias.  
**Inputs:** `output_path` (file), `AA_list` (str list), `bias_list` (float list)  
**Outputs:** AA bias JSONL (`output_path`)

### `run_inference`
**Purpose:** Generates or scores sequences using ProteinMPNN with optional constraints.  
**Inputs:**  
- Required: `out_folder`, `num_seq_per_target`, `sampling_temp`, `seed`, `batch_size`  
- Optional structural input: `pdb_path` **or** `jsonl_path`  
- Optional constraints: `chain_id_jsonl`, `fixed_positions_jsonl`, `tied_positions_jsonl`, `bias_AA_jsonl`, `bias_by_res_jsonl`  
- Other: `omit_AAs`, `model_name`, `use_soluble_model`, `score_only`, `path_to_fasta`  
**Outputs:** FASTA sequences and log files in `out_folder`

### `make_bias_per_res_dict`
**Purpose:** Generates per-residue bias dictionary from parsed PDBs.  
**Inputs:** `input_path` (dir), `output_path` (file)  
**Outputs:** Per-residue bias JSONL (`output_path`)

### `make_pssm_input_dict`
**Purpose:** Combines parsed PDBs with PSSM files into a bias-enriched JSONL.  
**Inputs:** `PSSM_input_path` (dir), `jsonl_input_path` (file), `output_path` (file)  
**Outputs:** PSSM-augmented JSONL (`output_path`)

---

## 3. Workflow Examples

### **Workflow 1: Basic Design of All Chains**
**Problem:** Generate sequences for all chains in a set of PDBs with no constraints.  
**Steps:**
1. **Parse PDBs**  
   ```bash
   parse_chains --input_path /pdbs/ --output_path parsed.jsonl
   ```
2. **Run inference**  
   ```bash
   run_inference --jsonl_path parsed.jsonl --out_folder /out/ --num_seq_per_target 8 --sampling_temp "0.1" --seed 42 --batch_size 1
   ```

### **Workflow 2: Constrained Design with Fixed Residues**
**Problem:** Design only chain A, keeping residues 10–15 and 50–55 fixed.  
**Steps:**
1. **Parse PDBs**  
   ```bash
   parse_chains --input_path /pdbs/ --output_path parsed.jsonl
   ```
2. **Assign designable chains**  
   ```bash
   assign_designable_chains --input_path parsed.jsonl --output_path chains.jsonl --chain_list "A"
   ```
3. **Define fixed positions**  
   ```bash
   define_fixed_positions --input_path parsed.jsonl --output_path fixed.jsonl --chain_list "A" --position_list "10 11 12 13 14 15,50 51 52 53 54 55"
   ```
4. **Run inference**  
   ```bash
   run_inference --jsonl_path parsed.jsonl --chain_id_jsonl chains.jsonl --fixed_positions_jsonl fixed.jsonl --out_folder /out/ --num_seq_per_target 4 --sampling_temp "0.2" --seed 0 --batch_size 1
   ```

### **Workflow 3: Symmetric Homooligomer Design**
**Problem:** Design a homodimer with symmetric residues tied.  
**Steps:**
1. **Parse PDBs**  
   ```bash
   parse_chains --input_path /pdbs/ --output_path parsed.jsonl
   ```
2. **Assign both chains as designable**  
   ```bash
   assign_designable_chains --input_path parsed.jsonl --output_path chains.jsonl --chain_list "A B"
   ```
3. **Define tied positions (symmetry)**  
   ```bash
   define_tied_positions --input_path parsed.jsonl --output_path tied.jsonl --chain_list "A B" --position_list "1 2 3,1 2 3" --homooligomer 1
   ```
4. **Run inference**  
   ```bash
   run_inference --jsonl_path parsed.jsonl --chain_id_jsonl chains.jsonl --tied_positions_jsonl tied.jsonl --out_folder /out/ --num_seq_per_target 6 --sampling_temp "0.1 0.5" --seed 123 --batch_size 2
   ```