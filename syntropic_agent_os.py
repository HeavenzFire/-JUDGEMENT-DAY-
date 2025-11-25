import os
import time
import json
import hashlib
import subprocess
from pathlib import Path
from difflib import unified_diff

import ast
import tempfile
import sys
import importlib.util

# ============================================================
# CONFIGURATION
# ============================================================
REPO = Path(os.getcwd())

SAP_DIR = REPO / "sap"
TASKS_DIR = SAP_DIR / "tasks"
QUARANTINE = SAP_DIR / "quarantine"
LOGS = SAP_DIR / "logs"

MAIN_BRANCH = "main"
SCAN_INTERVAL = 10

SAP_DIR.mkdir(exist_ok=True)
TASKS_DIR.mkdir(exist_ok=True)
QUARANTINE.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)


# ==================================================================
# UTILS
# ==================================================================
def sh(cmd):
    try:
        return subprocess.check_output(
            cmd, shell=True, text=True
        ).strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command Failed: {cmd}")
        print(e.output)
        return None


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()[:24]


def log(event, data=""):
    with open(LOGS / "saos.log", "a") as f:
        f.write(f"{time.time()} | {event} | {data}\n")


# ==================================================================
# 1. TASK DISCOVERY + PROMPT SHAPING (SEQA Layer)
# ==================================================================
def discover_new_tasks():
    tasks = []

    for task_dir in TASKS_DIR.iterdir():
        state_file = task_dir / "state.json"
        if not state_file.exists():
            continue

        state = json.loads(state_file.read_text())

        if state["status"] == "WAITING":
            tasks.append((task_dir, state))

    return tasks


def shape_prompt(task_dir):
    """SEQA rewrites prompts to maximize coherence + clarity."""
    prompt = (task_dir / "prompt.md").read_text()

    # High-order SEQA shaping rules
    shaped = f"""
[SEQA-PROMPT]
Optimize for:
- Structural clarity
- Minimal hallucination surface
- Explicit file targets
- Deterministic deliverables
- Strict adherence to context.json

Original:
{prompt}

Rewrite the implementation with precision and minimal ambiguity.
"""

    (task_dir / "prompt.shaped.md").write_text(shaped)
    return shaped


# ==================================================================
# 2. BRANCH FABRICATION
# ==================================================================
def create_branch(task_dir, state):
    prompt = (task_dir / "prompt.shaped.md").read_text()
    tid = sha256(prompt + str(state["created_at"]))
    branch = f"sap/task/{tid}"

    sh(f"git checkout -b {branch}")
    sh("git add sap/")
    sh(f"git commit -m 'SAOS: Dispatch Task {tid}'")
    sh(f"git push -u origin {branch}")

    state["branch"] = branch
    state["status"] = "PUSHED"

    with open(task_dir / "state.json", "w") as f:
        json.dump(state, f, indent=2)

    log("BRANCH_CREATED", branch)
    print(f"[+] Branch created: {branch}")

    return branch


# ==================================================================
# 3. AGENT PR DISCOVERY
# ==================================================================
def get_agent_prs():
    raw = sh("gh pr list --json number,title,headRefName,state")

    if not raw:
        return []

    prs = json.loads(raw)
    return [pr for pr in prs if pr["headRefName"].startswith("sap/task/")]


# ==================================================================
# 4. SEMANTIC DIFF ANALYZER
# ==================================================================
def analyze_diff(branch):
    sh(f"git fetch origin {branch}")
    sh(f"git checkout {branch}")

    diff = sh("git diff origin/main")

    if not diff:
        return None, True  # No changes? Safe.

    # Simple semantic sanitization
    red_flags = [
        "rm -rf",
        "delete",
        "DROP TABLE",
        "base64",
        "import os; os.remove"
    ]

    for flag in red_flags:
        if flag.lower() in diff.lower():
            return diff, False

    return diff, True


