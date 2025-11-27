WORKFLOW_ANALYST_PROMPT = """
You are a Senior DevOps Engineer analyzing a scientific code repository (like RFDiffusion or ProteinMPNN).

Goal: Identify the "Golden Workflows" for INFERENCE. 

CRITICAL INSTRUCTION:
Scientific repositories often have PRE-PROCESSING scripts (e.g., `parse_multiple_chains.py`, `assign_fixed_chains.py`, `make_fixed_positions_dict.py`) that MUST be run before the main inference script.
You MUST identify these helper scripts and include them in the workflow.

Ignore training workflows (backpropagation, loss calculation, etc).

AST DETECTED SCRIPTS:
{ast_summary}

USAGE EXAMPLES (Shell/Python):
{examples_text}

README SNIPPET:
{readme_snippet}

Analyze the inputs to find:
1. What is the main entry point script?
2. What are the PRE-REQUISITE scripts (parsing, data prep) that must be run first?
3. What arguments are ALWAYS used together?

Return a JSON list of identified tasks in execution order.
Format:
[
    {{
        "task_name": "parse_chains",
        "target_script_path": "helper_scripts/parse_multiple_chains.py",
        "description": "Parses PDB files into JSON format for the model.",
        "essential_args": ["input_path", "output_path"],
        "notes": "Step 1: Prepares input data."
    }},
    {{
        "task_name": "run_inference",
        "target_script_path": "scripts/run_inference.py",
        "description": "Runs the main model inference.",
        "essential_args": ["config", "output_dir"],
        "notes": "Step 2: Main inference."
    }}
]
"""

SCHEMA_REFINER_PROMPT = """
You are an API Architect. Define the MCP Tools based on the code analysis.

AST DETAILS (Ground Truth for Arguments):
{ast_json}

WORKFLOW INSIGHTS (Context for descriptions):
{workflows_json}

**CRITICAL INSTRUCTIONS FOR ARGUMENTS**:
1. **FOCUS ON RELEVANCE**: Do NOT include all arguments if the script has many (e.g. > 15). Focus only on arguments that appear in `WORKFLOW INSIGHTS` or are clearly critical for inference.
2. **MANDATORY**:
   - ALL arguments marked `required: True` in AST.
   - Key input/output paths (files, directories).
   - Core model parameters mentioned in workflows.
3. **FILTER NOISE**: Exclude debug flags, obscure hyperparameters, or training-only args unless they are commonly used.
4. **DEFAULTS**: Respect `required: False` from AST.

Return JSON list:
[
    {{
        "tool_name": "generate_structure",
        "script_path": "run_inference.py",
        "description": "...",
        "args": [
            {{ "name": "output_path", "type": "string", "required": true, "description": "Path to save outputs" }},
            {{ "name": "num_designs", "type": "integer", "required": false, "description": "Number of designs to generate", "default": 1 }}
        ]
    }}
]
"""

TOOL_CRITIC_PROMPT = """
You are a QA Lead for a scientific software wrapper.

Current Tool Definitions:
{tool_definitions}

Candidate Scripts (Not yet included):
{candidates}

Your Goal: Ensure the MCP server is complete but **MINIMAL**. Avoid redundancy.

**CRITICAL RULES**:
1. **NO REDUNDANCY**: Do NOT suggest a script if its functionality is already covered by an existing tool (e.g., via a flag or argument).
2. **DISTINCT PURPOSE**: Only suggest "Helper Scripts" if they perform a *distinct, necessary step* in the workflow (e.g., a mandatory pre-processing script that produces a required input file).
3. **IGNORE TRIVIAL SCRIPTS**: Ignore simple wrappers, demos, or minor utility scripts that are not part of the core inference pipeline.

**STEP 1: CHECK MISSING SCRIPTS (Coverage)**
Review `Candidate Scripts`. Are we missing any *essential* scripts for the workflow?
- **Data Prep**: Mandatory scripts to convert raw inputs to model inputs.
- **Post-Processing**: Mandatory scripts to interpret model outputs.
*If yes, add their paths to `missing_paths`.*

**STEP 2: CHECK MISSING ARGUMENTS (Usability)**
Review `Current Tool Definitions`. Do they expose all CRITICAL arguments?
- **Inputs/Outputs**: Are file paths (input files, output directories) exposed?
- **Model Config**: Are key parameters (temperature, seed, model selection) exposed?
*If an existing tool is missing critical args, add its script path to `missing_paths` to trigger a revision.*

Return JSON:
{{
    "approved": boolean, // true if NO missing essential scripts AND NO missing critical args
    "missing_paths": ["path/to/missing_script.py"]
}}
"""

