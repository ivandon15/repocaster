```markdown
# MCP Server User Guide

## Introduction

The MCP Server is designed to facilitate protein design and analysis by parsing PDB files, assigning chain roles, and running model inferences. It provides a streamlined process for preparing and analyzing protein structures.

### Core Capabilities
- Parse PDB files into JSONL format for model processing.
- Assign design and fixed roles to protein chains.
- Create dictionaries for fixed and tied positions in protein chains.
- Run model inference to generate protein sequences.

## Tool Reference

### jsonl_path
- **Purpose**: Specifies the directory containing parsed PDB files in JSONL format.
- **Input Schema**: `string` (Path to folder)
- **Output Schema**: None

### out_folder
- **Purpose**: Defines the directory for outputting generated sequences.
- **Input Schema**: `string` (Path to folder)
- **Output Schema**: None

### num_seq_per_target
- **Purpose**: Sets the number of sequences to generate per target.
- **Input Schema**: `integer`
- **Output Schema**: None

### sampling_temp
- **Purpose**: Determines the sampling temperature for amino acids, affecting diversity.
- **Input Schema**: `string` (Suggested values: 0.1, 0.15, 0.2, 0.25, 0.3)
- **Output Schema**: None

### seed
- **Purpose**: Sets the random seed for sequence generation.
- **Input Schema**: `integer`
- **Output Schema**: None

### batch_size
- **Purpose**: Configures the batch size for processing, adjustable based on GPU capacity.
- **Input Schema**: `integer`
- **Output Schema**: None

## Workflow Examples

### Workflow 1: Basic Protein Design
**Problem**: Generate protein sequences from PDB files.

1. **Parse Chains**
   - **Tool**: `parse_chains`
   - **Inputs**: 
     - `input_path`: Path to PDB files
     - `output_path`: Path to save JSONL files

2. **Assign Fixed Chains**
   - **Tool**: `assign_fixed_chains`
   - **Inputs**: 
     - `input_path`: Path to JSONL files
     - `output_path`: Path to save chain assignments
     - `chain_list`: List of chains to design/fix

3. **Run Inference**
   - **Tool**: `run_inference`
   - **Inputs**: 
     - `jsonl_path`: Path to JSONL files
     - `out_folder`: Path to save sequences
     - `num_seq_per_target`: Number of sequences per target
     - `sampling_temp`: Sampling temperature
     - `seed`: Random seed
     - `batch_size`: Batch size

### Workflow 2: Advanced Chain Positioning
**Problem**: Design proteins with specific fixed and tied positions.

1. **Parse Chains**
   - **Tool**: `parse_chains`
   - **Inputs**: 
     - `input_path`: Path to PDB files
     - `output_path`: Path to save JSONL files

2. **Assign Fixed Chains**
   - **Tool**: `assign_fixed_chains`
   - **Inputs**: 
     - `input_path`: Path to JSONL files
     - `output_path`: Path to save chain assignments
     - `chain_list`: List of chains to design/fix

3. **Make Fixed Positions Dictionary**
   - **Tool**: `make_fixed_positions_dict`
   - **Inputs**: 
     - `input_path`: Path to chain assignments
     - `output_path`: Path to save fixed positions
     - `chain_list`: List of chains
     - `position_list`: List of fixed positions

4. **Make Tied Positions Dictionary**
   - **Tool**: `make_tied_positions_dict`
   - **Inputs**: 
     - `input_path`: Path to chain assignments
     - `output_path`: Path to save tied positions
     - `chain_list`: List of chains
     - `position_list`: List of tied positions

5. **Run Inference**
   - **Tool**: `run_inference`
   - **Inputs**: 
     - `jsonl_path`: Path to JSONL files
     - `out_folder`: Path to save sequences
     - `num_seq_per_target`: Number of sequences per target
     - `sampling_temp`: Sampling temperature
     - `seed`: Random seed
     - `batch_size`: Batch size
```
