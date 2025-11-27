import os
import json
import logging
from typing import List, Dict, Any, TypedDict
from .prompts import (
    WORKFLOW_ANALYST_PROMPT,
    SCHEMA_REFINER_PROMPT,
    TOOL_CRITIC_PROMPT,
    TOOL_REVISER_PROMPT,
    DOC_WRITER_PROMPT,
    CODE_GENERATOR_PROMPT,
)

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
    from langgraph.graph import StateGraph, END
except ImportError:
    raise ImportError(
        "Please install dependencies: pip install langgraph langchain-openai"
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RepoCaster.DeepAgent")


# --- 1. State Definition ---
class AgentState(TypedDict):
    repo_path: str
    repo_name: str
    ast_data: Dict[str, Any]
    readme_content: str
    example_scripts: Dict[str, str]

    # Workflow Analysis
    identified_workflows: List[Dict]

    # Tool Definitions
    refined_tools: List[Dict]

    # Reflection Loop State
    critique_feedback: str
    missing_scripts: List[str]
    iteration_count: int

    # Artifacts
    user_manual: str
    mcp_server_code: str

    # New fields for reflection
    revision_count: int
    critique_approved: bool
    missing_paths: List[str]
    user_guide: str


# --- Nodes ---
class ContextGatherer:
    """Gather Context: README + Example Scripts"""

    def __call__(self, state: AgentState) -> AgentState:
        repo_path = state["repo_path"]
        logger.info(f"🔍 [Gatherer] Scanning {repo_path} for README and examples...")

        readme = ""
        examples = {}

        # Read README
        for f in os.listdir(repo_path):
            if f.lower().startswith("readme"):
                try:
                    with open(
                        os.path.join(repo_path, f),
                        "r",
                        encoding="utf-8",
                        errors="ignore",
                    ) as file:
                        readme = file.read()
                except:
                    pass

        # Search Usage Examples (.sh, .ipynb, key .py)
        for root, dirs, files in os.walk(repo_path):
            if any(x in root for x in [".git", "__pycache__", "venv", "node_modules"]):
                continue
            for f in files:
                fp = os.path.join(root, f)
                # As long as it is a script, or a py file with run/inference in the name
                if f.endswith((".sh", ".bash", ".ipynb")) or (
                    f.endswith(".py")
                    and any(k in f for k in ["run", "infer", "example", "submit"])
                ):
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as file:
                            content = file.read()
                            if 50 < len(content) < 15000:  # Simple length filter
                                rel_name = os.path.relpath(fp, repo_path)
                                examples[rel_name] = content
                    except:
                        pass
            if len(examples) > 15:
                break

        return {
            **state,
            "readme_content": readme,
            "example_scripts": examples,
            "revision_count": 0,
            "critique_approved": False,
            "missing_paths": [],
            "user_guide": "",
        }


class WorkflowAnalyst:
    def __init__(self, model_name, base_url=None, api_key=None):
        if base_url:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                base_url=base_url,
                api_key=api_key,
                model_kwargs={"response_format": {"type": "json_object"}},
            )
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                api_key=api_key,
                model_kwargs={"response_format": {"type": "json_object"}},
            )

    def __call__(self, state: AgentState) -> AgentState:
        logger.info("🧠 [Analyst] Deducting workflows from examples & AST...")

        if not state["example_scripts"] and not state["readme_content"]:
            logger.warning("⚠️ No context found. Skipping analysis.")
            return {**state, "identified_workflows": []}

        ast_summary = json.dumps(
            [
                {
                    "name": s["name"],
                    "path": s["path"],
                    "args_count": len(s.get("args", [])),
                }
                for s in state["ast_data"].get("scripts", [])
            ],
            indent=2,
        )

        examples_text = ""
        for name, content in list(state["example_scripts"].items())[
            :10
        ]:  # Limit to top 10 examples
            examples_text += f"\n--- FILE: {name} ---\n{content[:2000]}\n"

        prompt = ChatPromptTemplate.from_template(WORKFLOW_ANALYST_PROMPT)

        chain = prompt | self.llm | JsonOutputParser()
        try:
            workflows = chain.invoke(
                {
                    "ast_summary": ast_summary,
                    "examples_text": examples_text,
                    "readme_snippet": state["readme_content"][:3000],
                }
            )

            # --- FIX: Robustness check for LLM output ---
            # LLMs sometimes wrap the list in a dict like {"workflows": [...]}
            if isinstance(workflows, dict):
                # Try to find the list inside values
                found = False
                for val in workflows.values():
                    if isinstance(val, list):
                        workflows = val
                        found = True
                        break
                if not found:
                    workflows = []  # Fallback
            elif not isinstance(workflows, list):
                workflows = []  # Fallback
            # ---------------------------------------------

            logger.info(f"🧠 [Analyst] Identified {len(workflows)} workflows.")
            return {**state, "identified_workflows": workflows}
        except Exception as e:
            logger.error(f"Analyst failed: {e}")
            return {**state, "identified_workflows": []}