TOOL_REVISER_PROMPT = """
Generate or Revise MCP Tool definitions for the following scripts:
{scripts_json}

**CONTEXT**:
- You are defining tools for an MCP server.
- **ONE SCRIPT = ONE TOOL**. Do not create multiple tools for the same script.

**INSTRUCTIONS**:
1. **Analyze AST**: Look at the `args` list in the provided JSON.
2. **Select Arguments (Be Comprehensive yet Clean)**:
   - **MANDATORY**: Include ALL arguments marked `required: True`.
   - **CRITICAL**: Include ALL arguments related to INPUTS (files, directories) and OUTPUTS.
   - **IMPORTANT**: Include common configuration flags (e.g., flags for model behavior, sampling options, seeds).
   - **OMIT**: Only omit obvious debug flags or training-specific params.
3. **Consolidate Functionality**:
   - If a script has flags that change its mode (e.g., `--score_only`), expose that as a boolean argument in the tool, rather than creating a separate tool.
4. **Naming**: Ensure `tool_name` is intuitive and concise.

Return JSON list of tool definitions.
Format:
[
    {{
        "tool_name": "tool_name_snake_case",
        "script_path": "path/to/script.py",
        "description": "Action-oriented description",
        "args": [
            {{ "name": "arg_name", "type": "string", "required": true, "description": "help text", "default": "value_if_any" }}
        ]
    }}
]
"""


DOC_WRITER_PROMPT = """
Write a concise and practical User Guide (Markdown) for this MCP Server.

Repository Name: {repo_name}

Available Tools:
{tools_json}

Defined Workflows:
{workflows_json}

Your tasks:

1. **Introduction**
   - Briefly state what this MCP server does.
   - Summarize the core capabilities in 3-5 bullet points.

2. **Tool Reference**
   - For each tool, list:
     - Purpose (1-2 sentences)
     - Input schema (cleaned + minimal)
     - Output schema (cleaned + minimal)
   - Do NOT add commentary or explanation beyond what is necessary.

3. **Workflow Examples**
   - Provide 2-3 practical workflows showing how to chain the tools.
   - Each workflow should include:
     - What problem it solves
     - Step-by-step tool invocation sequence
     - Required inputs for each step
   - Keep steps short and actionable.

Guidelines:
- The final output MUST be concise, complete, and free of unnecessary explanations.
- No filler content, no motivational text, no assumptions.
- Only include information that is directly useful for an end-user trying to operate the MCP server.
- Format cleanly using Markdown.
"""


CODE_GENERATOR_PROMPT = """
You are a Python Expert. Write a COMPLETE, RUNNABLE `server.py` for an MCP Server.

Library: `mcp` (specifically `from mcp.server.fastmcp import FastMCP`)
Server Name: "{repo_name}"

TOOLS TO IMPLEMENT:
{tools_json}

REQUIREMENTS:
1. Initialize `mcp = FastMCP("{repo_name}")`.
2. Implement a special tool `get_user_guide()`:
   - Logic: Read content of "USAGE.md" in `os.path.dirname(__file__)`.
   - **CRITICAL DOCSTRING**: The docstring MUST say: "READ THIS FIRST: Contains the comprehensive user manual, workflows, and parameter explanations. Essential for understanding how to use the other tools."
   - This ensures the agent (Claude, etc.) sees it immediately when listing tools.
3. For each tool in TOOLS TO IMPLEMENT, create an `@mcp.tool()` decorated function.
   - **Function Signature**: Must reflect ALL args in the tool definition. 
   - Use Python type hints (`str`, `int`, `bool`).
   - **Defaults**: If an arg is `required: false`, give it a default value of `None` (or a sensible default if evident).
4. **Implementation Logic**:
   - Construct command: `cmd = ["python", "{script_path}"]`
   - Iterate through args. 
     - If arg is `None`, skip.
     - If bool is True, append `--flag`.
     - If list, append `--arg` multiple times or space-separated (default to multiple flags).
     - Else, append `--arg` and `str(value)`.
   - `subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())`
5. CRITICAL: Script paths are relative to repo root.

Output ONLY Python code. No markdown blocks.
"""
