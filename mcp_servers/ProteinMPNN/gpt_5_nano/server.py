import os
import subprocess
from typing import Optional, List

from mcp.server.fastmcp import FastMCP

# Initialize MCP server with the given server name
mcp = FastMCP("repo_source")


def _run_script(script_path: str, args: dict) -> str:
    """
    Internal helper to run a Python script with constructed CLI arguments.

    Args:
        script_path: Path to the script (relative to repo root).
        args: Dictionary of argument names to values.

    Returns:
        The stdout from the script if successful, or an error message with stderr.
    """
    # Resolve script path relative to repository root
    repo_root = os.path.dirname(os.path.abspath(__file__))
    script_full_path = script_path
    if not os.path.isabs(script_full_path):
        script_full_path = os.path.join(repo_root, script_path)

    cmd = ["python", script_full_path]

    for key, value in args.items():
        if value is None:
            continue
        if isinstance(value, bool):
            if value:
                cmd.append(f"--{key}")
            continue
        if isinstance(value, list):
            for item in value:
                if item is None:
                    continue
                cmd.extend([f"--{key}", str(item)])
        else:
            cmd.extend([f"--{key}", str(value)])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    if result.returncode != 0:
        return f"Error running {script_path} with args {args}:\n{result.stderr}"
    return result.stdout


# Special tool to expose user guide with required docstring
@mcp.tool()
def get_user_guide() -> str:
    """
    READ THIS FIRST: Contains the comprehensive user manual, workflows, and parameter explanations. Essential for understanding how to use the other tools.
    """
    usage_file = os.path.join(os.path.dirname(__file__), "USAGE.md")
    if os.path.exists(usage_file):
        with open(usage_file, "r", encoding="utf-8") as f:
            return f.read()
    return "USAGE.md not found"


# Tool 1: parse_chains
@mcp.tool()
def parse_chains(
    input_path: str, output_path: str, ca_only: Optional[str] = None
) -> str:
    """
    Parse raw PDB files (potentially multiple chains) into a parsed chains JSONL format suitable for ProteinMPNN input.

    Args:
        input_path: Path to a folder containing PDB files
        output_path: Path where to save the parsed .jsonl dictionary
        ca_only: Parse backbone CA-only structures (default: None)
    """
    script_path = "helper_scripts/parse_multiple_chains.py"
    args = {
        "input_path": input_path,
        "output_path": output_path,
        "ca_only": ca_only,
    }
    return _run_script(script_path, args)


# Tool 2: assign_fixed_chains
@mcp.tool()
def assign_fixed_chains(input_path: str, output_path: str, chain_list: str) -> str:
    """
    Mark which chains are designable vs fixed by listing chains to design.

    Args:
        input_path: Path to the parsed PDBs
        output_path: Path to the output dictionary
        chain_list: List of the chains that need to be designed
    """
    script_path = "helper_scripts/assign_fixed_chains.py"
    args = {
        "input_path": input_path,
        "output_path": output_path,
        "chain_list": chain_list,
    }
    return _run_script(script_path, args)


# Tool 3: make_fixed_positions_dict
@mcp.tool()
def make_fixed_positions_dict(
    input_path: str,
    output_path: str,
    chain_list: str,
    position_list: str,
    specify_non_fixed: Optional[str] = None,
) -> str:
    """
    Create a dictionary of fixed residues per chain to constrain design positions.

    Args:
        input_path: Path to the parsed PDBs
        output_path: Path to the output dictionary
        chain_list: List of the chains that need to be fixed
        position_list: Position lists, e.g. "11 12 14 18", "1 2 3 4"
        specify_non_fixed: Allows specifying residues that need to be designed (default: None)
    """
    script_path = "helper_scripts/make_fixed_positions_dict.py"
    args = {
        "input_path": input_path,
        "output_path": output_path,
        "chain_list": chain_list,
        "position_list": position_list,
        "specify_non_fixed": specify_non_fixed,
    }
    return _run_script(script_path, args)


