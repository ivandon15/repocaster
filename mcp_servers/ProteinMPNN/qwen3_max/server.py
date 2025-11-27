import os
import subprocess
from typing import Optional, List, Union
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("repo_source")


@mcp.tool()
def get_user_guide() -> str:
    """
    READ THIS FIRST: Contains the comprehensive user manual, workflows, and parameter explanations. Essential for understanding how to use the other tools.
    """
    usage_path = os.path.join(os.path.dirname(__file__), "USAGE.md")
    if not os.path.exists(usage_path):
        return "ERROR: USAGE.md not found in server directory."
    with open(usage_path, "r", encoding="utf-8") as f:
        return f.read()


def _run_script(script_path: str, **kwargs) -> str:
    cmd = ["python", script_path]
    for key, value in kwargs.items():
        if value is None:
            continue
        flag = f"--{key.replace('_', '-')}"
        if isinstance(value, bool):
            if value:
                cmd.append(flag)
        elif isinstance(value, list):
            for item in value:
                cmd.extend([flag, str(item)])
        else:
            cmd.extend([flag, str(value)])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    if result.returncode != 0:
        return f"ERROR: {result.stderr}"
    return result.stdout


@mcp.tool()
def parse_chains(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    ca_only: Optional[bool] = False,
) -> str:
    """Parses one or more PDB files into a standardized JSONL format containing backbone coordinates and chain metadata."""
    return _run_script(
        "helper_scripts/parse_multiple_chains.py",
        input_path=input_path,
        output_path=output_path,
        ca_only=ca_only,
    )


@mcp.tool()
def assign_designable_chains(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    chain_list: Optional[str] = None,
) -> str:
    """Specifies which chains should be designed (vs. kept fixed) during inference."""
    return _run_script(
        "helper_scripts/assign_fixed_chains.py",
        input_path=input_path,
        output_path=output_path,
        chain_list=chain_list,
    )


@mcp.tool()
def define_fixed_positions(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    chain_list: Optional[str] = None,
    position_list: Optional[str] = None,
    specify_non_fixed: Optional[bool] = False,
) -> str:
    """Defines residue positions that must remain fixed (or, with specify_non_fixed, defines positions to design)."""
    return _run_script(
        "helper_scripts/make_fixed_positions_dict.py",
        input_path=input_path,
        output_path=output_path,
        chain_list=chain_list,
        position_list=position_list,
        specify_non_fixed=specify_non_fixed,
    )


@mcp.tool()
def define_tied_positions(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
    chain_list: Optional[str] = None,
    position_list: Optional[str] = None,
    homooligomer: Optional[int] = 0,
) -> str:
    """Specifies pairs of residues across chains that must share the same amino acid during sampling (symmetry/tight coupling)."""
    return _run_script(
        "helper_scripts/make_tied_positions_dict.py",
        input_path=input_path,
        output_path=output_path,
        chain_list=chain_list,
        position_list=position_list,
        homooligomer=homooligomer,
    )


@mcp.tool()
def create_aa_bias(
    output_path: Optional[str] = None,
    AA_list: Optional[str] = None,
    bias_list: Optional[str] = None,
) -> str:
    """Generates global amino acid bias to steer sequence design toward specific physicochemical properties."""
    return _run_script(
        "helper_scripts/make_bias_AA.py",
        output_path=output_path,
        AA_list=AA_list,
        bias_list=bias_list,
    )


@mcp.tool()
def run_inference(
    out_folder: Optional[str] = None,
    num_seq_per_target: Optional[int] = None,
    sampling_temp: Optional[str] = None,
    batch_size: Optional[int] = None,
    pdb_path: Optional[str] = None,
    jsonl_path: Optional[str] = None,
    chain_id_jsonl: Optional[str] = None,
    fixed_positions_jsonl: Optional[str] = None,
    tied_positions_jsonl: Optional[str] = None,
    bias_AA_jsonl: Optional[str] = None,
    pssm_jsonl: Optional[str] = None,
    omit_AAs: Optional[str] = None,
    score_only: Optional[int] = 0,
    use_soluble_model: Optional[str] = None,
    model_name: Optional[str] = None,
) -> str:
    """Main inference script that generates or scores protein sequences given structural backbones and optional constraints."""
    return _run_script(
        "protein_mpnn_run.py",
        out_folder=out_folder,
        num_seq_per_target=num_seq_per_target,
        sampling_temp=sampling_temp,
        batch_size=batch_size,
        pdb_path=pdb_path,
        jsonl_path=jsonl_path,
        chain_id_jsonl=chain_id_jsonl,
        fixed_positions_jsonl=fixed_positions_jsonl,
        tied_positions_jsonl=tied_positions_jsonl,
        bias_AA_jsonl=bias_AA_jsonl,
        pssm_jsonl=pssm_jsonl,
        omit_AAs=omit_AAs,
        score_only=score_only,
        use_soluble_model=use_soluble_model,
        model_name=model_name,
    )


@mcp.tool()
def make_pssm_input_dict(
    PSSM_input_path: Optional[str] = None,
    jsonl_input_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """Generates a .jsonl dictionary with PSSM bias by combining parsed PDB data and PSSM files."""
    return _run_script(
        "helper_scripts/make_pssm_input_dict.py",
        PSSM_input_path=PSSM_input_path,
        jsonl_input_path=jsonl_input_path,
        output_path=output_path,
    )


@mcp.tool()
def make_bias_per_res_dict(
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """Creates a residue-level bias dictionary from parsed PDB data."""
    return _run_script(
        "helper_scripts/make_bias_per_res_dict.py",
        input_path=input_path,
        output_path=output_path,
    )


if __name__ == "__main__":
    mcp.run()
