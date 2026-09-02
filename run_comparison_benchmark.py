import json
import os
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

TASKS = [
    {
        "id": "task1_algorithm",
        "name": "Task 1: 알고리즘 구현 (SlidingWindowRateLimiter)",
        "prompt_path": "tasks/task1_algorithm/prompt.txt",
        "test_cmd": "python3 -m unittest tasks/task1_algorithm/test_rate_limiter.py",
        "env": {}
    },
    {
        "id": "task2_debugging",
        "name": "Task 2: 디버깅 및 결함 수정 (UserSessionAggregator)",
        "prompt_path": "tasks/task2_debugging/prompt.txt",
        "test_cmd": "python3 -m unittest tasks/task2_debugging/test_data_pipeline.py",
        "env": {}
    },
    {
        "id": "task3_refactoring",
        "name": "Task 3: 전략 패턴 리팩토링 (OrderProcessor)",
        "prompt_path": "tasks/task3_refactoring/prompt.txt",
        "test_cmd": "python3 -m unittest tasks/task3_refactoring/test_order_service.py",
        "env": {"PYTHONPATH": "tasks/task3_refactoring"}
    },
    {
        "id": "task4_agentic_tool_use",
        "name": "Task 4: 다중 파일 도구 활용 (JWT Token Auth Flow)",
        "prompt_path": "tasks/task4_agentic_tool_use/prompt.txt",
        "test_cmd": "python3 -m unittest tasks/task4_agentic_tool_use/test_auth_flow.py",
        "env": {}
    }
]

PRICING = {
    "input_per_m": 0.075,
    "cached_per_m": 0.01875,
    "output_per_m": 0.30
}

@dataclass
class RunResult:
    task_id: str
    task_name: str
    cli: str
    model: str
    success: bool
    wall_time_sec: float
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    total_tokens: int
    cost_usd: float
    files_changed: int
    lines_added: int
    lines_removed: int
    error_summary: Optional[str] = None

def reset_repo():
    subprocess.run(["git", "checkout", "--force", "HEAD"], check=True, capture_output=True)
    subprocess.run(["git", "clean", "-fdx", "-e", "results*", "-e", "*.py"], check=True, capture_output=True)

def get_git_diff_stats():
    res = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True)
    out = res.stdout.strip()
    files_changed, added, removed = 0, 0, 0
    # e.g., " 1 file changed, 10 insertions(+), 2 deletions(-)"
    match = re.search(r'(\d+)\s+file[s]?\s+changed(?:,\s+(\d+)\s+insertion[s]?\(\+\))?(?:,\s+(\d+)\s+deletion[s]?\(-\))?', out)
    if match:
        files_changed = int(match.group(1) or 0)
        added = int(match.group(2) or 0)
        removed = int(match.group(3) or 0)
    return files_changed, added, removed

def parse_json_from_output(text: str) -> Optional[Dict[str, Any]]:
    # Search for JSON substring
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace:last_brace+1]
        try:
            return json.loads(candidate)
        except Exception:
            pass
    return None

def run_test(cmd: str, extra_env: Dict[str, str]) -> bool:
    env = os.environ.copy()
    env.update(extra_env)
    res = subprocess.run(cmd, shell=True, env=env, capture_output=True)
    return res.returncode == 0

