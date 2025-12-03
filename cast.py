import sys
import os

# Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from repocaster.core import RepoCaster
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Run RepoCaster on a GitHub repository or local path."
    )
    parser.add_argument(
        "repo_input", help="GitHub repository URL or local path to the repository."
    )  # https://github.com/facebookresearch/esm
    parser.add_argument(
        "--model_name",
        default="gpt-4o",
        help="Name of the model to use (default: gpt-4o).",
    )  # deepseek-chat, qwen3-max
    parser.add_argument(
        "--model_url", default=None, help="URL for the model API (optional)."
    )  # https://api.deepseek.com, https://dashscope.aliyuncs.com/compatible-mode/v1, https://generativelanguage.googleapis.com/v1beta/openai/
    parser.add_argument(
        "--api_key",
        default="OPENAI_API_KEY",
        help="API key for the model (default: OPENAI_API_KEY env var).",
    )  # DEEPSEEK_API_KEY, QWEN_API_KEY
    parser.add_argument(
        "--langgraph_style",
        action="store_true",
        help="Generate MCP server code with LangGraph-compatible return formats.",
    )

    args = parser.parse_args()

    repo_input = args.repo_input
    model_name = args.model_name
    model_url = args.model_url
    api_key = os.environ.get(args.api_key)
    langgraph_style = args.langgraph_style

    if os.path.exists(repo_input) and os.path.isdir(repo_input):
        repo_name = os.path.basename(os.path.abspath(repo_input))
    else:
        repo_name = repo_input.split("/")[-1].replace(".git", "")

    caster = RepoCaster(
        repo_input,
        output_dir=f"./mcp_servers/{repo_name}",
        model_name=model_name,
        model_url=model_url,
        model_api_key=api_key,
        langgraph_style=langgraph_style,
    )
    caster.cast()


if __name__ == "__main__":
    # python cast.py \
    # https://github.com/facebookresearch/esm \
    # --model_name qwen3-max \
    # --model_url https://dashscope.aliyuncs.com/compatible-mode/v1 \
    # --api_key QWEN_API_KEY \
    # --langgraph_style
    main()
