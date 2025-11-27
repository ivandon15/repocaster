# MCP Server User Guide (Markdown)

Introduction
- The MCP server orchestrates a modular ProteinMPNN design workflow: parse raw PDBs, designate fixed/designable chains and residues, optionally tie or bias positions, and run protein design inference.
- Core capabilities
  - Convert raw PDBs into a JSONL format suitable for ProteinMPNN input.
  - Mark designable vs fixed chains and constrain design positions (fixed, tied, or biased).
  - Support CA-only structures and CA-only models.
  - Run ProteinMPNN inference to generate designed sequences and backbone coordinates.

Tool Reference

- Tool: parse_chains
  - Purpose: Parse raw PDB files (potentially multiple chains) into a parsed chains JSONL format suitable for ProteinMPNN input.
  - Input schema
    - input_path: string (required) – Path to a folder containing PDB files
    - output_path: string (required) – Path where to save the parsed .jsonl dictionary
    - ca_only: string (optional) – Parse backbone CA-only structures (default: false)
  - Output schema
    - parsed_pdbs_jsonl_path: string – Path to saved parsed_pdbs.jsonl
    - content_description: JSONL objects per chain (e.g., chain_id, residues) (minimal description)

- Tool: assign_fixed_chains
  - Purpose: Mark which chains are designable vs fixed by listing chains to design.
  - Input schema
    - input_path: string (required) – Path to the parsed PDBs
    - output_path: string (required) – Path to the output dictionary
    - chain_list: string (required) – List of chains to design (e.g., "A B")
  - Output schema
    - fixed_design_map_path: string – Path to the output dictionary categorizing chains as designable/fixed
    - content_description: JSON containing chain designability flags (minimal)

- Tool: make_fixed_positions_dict
  - Purpose: Create a dictionary of fixed residues per chain to constrain design positions.
  - Input schema
    - input_path: string (required) – Path to the parsed PDBs
    - output_path: string (required) – Path to the output dictionary
    - chain_list: string (required) – List of chains to fix
    - position_list: string (required) – Positions to fix (e.g., "11 12 14 18")
    - specify_non_fixed: string (optional) – Allows specifying residues to be designed (default: false)
  - Output schema
    - fixed_positions_jsonl_path: string – Path to the fixed_positions.jsonl
    - content_description: JSON mapping chains → fixed residue indices (minimal)

- Tool: make_tied_positions_dict
  - Purpose: Create a dictionary of tied positions to sample residues jointly across chains.
  - Input schema
    - input_path: string (required)
    - output_path: string (required)
    - chain_list: string (required)
    - position_list: string (required) – Positions to tie (e.g., "11 12 14 18")
    - homooligomer: integer (optional) – If 1, design homooligomer
    - pos_neg_chain_list: string (optional) – Chain lists to be tied together
    - pos_neg_chain_betas: string (optional) – Beta weights per chain (1.0, -0.1, -0.5, 0.0)
  - Output schema
    - tied_positions_jsonl_path: string – Path to the tied_positions.jsonl
    - content_description: JSON describing tied sets (minimal)

- Tool: make_bias_AA
  - Purpose: Generate an amino-acid bias dictionary to bias design toward specified residues.
  - Input schema
    - output_path: string (required) – Path to the output dictionary
    - AA_list: string (required) – List of AAs to bias
    - bias_list: string (required) – Bias strengths corresponding to AA_list
  - Output schema
    - bias_AA_jsonl_path: string – Path to bias_AA.jsonl
    - content_description: JSON mapping AA → biasStrength (minimal)

- Tool: protein_inference
  - Purpose: Run ProteinMPNN inference to generate designed sequences/backbone coordinates.
  - Input schema
    - out_folder: string (required) – Output folder for designs
    - num_seq_per_target: integer (required) – Number of sequences per target
    - sampling_temp: string (required) – Space-separated temperatures for amino acids
    - seed: integer (required) – Random seed; 0 for random
    - batch_size: integer (required) – Batch size for GPU inference
    - jsonl_path: string (optional) – Path to parsed pdbs in jsonl format
    - chain_id_jsonl: string (optional) – Path to chain-id mapping jsonl
    - fixed_positions_jsonl: string (optional) – Path to fixed positions jsonl
    - tied_positions_jsonl: string (optional) – Path to tied positions jsonl
    - bias_AA_jsonl: string (optional) – Path to AA bias jsonl
    - pdb_path: string (optional) – Path to a single PDB to be designed
    - pdb_path_chains: string (optional) – Chains to design in the provided PDB
    - path_to_fasta: string (optional) – Path to a fasta file with sequences to design
    - path_to_model_weights: string (optional) – Path to model weights folder
    - model_name: string (optional) – ProteinMPNN model name
    - ca_only: string (optional) – Parse CA-only structures and use CA-only models
  - Output schema
    - out_folder: string – Location where designed sequences and coordinates are stored
    - content_description: basic summary of generated designs (minimal)

