import os
import subprocess
from typing import Optional, List, Union
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("repo_source")


def _run_script(script_path: str, args_dict: dict) -> dict:
    """
    Helper function to run a Python script with given arguments.

    Args:
        script_path: Path to the Python script to run.
        args_dict: Dictionary of argument names and values.

    Returns:
        Dictionary with execution status and relevant outputs.
    """
    cmd = ["python", script_path]

    for key, value in args_dict.items():
        if value is None:
            continue

        # Handle boolean flags
        if isinstance(value, bool):
            if value:
                cmd.append(f"--{key}")
        # Handle lists (space-separated or multiple flags)
        elif isinstance(value, list):
            for item in value:
                cmd.extend([f"--{key}", str(item)])
        else:
            cmd.extend([f"--{key}", str(value)])

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=os.getcwd(), check=True
        )
        return {"status": "success", "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": f"Execution failed: {e.stderr}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@mcp.tool()
def get_user_guide() -> dict:
    """
    READ THIS FIRST: Contains the comprehensive user manual, workflows, and parameter explanations. Essential for understanding how to use the other tools.

    Returns:
        Dictionary containing the user guide content.
    """
    try:
        usage_path = os.path.join(os.path.dirname(__file__), "USAGE.md")
        with open(usage_path, "r") as f:
            content = f.read()
        return {"status": "completed", "user_guide": content}
    except Exception as e:
        return {"status": "error", "error": f"Failed to read USAGE.md: {str(e)}"}


@mcp.tool()
def parse_chains(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    ca_only: Optional[str] = None,
) -> dict:
    """
    Parses one or more PDB files into a standardized JSONL format containing backbone coordinates and chain metadata.

    Args:
        input_path: Path to a folder with pdb files, e.g. /home/my_pdbs/, if you find a pdb file just put the folder path to that file
        output_path: Path where to save .jsonl dictionary of parsed pdbs
        ca_only: Parse a backbone-only structure (default: false)
    """
    args = {
        "input_path": input_path,
        "output_path": output_path,
        "ca_only": ca_only.lower() == "true" if ca_only else None,
    }

    script_path = "helper_scripts/parse_multiple_chains.py"
    result = _run_script(script_path, args)

    if result["status"] == "success":
        return {"jsonl_path": output_path, "status": "inputs_prepared"}
    else:
        return result


@mcp.tool()
def assign_designable_chains(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    chain_list: Optional[str] = None,
) -> dict:
    """
    Specifies which chains should be designed (vs. kept fixed) during inference, producing a chain assignment JSONL file.

    Args:
        input_path: Path to the parsed PDBs
        output_path: Path to the output dictionary
        chain_list: List of the chains that need to be designed
    """
    args = {
        "input_path": input_path,
        "output_path": output_path,
        "chain_list": chain_list,
    }

    script_path = "helper_scripts/assign_fixed_chains.py"
    result = _run_script(script_path, args)

    if result["status"] == "success":
        return {"chain_id_jsonl": output_path, "status": "inputs_prepared"}
    else:
        return result


@mcp.tool()
def define_fixed_positions(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    chain_list: Optional[str] = None,
    position_list: Optional[str] = None,
    specify_non_fixed: Optional[str] = None,
) -> dict:
    """
    Generates a dictionary specifying which residue positions should remain fixed (or, if --specify_non_fixed is used, which positions are designable).

    Args:
        input_path: Path to the parsed PDBs
        output_path: Path to the output dictionary
        chain_list: List of the chains that need to be fixed
        position_list: Position lists, e.g. 11 12 14 18, 1 2 3 4 for first chain and the second chain
        specify_non_fixed: Allows specifying just residues that need to be designed (default: false)
    """
    args = {
        "input_path": input_path,
        "output_path": output_path,
        "chain_list": chain_list,
        "position_list": position_list,
        "specify_non_fixed": (
            specify_non_fixed.lower() == "true" if specify_non_fixed else None
        ),
    }

    script_path = "helper_scripts/make_fixed_positions_dict.py"
    result = _run_script(script_path, args)

    if result["status"] == "success":
        return {"fixed_positions_jsonl": output_path, "status": "inputs_prepared"}
    else:
        return result


@mcp.tool()
def define_tied_positions(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    chain_list: Optional[str] = None,
    position_list: Optional[str] = None,
    homooligomer: Optional[int] = None,
) -> dict:
    """
    Creates a mapping of residue positions across chains that should be sampled jointly (e.g., for symmetric complexes).

    Args:
        input_path: Path to the parsed PDBs
        output_path: Path to the output dictionary
        chain_list: List of the chains that need to be fixed
        position_list: Position lists, e.g. 11 12 14 18, 1 2 3 4 for first chain and the second chain
        homooligomer: If 0 do not use, if 1 then design homooligomer
    """
    args = {
        "input_path": input_path,
        "output_path": output_path,
        "chain_list": chain_list,
        "position_list": position_list,
        "homooligomer": homooligomer,
    }

    script_path = "helper_scripts/make_tied_positions_dict.py"
    result = _run_script(script_path, args)

    if result["status"] == "success":
        return {"tied_positions_jsonl": output_path, "status": "inputs_prepared"}
    else:
        return result


@mcp.tool()
def define_aa_bias(
    output_path: Optional[str] = None,
    AA_list: Optional[str] = None,
    bias_list: Optional[str] = None,
) -> dict:
    """
    Generates global amino acid biases to influence sequence sampling toward desired physicochemical properties.

    Args:
        output_path: Path to the output dictionary
        AA_list: List of AAs to be biased
        bias_list: AA bias strengths
    """
    args = {"output_path": output_path, "AA_list": AA_list, "bias_list": bias_list}

    script_path = "helper_scripts/make_bias_AA.py"
    result = _run_script(script_path, args)

    if result["status"] == "success":
        return {"bias_AA_jsonl": output_path, "status": "inputs_prepared"}
    else:
        return result


@mcp.tool()
def run_inference(
    out_folder: Optional[str] = None,
    num_seq_per_target: Optional[int] = None,
    sampling_temp: Optional[str] = None,
    seed: Optional[int] = None,
    batch_size: Optional[int] = None,
    pdb_path: Optional[str] = None,
    jsonl_path: Optional[str] = None,
    chain_id_jsonl: Optional[str] = None,
    fixed_positions_jsonl: Optional[str] = None,
    tied_positions_jsonl: Optional[str] = None,
    bias_AA_jsonl: Optional[str] = None,
    bias_by_res_jsonl: Optional[str] = None,
    omit_AAs: Optional[str] = None,
    model_name: Optional[str] = None,
    use_soluble_model: Optional[str] = None,
    score_only: Optional[int] = None,
    path_to_fasta: Optional[str] = None,
) -> dict:
    """
    Main inference script that generates or scores protein sequences given structural backbones and optional constraints.

    Args:
        out_folder: Path to a folder to output sequences, e.g. /home/out/
        num_seq_per_target: Number of sequences to generate per target
        sampling_temp: A string of temperatures, e.g. '0.2 0.25 0.5'. Higher values increase diversity.
        seed: Random seed; if 0, a random seed will be picked
        batch_size: Batch size; reduce if running out of GPU memory
        pdb_path: Path to a single PDB to be designed
        jsonl_path: Path to a folder with parsed pdb into jsonl
        chain_id_jsonl: Path to a dictionary specifying which chains need to be designed and which are fixed
        fixed_positions_jsonl: Path to a dictionary with fixed positions
        tied_positions_jsonl: Path to a dictionary with tied positions
        bias_AA_jsonl: Path to a dictionary which specifies AA composition bias
        bias_by_res_jsonl: Path to dictionary with per position bias
        omit_AAs: Specify which amino acids should be omitted in the generated sequence, e.g. 'AC'
        model_name: ProteinMPNN model name: v_48_002, v_48_010, v_48_020, v_48_030
        use_soluble_model: Flag to load ProteinMPNN weights trained on soluble proteins only
        score_only: 0 for False, 1 for True; score input backbone-sequence pairs
        path_to_fasta: Score provided input sequence in a fasta format; e.g. GGGGGG/PPPPS/WWW for chains A, B, C
    """
    args = {
        "out_folder": out_folder,
        "num_seq_per_target": num_seq_per_target,
        "sampling_temp": sampling_temp,
        "seed": seed,
        "batch_size": batch_size,
        "pdb_path": pdb_path,
        "jsonl_path": jsonl_path,
        "chain_id_jsonl": chain_id_jsonl,
        "fixed_positions_jsonl": fixed_positions_jsonl,
        "tied_positions_jsonl": tied_positions_jsonl,
        "bias_AA_jsonl": bias_AA_jsonl,
        "bias_by_res_jsonl": bias_by_res_jsonl,
        "omit_AAs": omit_AAs,
        "model_name": model_name,
        "use_soluble_model": (
            use_soluble_model.lower() == "true" if use_soluble_model else None
        ),
        "score_only": score_only,
        "path_to_fasta": path_to_fasta,
    }

    script_path = "protein_mpnn_run.py"
    result = _run_script(script_path, args)

    if result["status"] == "success":
        return {
            "fasta_file": (
                os.path.join(out_folder, "seqs.fasta") if out_folder else None
            ),
            "status": "completed",
        }
    else:
        return result


@mcp.tool()
def make_bias_per_res_dict(
    input_path: Optional[str] = None, output_path: Optional[str] = None
) -> dict:
    """
    Generates a residue-level bias dictionary from parsed PDB structures and saves it to a specified output path.

    Args:
        input_path: Path to the directory containing parsed PDB files
        output_path: Path where the output bias dictionary will be saved
    """
    args = {"input_path": input_path, "output_path": output_path}

    script_path = "helper_scripts/make_bias_per_res_dict.py"
    result = _run_script(script_path, args)

    if result["status"] == "success":
        return {"bias_by_res_jsonl": output_path, "status": "inputs_prepared"}
    else:
        return result


@mcp.tool()
def make_pssm_input_dict(
    PSSM_input_path: Optional[str] = None,
    jsonl_input_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> dict:
    """
    Generates a JSONL dictionary enriched with PSSM bias by combining parsed PDB data and PSSM files.

    Args:
        PSSM_input_path: Path to PSSMs saved as npz files.
        jsonl_input_path: Path where to load .jsonl dictionary of parsed pdbs.
        output_path: Path where to save .jsonl dictionary with PSSM bias.
    """
    args = {
        "PSSM_input_path": PSSM_input_path,
        "jsonl_input_path": jsonl_input_path,
        "output_path": output_path,
    }

    script_path = "helper_scripts/make_pssm_input_dict.py"
    result = _run_script(script_path, args)

    if result["status"] == "success":
        return {"pssm_jsonl": output_path, "status": "inputs_prepared"}
    else:
        return result


if __name__ == "__main__":
    mcp.run()