class SchemaRefiner:
    def __init__(self, model_name, base_url=None, api_key=None):
        if base_url:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                base_url=base_url,
                api_key=api_key,
                model_kwargs={"response_format": {"type": "json_object"}},
            )
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                api_key=api_key,
                model_kwargs={"response_format": {"type": "json_object"}},
            )

    def __call__(self, state: AgentState) -> AgentState:
        logger.info("🔧 [Refiner] Finalizing tool definitions...")

        # --- FIX: Robust list comprehension ---
        # Ensure w is a dict before calling .get()
        workflow_paths = []
        if state["identified_workflows"] and isinstance(
            state["identified_workflows"], list
        ):
            for w in state["identified_workflows"]:
                if isinstance(w, dict):
                    path = w.get("target_script_path")
                    if path:
                        workflow_paths.append(path)
        # --------------------------------------

        # Find AST details for identified workflows
        relevant_scripts = []

        for script in state["ast_data"].get("scripts", []):
            # Heuristic matching
            # Include if it's part of the identified workflow OR looks like a main script
            if script["path"] in workflow_paths:
                relevant_scripts.append(script)
            elif any(
                w in script["name"]
                for w in [
                    "inference",
                    "run",
                    "predict",
                    "generate",
                    "parse",
                    "assign",
                    "make",
                    "prep",
                ]
            ):
                relevant_scripts.append(script)

        if not relevant_scripts:
            # Fallback: use all scripts if analyst failed
            relevant_scripts = state["ast_data"].get("scripts", [])[:5]

        prompt = ChatPromptTemplate.from_template(SCHEMA_REFINER_PROMPT)

        chain = prompt | self.llm | JsonOutputParser()
        try:
            tools = chain.invoke(
                {
                    "ast_json": json.dumps(relevant_scripts, indent=2),
                    "workflows_json": json.dumps(
                        state["identified_workflows"], indent=2
                    ),
                }
            )

            # --- FIX: Robustness check for LLM output ---
            if isinstance(tools, dict):
                for val in tools.values():
                    if isinstance(val, list):
                        tools = val
                        break
            if not isinstance(tools, list):
                tools = []
            # ---------------------------------------------

            return {**state, "refined_tools": tools}
        except Exception as e:
            logger.error(f"Refiner failed: {e}")
            return {**state, "refined_tools": []}


class ToolCritic:
    def __init__(self, model_name, base_url=None, api_key=None):
        if base_url:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                base_url=base_url,
                api_key=api_key,
                model_kwargs={"response_format": {"type": "json_object"}},
            )
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                api_key=api_key,
                model_kwargs={"response_format": {"type": "json_object"}},
            )

    def __call__(self, state: AgentState) -> AgentState:
        logger.info(
            f"🧐 [Critic] Reviewing tool coverage (Round {state['revision_count'] + 1})..."
        )

        current_tools = set()
        for t in state["refined_tools"]:
            # Robustly get the path, handling potential key variations
            if isinstance(t, dict):
                path = t.get("script_path") or t.get("path")
                if path:
                    current_tools.add(path)
            else:
                logger.warning(f"⚠️ [Critic] Skipping invalid tool definition: {t}")

        all_scripts = state["ast_data"].get("scripts", [])

        # Filter potential candidates that are NOT in current tools
        candidates = []
        for s in all_scripts:
            if s["path"] not in current_tools:
                candidates.append(s["path"])

        if not candidates:
            return {**state, "critique_approved": True}

        prompt = ChatPromptTemplate.from_template(TOOL_CRITIC_PROMPT)

        chain = prompt | self.llm | JsonOutputParser()
        try:
            result = chain.invoke(
                {
                    "tool_definitions": json.dumps(state["refined_tools"], indent=2),
                    "candidates": candidates[:50],  # Limit to avoid token overflow
                }
            )
            return {
                **state,
                "critique_approved": result.get("approved", True),
                "missing_paths": result.get("missing_paths", []),
            }
        except Exception as e:
            logger.error(f"Critic failed: {e}")
            return {**state, "critique_approved": True}


class ToolReviser:
    def __init__(self, model_name, base_url=None, api_key=None):
        if base_url:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                base_url=base_url,
                api_key=api_key,
                model_kwargs={"response_format": {"type": "json_object"}},
            )
        else:
            self.llm = ChatOpenAI(
                model=model_name,
                temperature=0,
                api_key=api_key,
                model_kwargs={"response_format": {"type": "json_object"}},
            )

    def __call__(self, state: AgentState) -> AgentState:
        logger.info(
            f"✏️ [Reviser] Adding {len(state['missing_paths'])} missing tools..."
        )

        missing_scripts = []
        for path in state["missing_paths"]:
            for s in state["ast_data"].get("scripts", []):
                if s["path"] == path:
                    missing_scripts.append(s)
                    break

        if not missing_scripts:
            return {**state, "revision_count": state["revision_count"] + 1}

        prompt = ChatPromptTemplate.from_template(TOOL_REVISER_PROMPT)

        chain = prompt | self.llm | JsonOutputParser()
        try:
            new_tools = chain.invoke(
                {"scripts_json": json.dumps(missing_scripts, indent=2)}
            )

            # Remove old versions of the tools being revised (if any)
            # This allows "updating" a tool by re-generating it
            current_tools = []
            paths_being_revised = set(state["missing_paths"])

            for t in state["refined_tools"]:
                # Robustly get path
                t_path = t.get("script_path") or t.get("path")
                if t_path not in paths_being_revised:
                    current_tools.append(t)

            updated_tools = current_tools + new_tools
            return {
                **state,
                "refined_tools": updated_tools,
                "revision_count": state["revision_count"] + 1,
            }
        except Exception as e:
            logger.error(f"Reviser failed: {e}")
            return {**state, "revision_count": state["revision_count"] + 1}