# Tool 4: make_tied_positions_dict
@mcp.tool()
def make_tied_positions_dict(
    input_path: str,
    output_path: str,
    chain_list: str,
    position_list: str,
    homooligomer: Optional[int] = None,
    pos_neg_chain_list: Optional[str] = None,
    pos_neg_chain_betas: Optional[str] = None,
) -> str:
    """
    Create a dictionary of tied positions to sample residues jointly across chains.

    Args:
        input_path: Path to the parsed PDBs
        output_path: Path to the output dictionary
        chain_list: List of the chains that need to be fixed
        position_list: Position lists, e.g. "11 12 14 18"
        homooligomer: If 0 do not use, if 1 then design homooligomer
        pos_neg_chain_list: Chain lists to be tied together
        pos_neg_chain_betas: Chain beta list for the chain lists provided; 1.0 for positive design, -0.1 or -0.5 for negative, 0.0 means do not use that chain info
    """
    script_path = "helper_scripts/make_tied_positions_dict.py"
    args = {
        "input_path": input_path,
        "output_path": output_path,
        "chain_list": chain_list,
        "position_list": position_list,
        "homooligomer": homooligomer,
        "pos_neg_chain_list": pos_neg_chain_list,
        "pos_neg_chain_betas": pos_neg_chain_betas,
    }
    return _run_script(script_path, args)


# Tool 5: make_bias_AA
@mcp.tool()
def make_bias_AA(output_path: str, AA_list: str, bias_list: str) -> str:
    """
    Generate an amino-acid bias dictionary to bias design toward specified residues.

    Args:
        output_path: Path to the output dictionary
        AA_list: List of AAs to be biased
        bias_list: AA bias strengths
    """
    script_path = "helper_scripts/make_bias_AA.py"
    args = {
        "output_path": output_path,
        "AA_list": AA_list,
        "bias_list": bias_list,
    }
    return _run_script(script_path, args)


# Tool 6: protein_inference
@mcp.tool()
def protein_inference(
    out_folder: str,
    num_seq_per_target: int,
    sampling_temp: str,
    seed: int,
    batch_size: int,
    jsonl_path: Optional[str] = None,
    chain_id_jsonl: Optional[str] = None,
    fixed_positions_jsonl: Optional[str] = None,
    tied_positions_jsonl: Optional[str] = None,
    bias_AA_jsonl: Optional[str] = None,
    pdb_path: Optional[str] = None,
    pdb_path_chains: Optional[str] = None,
    path_to_fasta: Optional[str] = None,
    path_to_model_weights: Optional[str] = None,
    model_name: Optional[str] = None,
    ca_only: Optional[str] = None,
) -> str:
    """
    Run ProteinMPNN inference to generate designed sequences/backbone coordinates.

    Args:
        out_folder: Output folder for designs
        num_seq_per_target: Number of sequences to generate per target
        sampling_temp: Sampling temperatures for amino acids
        seed: Random seed; use 0 for a random seed
        batch_size: Batch size for GPU inference
        jsonl_path: Path to parsed pdbs in jsonl format
        chain_id_jsonl: Path to chain-id mapping jsonl
        fixed_positions_jsonl: Path to fixed positions jsonl
        tied_positions_jsonl: Path to tied positions jsonl
        bias_AA_jsonl: Path to AA bias jsonl
        pdb_path: Path to a single PDB to be designed
        pdb_path_chains: Chains to design in the provided PDB
        path_to_fasta: Path to a fasta file with sequences to design
        path_to_model_weights: Path to model weights folder
        model_name: ProteinMPNN model name
        ca_only: Parse CA-only structures and use CA-only models
    """
    script_path = "protein_mpnn_run.py"
    args = {
        "out_folder": out_folder,
        "num_seq_per_target": num_seq_per_target,
        "sampling_temp": sampling_temp,
        "seed": seed,
        "batch_size": batch_size,
        "jsonl_path": jsonl_path,
        "chain_id_jsonl": chain_id_jsonl,
        "fixed_positions_jsonl": fixed_positions_jsonl,
        "tied_positions_jsonl": tied_positions_jsonl,
        "bias_AA_jsonl": bias_AA_jsonl,
        "pdb_path": pdb_path,
        "pdb_path_chains": pdb_path_chains,
        "path_to_fasta": path_to_fasta,
        "path_to_model_weights": path_to_model_weights,
        "model_name": model_name,
        "ca_only": ca_only,
    }
    return _run_script(script_path, args)