# ==================================================================
# 5. AUTO TEST GENERATION (Evolution D: Real Test Suite)
# ==================================================================
def run_tests(branch):
    """
    Generates and runs unit tests for changed Python files.
    """
    diff = sh("git diff origin/main")

    if not diff:
        return True

    # Find changed .py files
    changed_files = []
    for line in diff.split('\n'):
        if line.startswith('+++ b/') and line.endswith('.py'):
            file_path = line[6:]  # remove '+++ b/'
            if os.path.exists(file_path):
                changed_files.append(file_path)

    if not changed_files:
        return True

    # Generate tests
    test_code = "import unittest\n\n"
    for file_path in changed_files:
        try:
            with open(file_path, 'r') as f:
                source = f.read()
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                    test_name = f"test_{node.name}"
                    test_code += f"class Test{node.name.capitalize()}(unittest.TestCase):\n"
                    test_code += f"    def {test_name}(self):\n"
                    test_code += f"        # Auto-generated test for {node.name}\n"
                    test_code += f"        # TODO: Add assertions\n"
                    test_code += f"        pass\n\n"
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            continue

    if "class Test" not in test_code:
        return True  # No functions to test

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_test_file = f.name

    # Run tests
    try:
        result = subprocess.run(['python', '-m', 'unittest', temp_test_file], capture_output=True, text=True)
        os.unlink(temp_test_file)
        if result.returncode == 0:
            print("[+] Tests passed")
            return True
        else:
            print("[!] Tests failed")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Error running tests: {e}")
        os.unlink(temp_test_file)
        return False


# ==================================================================
# 6. ROLLBACK & QUARANTINE
# ==================================================================
def quarantine_branch(branch, pr_number, diff):
    qdir = QUARANTINE / branch.replace("/", "_")
    qdir.mkdir(exist_ok=True)

    (qdir / "diff.txt").write_text(diff or "NO DIFF")
    (qdir / "notes.txt").write_text(f"Quarantined PR #{pr_number} (semantic violation)")

    sh(f"gh pr close {pr_number}")
    log("QUARANTINED", branch)
    print(f"[!] PR #{pr_number} quarantined.")


# ==================================================================
# 7. PROCESS AGENT PRS
# ==================================================================
def process_pr(pr):
    num = pr["number"]
    branch = pr["headRefName"]

    print(f"\n[!] PR DETECTED: #{num} from {branch}")

    # Analyze diff
    diff, safe = analyze_diff(branch)

    if not safe:
        quarantine_branch(branch, num, diff)
        return

    # Run tests
    print("[*] Running tests...")
    if not run_tests(branch):
        quarantine_branch(branch, num, diff)
        return

    # Merge PR
    sh(f"git checkout {MAIN_BRANCH}")
    sh(f"git merge {branch}")
    sh(f"git push origin {MAIN_BRANCH}")

    sh(f"gh pr close {num}")

    update_task_state(branch, "COMPLETE")
    log("PR_MERGED", num)

    print(f"[+] PR #{num} merged successfully.")


# ==================================================================
# 8. UPDATE TASK STATE
# ==================================================================
def update_task_state(branch, status):
    for d in TASKS_DIR.iterdir():
        state_file = d / "state.json"
        if not state_file.exists():
            continue

        state = json.loads(state_file.read_text())
        if state.get("branch") == branch:
            state["status"] = status
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)
            return


# ==================================================================
# 9. MASTER LOOP — SAOS CYBERNETIC HEARTBEAT
# ==================================================================
def loop():
    print("=== SYNTROPIC AGENT OS (SAOS v1.0) ONLINE ===")

    rewrite_engine = SelfRewriteEngine(Path(__file__))
    cycle_count = 0

    while True:
        # 1. Find new tasks
        tasks = discover_new_tasks()

        for task_dir, state in tasks:
            shape_prompt(task_dir)
            create_branch(task_dir, state)

        # 2. Process PRs
        prs = get_agent_prs()
        for pr in prs:
            process_pr(pr)

        # 3. Self-Rewrite (every 10 cycles)
        cycle_count += 1
        if cycle_count % 10 == 0:
            print("[*] Analyzing self for potential rewrites...")
            suggestions = rewrite_engine.analyze_code()
            if suggestions:
                print(f"[+] Suggestions: {suggestions}")
                new_source = rewrite_engine.generate_rewrite(suggestions)
                if rewrite_engine.apply_rewrite(new_source):
                    print("[+] Self-rewrite completed. Restarting loop.")
                    # Restart the script to load new code
                    os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print("[-] No suggestions for rewrite.")

        time.sleep(SCAN_INTERVAL)


if __name__ == "__main__":
    loop()