class DocWriter:
    def __init__(self, model_name, base_url=None, api_key=None):
        if base_url:
            self.llm = ChatOpenAI(
                model=model_name, temperature=0, base_url=base_url, api_key=api_key
            )
        else:
            self.llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key)

    def __call__(self, state: AgentState) -> AgentState:
        logger.info("📖 [DocWriter] Generating User Manual...")

        prompt = ChatPromptTemplate.from_template(DOC_WRITER_PROMPT)

        chain = prompt | self.llm | StrOutputParser()
        guide = chain.invoke(
            {
                "repo_name": state["repo_name"],
                "tools_json": json.dumps(state["refined_tools"], indent=2),
                "workflows_json": json.dumps(state["identified_workflows"], indent=2),
            }
        )
        return {**state, "user_guide": guide}


class CodeGenerator:
    def __init__(self, model_name, base_url=None, api_key=None):
        if base_url:
            self.llm = ChatOpenAI(
                model=model_name, temperature=0, base_url=base_url, api_key=api_key
            )
        else:
            self.llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key)

    def __call__(self, state: AgentState) -> AgentState:
        logger.info("💻 [Generator] Writing MCP Server Code...")

        # --- FIX: Code uses external USAGE.md instead of hardcoded string ---
        prompt = ChatPromptTemplate.from_template(CODE_GENERATOR_PROMPT)

        chain = prompt | self.llm | StrOutputParser()
        # We DO NOT pass user_guide content here to keep token count low
        response = chain.invoke(
            {
                "repo_name": state["repo_name"],
                "tools_json": json.dumps(state["refined_tools"], indent=2),
                "script_path": "{script_path}",  # literal for template
            }
        )

        code = response.replace("```python", "").replace("```", "").strip()
        return {**state, "mcp_server_code": code}


# --- Graph Builder ---


def should_continue_critique(state: AgentState):
    if state["critique_approved"] or state["revision_count"] >= 3:
        return "doc_writer"
    return "reviser"


class DeepRepoAgent:
    def __init__(
        self,
        repo_path: str,
        ast_result: Dict,
        model_url=None,
        model_name="gpt-5-nano",
        model_api_key=None,
    ):
        self.repo_path = repo_path
        self.repo_name = os.path.basename(repo_path)
        self.ast_result = ast_result
        self.model_name = model_name
        self.model_url = model_url
        self.model_api_key = model_api_key

        # Build Graph
        builder = StateGraph(AgentState)
        builder.add_node("gather", ContextGatherer())
        builder.add_node(
            "analyze", WorkflowAnalyst(model_name, self.model_url, self.model_api_key)
        )
        builder.add_node(
            "refine", SchemaRefiner(model_name, self.model_url, self.model_api_key)
        )
        builder.add_node(
            "critique", ToolCritic(model_name, self.model_url, self.model_api_key)
        )
        builder.add_node(
            "reviser", ToolReviser(model_name, self.model_url, self.model_api_key)
        )
        builder.add_node(
            "doc_writer", DocWriter(model_name, self.model_url, self.model_api_key)
        )
        builder.add_node(
            "generate", CodeGenerator(model_name, self.model_url, self.model_api_key)
        )

        builder.set_entry_point("gather")
        builder.add_edge("gather", "analyze")
        builder.add_edge("analyze", "refine")
        builder.add_edge("refine", "critique")

        builder.add_conditional_edges(
            "critique",
            should_continue_critique,
            {"doc_writer": "doc_writer", "reviser": "reviser"},
        )

        builder.add_edge("reviser", "critique")
        builder.add_edge("doc_writer", "generate")
        builder.add_edge("generate", END)

        self.app = builder.compile()
        try:
            self.app.get_graph().draw_mermaid_png(
                output_file_path="langgraph_visualization.png"
            )
        except Exception:
            pass

    def run(self) -> Dict[str, str]:
        initial_state = {
            "repo_path": self.repo_path,
            "repo_name": self.repo_name,
            "ast_data": self.ast_result,
            "readme_content": "",
            "example_scripts": {},
            "identified_workflows": [],
            "refined_tools": [],
            "mcp_server_code": "",
            "revision_count": 0,
            "critique_approved": False,
            "missing_paths": [],
            "user_guide": "",
        }

        result = self.app.invoke(initial_state)
        return {
            "server_code": result["mcp_server_code"],
            "user_manual": result["user_guide"],
        }
