import os
import subprocess
from typing import Optional
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("repo_source")


@mcp.tool()
def get_user_guide() -> str:
    """READ THIS FIRST: Contains the comprehensive user manual, workflows, and parameter explanations. Essential for understanding how to use the other tools."""
    try:
        file_path = os.path.join(os.path.dirname(__file__), "USAGE.md")
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "USAGE.md not found. Please ensure the user guide file exists in the repository root."
    except Exception as e:
        return f"Error reading user guide: {str(e)}"


@mcp.tool()
def protein_mpnn_run(
    pdb_path: Optional[str] = None,
    jsonl_path: Optional[str] = None,
    pdb_path_chains: Optional[str] = None,
    chain_id_jsonl: Optional[str] = None,
    fixed_positions_jsonl: Optional[str] = None,
    tied_positions_jsonl: Optional[str] = None,
    bias_AA_jsonl: Optional[str] = None,
    path_to_fasta: Optional[str] = None,
    out_folder: Optional[str] = None,
    num_seq_per_target: Optional[int] = None,
    sampling_temp: Optional[str] = None,
    batch_size: Optional[int] = None,
    seed: Optional[int] = None,
    score_only: Optional[int] = None,
    ca_only: Optional[str] = None,
) -> str:
    """Main ProteinMPNN inference for protein sequence design and scoring"""
    cmd = ["python", "protein_mpnn_run.py"]

    if pdb_path is not None:
        cmd.extend(["--pdb_path", pdb_path])
    if jsonl_path is not None:
        cmd.extend(["--jsonl_path", jsonl_path])
    if pdb_path_chains is not None:
        cmd.extend(["--pdb_path_chains", pdb_path_chains])
    if chain_id_jsonl is not None:
        cmd.extend(["--chain_id_jsonl", chain_id_jsonl])
    if fixed_positions_jsonl is not None:
        cmd.extend(["--fixed_positions_jsonl", fixed_positions_jsonl])
    if tied_positions_jsonl is not None:
        cmd.extend(["--tied_positions_jsonl", tied_positions_jsonl])
    if bias_AA_jsonl is not None:
        cmd.extend(["--bias_AA_jsonl", bias_AA_jsonl])
    if path_to_fasta is not None:
        cmd.extend(["--path_to_fasta", path_to_fasta])
    if out_folder is not None:
        cmd.extend(["--out_folder", out_folder])
    if num_seq_per_target is not None:
        cmd.extend(["--num_seq_per_target", str(num_seq_per_target)])
    if sampling_temp is not None:
        cmd.extend(["--sampling_temp", sampling_temp])
    if batch_size is not None:
        cmd.extend(["--batch_size", str(batch_size)])
    if seed is not None:
        cmd.extend(["--seed", str(seed)])
    if score_only is not None:
        cmd.extend(["--score_only", str(score_only)])
    if ca_only is not None:
        cmd.extend(["--ca_only", ca_only])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"


@mcp.tool()
def parse_multiple_chains(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    ca_only: Optional[str] = None,
) -> str:
    """Parses multiple PDB files into JSON format for the model"""
    cmd = ["python", "helper_scripts/parse_multiple_chains.py"]

    if input_path is not None:
        cmd.extend(["--input_path", input_path])
    if output_path is not None:
        cmd.extend(["--output_path", output_path])
    if ca_only is not None:
        cmd.extend(["--ca_only", ca_only])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"


@mcp.tool()
def assign_fixed_chains(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    chain_list: Optional[str] = None,
) -> str:
    """Assigns which chains to design vs keep fixed"""
    cmd = ["python", "helper_scripts/assign_fixed_chains.py"]

    if input_path is not None:
        cmd.extend(["--input_path", input_path])
    if output_path is not None:
        cmd.extend(["--output_path", output_path])
    if chain_list is not None:
        cmd.extend(["--chain_list", chain_list])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"


@mcp.tool()
def make_fixed_positions_dict(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    chain_list: Optional[str] = None,
    position_list: Optional[str] = None,
) -> str:
    """Creates fixed positions dictionary for residue-level constraints"""
    cmd = ["python", "helper_scripts/make_fixed_positions_dict.py"]

    if input_path is not None:
        cmd.extend(["--input_path", input_path])
    if output_path is not None:
        cmd.extend(["--output_path", output_path])
    if chain_list is not None:
        cmd.extend(["--chain_list", chain_list])
    if position_list is not None:
        cmd.extend(["--position_list", position_list])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"


@mcp.tool()
def make_bias_AA(
    output_path: Optional[str] = None,
    AA_list: Optional[str] = None,
    bias_list: Optional[str] = None,
) -> str:
    """Creates amino acid bias dictionary for composition preferences"""
    cmd = ["python", "helper_scripts/make_bias_AA.py"]

    if output_path is not None:
        cmd.extend(["--output_path", output_path])
    if AA_list is not None:
        cmd.extend(["--AA_list", AA_list])
    if bias_list is not None:
        cmd.extend(["--bias_list", bias_list])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"


@mcp.tool()
def make_tied_positions_dict(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    chain_list: Optional[str] = None,
    position_list: Optional[str] = None,
) -> str:
    """Creates tied positions dictionary for correlated mutations"""
    cmd = ["python", "helper_scripts/make_tied_positions_dict.py"]

    if input_path is not None:
        cmd.extend(["--input_path", input_path])
    if output_path is not None:
        cmd.extend(["--output_path", output_path])
    if chain_list is not None:
        cmd.extend(["--chain_list", chain_list])
    if position_list is not None:
        cmd.extend(["--position_list", position_list])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
