import os
import subprocess
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("repo_source")


def get_user_guide() -> str:
    """
    READ THIS FIRST: Contains the comprehensive user manual, workflows, and parameter explanations.
    Essential for understanding how to use the other tools.
    """
    usage_path = os.path.join(os.path.dirname(__file__), "USAGE.md")
    with open(usage_path, "r") as file:
        return file.read()


@mcp.tool()
def jsonl_path(jsonl_path: Optional[str] = None) -> None:
    script_path = "scripts/jsonl_path_script.py"
    cmd = ["python", script_path]
    if jsonl_path is not None:
        cmd.extend(["--jsonl_path", jsonl_path])
    subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())


@mcp.tool()
def out_folder(out_folder: Optional[str] = None) -> None:
    script_path = "scripts/out_folder_script.py"
    cmd = ["python", script_path]
    if out_folder is not None:
        cmd.extend(["--out_folder", out_folder])
    subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())


@mcp.tool()
def num_seq_per_target(num_seq_per_target: Optional[int] = None) -> None:
    script_path = "scripts/num_seq_per_target_script.py"
    cmd = ["python", script_path]
    if num_seq_per_target is not None:
        cmd.extend(["--num_seq_per_target", str(num_seq_per_target)])
    subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())


@mcp.tool()
def sampling_temp(sampling_temp: Optional[str] = None) -> None:
    script_path = "scripts/sampling_temp_script.py"
    cmd = ["python", script_path]
    if sampling_temp is not None:
        cmd.extend(["--sampling_temp", sampling_temp])
    subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())


@mcp.tool()
def seed(seed: Optional[int] = None) -> None:
    script_path = "scripts/seed_script.py"
    cmd = ["python", script_path]
    if seed is not None:
        cmd.extend(["--seed", str(seed)])
    subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())


@mcp.tool()
def batch_size(batch_size: Optional[int] = None) -> None:
    script_path = "scripts/batch_size_script.py"
    cmd = ["python", script_path]
    if batch_size is not None:
        cmd.extend(["--batch_size", str(batch_size)])
    subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
