import os
import subprocess
from typing import Optional, Union
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("repo_source")


@mcp.tool()
def get_user_guide() -> str:
    """
    READ THIS FIRST: Contains the comprehensive user manual, workflows, and parameter explanations. Essential for understanding how to use the other tools.
    """
    usage_path = os.path.join(os.path.dirname(__file__), "USAGE.md")
    if not os.path.exists(usage_path):
        return "USAGE.md not found in server directory."
    with open(usage_path, "r", encoding="utf-8") as f:
        return f.read()


@mcp.tool()
def esmfold_structure_prediction(
    fasta: str,
    pdb: str,
    model_dir: Optional[str] = None,
    num_recycles: Optional[int] = None,
    max_tokens_per_batch: Optional[int] = None,
    cpu_only: Optional[str] = None,
) -> str:
    """Predicts 3D protein structure from amino acid sequence using ESMFold."""
    cmd = ["python", "scripts/fold.py"]
    cmd.extend(["--fasta", fasta])
    cmd.extend(["--pdb", pdb])
    if model_dir is not None:
        cmd.extend(["--model-dir", model_dir])
    if num_recycles is not None:
        cmd.extend(["--num-recycles", str(num_recycles)])
    if max_tokens_per_batch is not None:
        cmd.extend(["--max-tokens-per-batch", str(max_tokens_per_batch)])
    if cpu_only is not None:
        cmd.append("--cpu-only")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    if result.returncode != 0:
        return f"Error: {result.stderr}"
    return result.stdout


@mcp.tool()
def inverse_folding_sample_sequences(
    chain: Optional[str] = None,
    temperature: Optional[float] = None,
    outpath: Optional[str] = None,
    num_samples: Optional[int] = None,
    multichain_backbone: Optional[str] = None,
    singlechain_backbone: Optional[str] = None,
) -> str:
    """Samples sequences compatible with a given backbone structure using inverse folding model (e.g., ESM-IF1)."""
    cmd = ["python", "examples/inverse_folding/sample_sequences.py"]
    if chain is not None:
        cmd.extend(["--chain", chain])
    if temperature is not None:
        cmd.extend(["--temperature", str(temperature)])
    if outpath is not None:
        cmd.extend(["--outpath", outpath])
    if num_samples is not None:
        cmd.extend(["--num-samples", str(num_samples)])
    if multichain_backbone is not None:
        cmd.append("--multichain-backbone")
    if singlechain_backbone is not None:
        cmd.append("--singlechain-backbone")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    if result.returncode != 0:
        return f"Error: {result.stderr}"
    return result.stdout


@mcp.tool()
def inverse_folding_score_likelihoods(
    outpath: Optional[str] = None,
    chain: Optional[str] = None,
    multichain_backbone: Optional[str] = None,
    singlechain_backbone: Optional[str] = None,
) -> str:
    """Computes per-residue log-likelihood scores for a given sequence-structure pair using inverse folding model."""
    cmd = ["python", "examples/inverse_folding/score_log_likelihoods.py"]
    if outpath is not None:
        cmd.extend(["--outpath", outpath])
    if chain is not None:
        cmd.extend(["--chain", chain])
    if multichain_backbone is not None:
        cmd.append("--multichain-backbone")
    if singlechain_backbone is not None:
        cmd.append("--singlechain-backbone")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    if result.returncode != 0:
        return f"Error: {result.stderr}"
    return result.stdout


@mcp.tool()
def variant_effect_prediction(
    model_location: Optional[str] = None,
    sequence: Optional[str] = None,
    dms_input: Optional[str] = None,
    mutation_col: Optional[str] = None,
    dms_output: Optional[str] = None,
    offset_idx: Optional[int] = None,
    scoring_strategy: Optional[str] = None,
    msa_path: Optional[str] = None,
) -> str:
    """Predicts functional effects of amino acid variants using ESM-1v or similar models."""
    cmd = ["python", "examples/variant-prediction/predict.py"]
    if model_location is not None:
        cmd.extend(["--model-location", model_location])
    if sequence is not None:
        cmd.extend(["--sequence", sequence])
    if dms_input is not None:
        cmd.extend(["--dms-input", dms_input])
    if mutation_col is not None:
        cmd.extend(["--mutation-col", mutation_col])
    if dms_output is not None:
        cmd.extend(["--dms-output", dms_output])
    if offset_idx is not None:
        cmd.extend(["--offset-idx", str(offset_idx)])
    if scoring_strategy is not None:
        cmd.extend(["--scoring-strategy", scoring_strategy])
    if msa_path is not None:
        cmd.extend(["--msa-path", msa_path])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    if result.returncode != 0:
        return f"Error: {result.stderr}"
    return result.stdout


@mcp.tool()
def representation_extraction(
    include: str,
    repr_layers: Optional[int] = None,
    toks_per_batch: Optional[int] = None,
    truncation_seq_length: Optional[int] = None,
) -> str:
    """Extracts ESM-2 embeddings or representations from protein sequences."""
    cmd = ["python", "scripts/extract.py"]
    cmd.extend(["--include", include])
    if repr_layers is not None:
        cmd.extend(["--repr_layers", str(repr_layers)])
    if toks_per_batch is not None:
        cmd.extend(["--toks_per_batch", str(toks_per_batch)])
    if truncation_seq_length is not None:
        cmd.extend(["--truncation_seq_length", str(truncation_seq_length)])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
    if result.returncode != 0:
        return f"Error: {result.stderr}"
    return result.stdout


if __name__ == "__main__":
    mcp.run()