def run_gemini(task: Dict[str, Any]) -> RunResult:
    reset_repo()
    prompt = open(task["prompt_path"], encoding="utf-8").read().strip()
    
    cmd = ["gemini", "-p", prompt, "-y", "-o", "json"]
    env = os.environ.copy()
    env["GOOGLE_CLOUD_PROJECT"] = "p-khm8-dev-svc"
    
    start_time = time.time()
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    elapsed = time.time() - start_time
    
    # Evaluate
    success = run_test(task["test_cmd"], task["env"])
    files_c, lines_a, lines_r = get_git_diff_stats()
    
    # Parse tokens
    data = parse_json_from_output(proc.stdout)
    input_tokens = 0
    output_tokens = 0
    cached_tokens = 0
    total_tokens = 0
    
    if data and "stats" in data:
        stats = data["stats"]
        models_stat = stats.get("models", {})
        for m_name, m_info in models_stat.items():
            toks = m_info.get("tokens", {})
            input_tokens += toks.get("prompt", 0)
            output_tokens += toks.get("candidates", 0) + toks.get("thoughts", 0)
            cached_tokens += toks.get("cached", 0)
            total_tokens += toks.get("total", 0)
            
    cost = ((input_tokens - cached_tokens) * PRICING["input_per_m"] / 1_000_000) + \
           (cached_tokens * PRICING["cached_per_m"] / 1_000_000) + \
           (output_tokens * PRICING["output_per_m"] / 1_000_000)
           
    return RunResult(
        task_id=task["id"],
        task_name=task["name"],
        cli="Gemini CLI",
        model="gemini-3.5-flash",
        success=success,
        wall_time_sec=round(elapsed, 2),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        total_tokens=total_tokens,
        cost_usd=round(cost, 6),
        files_changed=files_c,
        lines_added=lines_a,
        lines_removed=lines_r,
        error_summary=None if success else "Unit test assertions failed"
    )

def run_antigravity(task: Dict[str, Any]) -> RunResult:
    reset_repo()
    prompt = open(task["prompt_path"], encoding="utf-8").read().strip()
    
    cmd = [
        "/Users/kimhakmin/.local/bin/agy",
        "-p", prompt,
        "--model", "Gemini 3.5 Flash (Low)",
        "--output-format", "json",
        "--project", "p-khm8-dev-svc",
        "--dangerously-skip-permissions"
    ]
    env = os.environ.copy()
    env["GOOGLE_CLOUD_PROJECT"] = "p-khm8-dev-svc"
    
    start_time = time.time()
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    elapsed = time.time() - start_time
    
    # Evaluate
    success = run_test(task["test_cmd"], task["env"])
    files_c, lines_a, lines_r = get_git_diff_stats()
    
    data = parse_json_from_output(proc.stdout)
    input_tokens = 0
    output_tokens = 0
    cached_tokens = 0
    total_tokens = 0
    
    if data and "usage" in data:
        usage = data["usage"]
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0) + usage.get("thinking_tokens", 0)
        cached_tokens = usage.get("cache_read_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        
    cost = ((input_tokens - cached_tokens) * PRICING["input_per_m"] / 1_000_000) + \
           (cached_tokens * PRICING["cached_per_m"] / 1_000_000) + \
           (output_tokens * PRICING["output_per_m"] / 1_000_000)

    return RunResult(
        task_id=task["id"],
        task_name=task["name"],
        cli="Antigravity CLI",
        model="Gemini 3.5 Flash (Low)",
        success=success,
        wall_time_sec=round(elapsed, 2),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        total_tokens=total_tokens,
        cost_usd=round(cost, 6),
        files_changed=files_c,
        lines_added=lines_a,
        lines_removed=lines_r,
        error_summary=None if success else "Unit test assertions failed"
    )

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    all_results = []
    print("=== STARTING CLI COMPARISON BENCHMARK ===")
    
    for task in TASKS:
        print(f"\n>>> Running: {task['name']}")
        
        print("  [1/2] Executing Gemini CLI...")
        res_g = run_gemini(task)
        print(f"        Success: {res_g.success} | Time: {res_g.wall_time_sec}s | Tokens: {res_g.total_tokens} | Cost: ${res_g.cost_usd}")
        all_results.append(asdict(res_g))
        
        print("  [2/2] Executing Antigravity CLI...")
        res_a = run_antigravity(task)
        print(f"        Success: {res_a.success} | Time: {res_a.wall_time_sec}s | Tokens: {res_a.total_tokens} | Cost: ${res_a.cost_usd}")
        all_results.append(asdict(res_a))

    with open("results/benchmark_comparison_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
        
    print("\n=== BENCHMARK COMPLETE. Results saved to results/benchmark_comparison_raw.json ===")
