import ast
import os
import logging

logger = logging.getLogger("RepoCaster.Analyzer")


class ArgParseVisitor(ast.NodeVisitor):
    """
    AST visitor specifically for extracting argparse argument definitions.
    It does not execute code but analyzes the code structure, making it safe and fast.
    """

    def __init__(self):
        self.arguments = []
        self.description = "Auto-detected script"

    def visit_Call(self, node):
        # Detect add_argument calls
        if isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument":
            arg_info = {"name": None, "type": "string", "required": False, "help": ""}

            # Parse positional arguments (flags)
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    if arg.value.startswith("--"):
                        arg_info["name"] = arg.value.lstrip("-")
                    elif arg.value.startswith("-"):
                        # Short arguments, usually we prioritize long arguments, handle if no long arg exists
                        pass

            # Parse keyword arguments (help, type, default, required)
            for keyword in node.keywords:
                if keyword.arg == "help" and isinstance(keyword.value, ast.Constant):
                    arg_info["help"] = keyword.value.value
                elif keyword.arg == "type":
                    if isinstance(keyword.value, ast.Name):
                        if keyword.value.id == "int":
                            arg_info["type"] = "integer"
                        elif keyword.value.id == "float":
                            arg_info["type"] = "number"
                        elif keyword.value.id == "bool":
                            arg_info["type"] = "boolean"
                elif keyword.arg == "required" and isinstance(
                    keyword.value, ast.Constant
                ):
                    arg_info["required"] = keyword.value.value
                elif keyword.arg == "default":
                    # If default exists, it is not required
                    arg_info["required"] = False

            if arg_info["name"]:
                self.arguments.append(arg_info)

        self.generic_visit(node)


class FunctionVisitor(ast.NodeVisitor):
    """
    Extract top-level function signatures
    """

    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        # Ignore private functions
        if node.name.startswith("_"):
            return

        func_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "",
            "args": [],
        }

        # Simple argument extraction logic
        for arg in node.args.args:
            if arg.arg != "self":
                func_info["args"].append(
                    {
                        "name": arg.arg,
                        "type": "string",  # Default string, can be enhanced via type hints
                    }
                )

        self.functions.append(func_info)
        self.generic_visit(node)


class RepoAnalyzer:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def analyze(self):
        results = {"scripts": [], "library": []}  # CLI scripts  # Python API functions

        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.repo_path)

                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read(), filename=full_path)

                        # 1. Check for argparse (CLI script characteristics)
                        # Simple heuristic: check if file content contains 'argparse' and '__main__'
                        with open(full_path, "r", encoding="utf-8") as f_txt:
                            content = f_txt.read()

                        if "argparse" in content and "__main__" in content:
                            visitor = ArgParseVisitor()
                            visitor.visit(tree)
                            if visitor.arguments:
                                results["scripts"].append(
                                    {
                                        "path": rel_path,
                                        "name": os.path.splitext(file)[0],
                                        "type": "cli",
                                        "args": visitor.arguments,
                                        "description": f"CLI execution of {file}",
                                    }
                                )

                        # 2. Check top-level functions (Library characteristics)
                        # Exclude files that are usually scripts, focus on utils, models, etc.
                        if "utils" in file or "model" in file or "api" in file:
                            func_visitor = FunctionVisitor()
                            func_visitor.visit(tree)
                            if func_visitor.functions:
                                results["library"].append(
                                    {
                                        "path": rel_path,
                                        "module": rel_path.replace("/", ".").replace(
                                            ".py", ""
                                        ),
                                        "functions": func_visitor.functions,
                                    }
                                )

                    except Exception as e:
                        logger.warning(f"Failed to parse {rel_path}: {e}")

        return results
