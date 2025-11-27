import os
import shutil
import subprocess
from .analyzer import RepoAnalyzer
from .deep_agent import DeepRepoAgent  # Use the new Deep Agent


class RepoCaster:
    def __init__(
        self,
        repo_url,
        output_dir="./output_mcp",
        model_name=None,
        model_url=None,
        model_api_key=None,
    ):
        self.repo_url = repo_url
        self.output_dir = output_dir
        self.repo_name = repo_url.split("/")[-1].replace(".git", "")
        self.model_name = model_name
        self.model_url = model_url
        self.model_api_key = model_api_key

    def _clone_repo(self, target_dir):
        if os.path.exists(self.repo_url) and os.path.isdir(self.repo_url):
            print(f"📂 Copying local repo from {self.repo_url}...")
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.copytree(self.repo_url, target_dir, dirs_exist_ok=True)
        else:
            print(f"🚀 Cloning {self.repo_url}...")
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            subprocess.run(
                ["git", "clone", "--depth", "1", self.repo_url, target_dir], check=True
            )

    def cast(self):
        print(f"🔥 Starting RepoCaster for {self.repo_name}")

        # 1. Setup Directories
        os.makedirs(self.output_dir, exist_ok=True)
        repo_local_path = os.path.join(self.output_dir, "repo_source")

        # 2. Clone Code
        self._clone_repo(repo_local_path)

        # 3. AST Analysis
        print("🔍 Analyzing repository structure (AST)...")
        analyzer = RepoAnalyzer(repo_local_path)
        analysis_result = analyzer.analyze()
        print(f"   -> Found {len(analysis_result['scripts'])} CLI scripts")

        # 4. Deep Agent (Reasoning + Generation)
        print("🧠 Running Deep Repo Agent (LangGraph)...")
        server_code = ""
        try:
            agent = DeepRepoAgent(
                repo_local_path,
                analysis_result,
                model_url=self.model_url,
                model_name=self.model_name,
                model_api_key=self.model_api_key,
            )
            result = agent.run()
            server_code = result["server_code"]
            user_manual = result["user_manual"]
        except ImportError:
            print("❌ LangGraph not installed. Cannot run Deep Agent.")
            return
        except Exception as e:
            print(f"❌ Agent failed: {e}")
            import traceback

            traceback.print_exc()
            return

        # 5. Write Output Files
        print("💾 Saving MCP Server files...")

        # Write server.py
        with open(
            os.path.join(self.output_dir, "server.py"), "w", encoding="utf-8"
        ) as f:
            f.write(server_code)

        # Write USAGE.md (Critical for the get_user_guide tool)
        with open(
            os.path.join(self.output_dir, "USAGE.md"), "w", encoding="utf-8"
        ) as f:
            f.write(user_manual)

        print(f"✅ Done! MCP Server is ready at: {self.output_dir}/server.py")