Workflow Examples

Workflow 1: End-to-end raw PDB design with fixed residues
- Problem solved: From raw PDBs, fix specific residues on a chain and run a design pass.
- Steps
  1) parse_chains
     - Input: input_path="raw_pdbs/", output_path="parsed_pdbs.jsonl"
     - ca_only: false (optional)
  2) assign_fixed_chains
     - Input: input_path="parsed_pdbs.jsonl", output_path="designable_fixed.json", chain_list="A"
  3) make_fixed_positions_dict
     - Input: input_path="parsed_pdbs.jsonl", output_path="fixed_positions.jsonl", chain_list="A", position_list="11 12 14"
  4) protein_inference
     - Input: out_folder="designs/end2end_fixA/", num_seq_per_target=20, sampling_temp="0.8 1.0 1.2", seed=42, batch_size=8
     - jsonl_path="parsed_pdbs.jsonl", fixed_positions_jsonl="fixed_positions.jsonl"
- Required inputs (per step)
  - Step 1: raw_pdbs/; parsed_pdbs.jsonl
  - Step 2: parsed_pdbs.jsonl; designable_fixed.json; chain_list="A"
  - Step 3: parsed_pdbs.jsonl; fixed_positions.jsonl; chain_list="A"; position_list="11 12 14"
  - Step 4: designs/output folder, plus required inference args; fixed_positions_jsonl

Workflow 2: Design with tied positions across chains
- Problem solved: Tie residues across chains to sample jointly.
- Steps
  1) parse_chains
     - Input: input_path="raw_pdbs/", output_path="parsed_pdbs.jsonl"
  2) make_tied_positions_dict
     - Input: input_path="parsed_pdbs.jsonl", output_path="tied_positions.jsonl", chain_list="A B", position_list="11 12 14"
  3) protein_inference
     - Input: out_folder="designs/tied/", num_seq_per_target=15, sampling_temp="0.8 1.0", seed=0, batch_size=8
     - jsonl_path="parsed_pdbs.jsonl", tied_positions_jsonl="tied_positions.jsonl"
- Required inputs
  - Step 1: raw_pdbs/; parsed_pdbs.jsonl
  - Step 2: parsed_pdbs.jsonl; tied_positions.jsonl; chain_list="A B"; position_list="11 12 14"
  - Step 3: designs/tied/, num_seq_per_target, sampling_temp, seed, batch_size; jsonl_path; tied_positions_jsonl

Workflow 3: Bias-guided design
- Problem solved: Bias design toward specific amino acids globally.
- Steps
  1) parse_chains
     - Input: input_path="raw_pdbs/", output_path="parsed_pdbs.jsonl"
  2) make_bias_AA
     - Input: output_path="bias_AA.jsonl", AA_list="H L F", bias_list="1.0 0.8 0.5"
  3) protein_inference
     - Input: out_folder="designs/bias/", num_seq_per_target=25, sampling_temp="0.9", seed=7, batch_size=8
     - jsonl_path="parsed_pdbs.jsonl", bias_AA_jsonl="bias_AA.jsonl"
- Required inputs
  - Step 1: raw_pdbs/; parsed_pdbs.jsonl
  - Step 2: output_path="bias_AA.jsonl"; AA_list; bias_list
  - Step 3: designs/bias/, num_seq_per_target, sampling_temp, seed, batch_size; jsonl_path; bias_AA_jsonl

Notes
- Optional CA-only paths (ca_only) can be used in parse_chains and/or protein_inference to leverage CA-only models.
- The JSONL outputs are intended as inputs to downstream steps; paths referenced should be consistent across steps.
- The essential arguments per workflow are the ones labeled “required” in the tool definitions.