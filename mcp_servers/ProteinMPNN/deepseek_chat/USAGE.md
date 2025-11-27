# ProteinMPNN MCP Server User Guide

## Introduction
This MCP server provides protein sequence design and scoring using ProteinMPNN. It generates novel protein sequences that fold into specified backbone structures while supporting various constraints and design scenarios.

**Core capabilities:**
- Design protein sequences for given backbone structures
- Score sequence-structure compatibility
- Apply chain-specific, position-level, and amino acid bias constraints
- Support tied positions for symmetric/correlated mutations
- Process single or multiple PDB structures

## Tool Reference

### protein_mpnn_run
**Purpose:** Main ProteinMPNN inference for protein sequence design and scoring.

**Input:**
```json
{
  "pdb_path": "string",
  "jsonl_path": "string",
  "pdb_path_chains": "string",
  "chain_id_jsonl": "string",
  "fixed_positions_jsonl": "string",
  "tied_positions_jsonl": "string",
  "bias_AA_jsonl": "string",
  "path_to_fasta": "string",
  "out_folder": "string",
  "num_seq_per_target": "integer",
  "sampling_temp": "string",
  "batch_size": "integer",
  "seed": "integer",
  "score_only": "integer",
  "ca_only": "string"
}
```

**Output:** Generated sequences and scores in specified output folder.

### parse_multiple_chains
**Purpose:** Parses multiple PDB files into JSON format for the model.

**Input:**
```json
{
  "input_path": "string",
  "output_path": "string",
  "ca_only": "string"
}
```

**Output:** JSONL file with parsed PDB data.

### assign_fixed_chains
**Purpose:** Assigns which chains to design vs keep fixed.

**Input:**
```json
{
  "input_path": "string",
  "output_path": "string",
  "chain_list": "string"
}
```

**Output:** Chain assignment dictionary.

### make_fixed_positions_dict
**Purpose:** Creates fixed positions dictionary for residue-level constraints.

**Input:**
```json
{
  "input_path": "string",
  "output_path": "string",
  "chain_list": "string",
  "position_list": "string"
}
```

**Output:** Fixed positions dictionary.

### make_bias_AA
**Purpose:** Creates amino acid bias dictionary for composition preferences.

**Input:**
```json
{
  "output_path": "string",
  "AA_list": "string",
  "bias_list": "string"
}
```

**Output:** Amino acid bias dictionary.

### make_tied_positions_dict
**Purpose:** Creates tied positions dictionary for correlated mutations.

**Input:**
```json
{
  "input_path": "string",
  "output_path": "string",
  "chain_list": "string",
  "position_list": "string"
}
```

**Output:** Tied positions dictionary.

## Workflow Examples

### Basic Single Chain Design
**Problem:** Design sequences for a single protein chain.

**Steps:**
1. **Run ProteinMPNN inference:**
   ```json
   {
     "pdb_path": "/path/to/structure.pdb",
     "pdb_path_chains": "A",
     "out_folder": "/path/to/output",
     "num_seq_per_target": 10,
     "sampling_temp": "0.1",
     "batch_size": 1,
     "seed": 0
   }
   ```

### Multi-Chain Complex Design
**Problem:** Design specific chains in a protein complex while keeping others fixed.

**Steps:**
1. **Parse PDB structure:**
   ```json
   {
     "input_path": "/path/to/pdbs",
     "output_path": "/path/to/parsed.jsonl"
   }
   ```

2. **Assign chains to design:**
   ```json
   {
     "input_path": "/path/to/parsed.jsonl",
     "output_path": "/path/to/chain_assign.json",
     "chain_list": "A B"
   }
   ```

3. **Run constrained design:**
   ```json
   {
     "jsonl_path": "/path/to/parsed.jsonl",
     "chain_id_jsonl": "/path/to/chain_assign.json",
     "out_folder": "/path/to/output",
     "num_seq_per_target": 10,
     "sampling_temp": "0.1",
     "batch_size": 1,
     "seed": 0
   }
   ```

### Position-Constrained Design with AA Bias
**Problem:** Design specific positions with amino acid composition preferences.

**Steps:**
1. **Create AA bias dictionary:**
   ```json
   {
     "output_path": "/path/to/bias.json",
     "AA_list": "A R N D",
     "bias_list": "2.0 1.5 0.5 -1.0"
   }
   ```

2. **Parse structure:**
   ```json
   {
     "input_path": "/path/to/pdbs",
     "output_path": "/path/to/parsed.jsonl"
   }
   ```

3. **Run biased design:**
   ```json
   {
     "jsonl_path": "/path/to/parsed.jsonl",
     "bias_AA_jsonl": "/path/to/bias.json",
     "out_folder": "/path/to/output",
     "num_seq_per_target": 10,
     "sampling_temp": "0.1",
     "batch_size": 1,
     "seed": 0
   }
   ```