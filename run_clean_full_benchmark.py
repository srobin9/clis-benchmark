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
        "env": {"PYTHONPATH": "tasks/task1_algorithm"}
    },
    {
        "id": "task2_debugging",
        "name": "Task 2: 디버깅 및 결함 수정 (UserSessionAggregator)",
        "prompt_path": "tasks/task2_debugging/prompt.txt",
        "test_cmd": "python3 -m unittest tasks/task2_debugging/test_data_pipeline.py",
        "env": {"PYTHONPATH": "tasks/task2_debugging"}
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
        "env": {"PYTHONPATH": "tasks/task4_agentic_tool_use"}
    }
]

PRICING = {
    "input_per_m": 0.075,
    "cached_per_m": 0.01875,
    "output_per_m": 0.30
}

@dataclass
class FreshRunResult:
    task_id: str
    task_name: str
    cli: str
    model: str
    success: bool
    wall_time_sec: float
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    cached_tokens: int
    total_tokens: int
    cost_usd: float
    files_changed: int
    lines_added: int
    lines_removed: int
    test_output: str

def reset_repo():
    subprocess.run(["git", "checkout", "--force", "HEAD"], check=True, capture_output=True)
    subprocess.run(["git", "clean", "-fdx", "-e", "results*", "-e", "*.py"], check=True, capture_output=True)
    # Ensure template files are in place
    subprocess.run(["cp", "tasks/.templates/task1_rate_limiter.py", "tasks/task1_algorithm/rate_limiter.py"], check=True)
    subprocess.run(["cp", "tasks/.templates/task2_data_pipeline.py", "tasks/task2_debugging/data_pipeline.py"], check=True)
    subprocess.run(["cp", "tasks/.templates/task3_order_service.py", "tasks/task3_refactoring/order_service.py"], check=True)
    subprocess.run(["cp", "tasks/.templates/task4_jwt_handler.py", "tasks/task4_agentic_tool_use/mock_project/src/auth/jwt_handler.py"], check=True)

def get_git_diff_stats():
    res = subprocess.run(["git", "diff", "--stat"], capture_output=True, text=True)
    out = res.stdout.strip()
    files_changed, added, removed = 0, 0, 0
    match = re.search(r'(\d+)\s+file[s]?\s+changed(?:,\s+(\d+)\s+insertion[s]?\(\+\))?(?:,\s+(\d+)\s+deletion[s]?\(-\))?', out)
    if match:
        files_changed = int(match.group(1) or 0)
        added = int(match.group(2) or 0)
        removed = int(match.group(3) or 0)
    return files_changed, added, removed

def parse_json_from_output(text: str) -> Optional[Dict[str, Any]]:
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = text[first_brace:last_brace+1]
        try:
            return json.loads(candidate)
        except Exception:
            pass
    return None

def run_test(cmd: str, extra_env: Dict[str, str]):
    env = os.environ.copy()
    env.update(extra_env)
    res = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
    passed = (res.returncode == 0)
    output = (res.stdout + "\n" + res.stderr).strip()
    return passed, output

def execute_gemini(task: Dict[str, Any]) -> FreshRunResult:
    reset_repo()
    prompt = open(task["prompt_path"], encoding="utf-8").read().strip()
    cmd = ["gemini", "-p", prompt, "-y", "-o", "json"]
    env = os.environ.copy()
    env["GOOGLE_CLOUD_PROJECT"] = "p-khm8-dev-svc"
    
    t0 = time.time()
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    elapsed = time.time() - t0
    
    passed, test_out = run_test(task["test_cmd"], task["env"])
    fc, la, lr = get_git_diff_stats()
    
    data = parse_json_from_output(proc.stdout)
    input_tokens, output_tokens, cached_tokens, total_tokens = 0, 0, 0, 0
    if data and "stats" in data:
        for _, m_info in data["stats"].get("models", {}).items():
            toks = m_info.get("tokens", {})
            input_tokens += toks.get("prompt", 0)
            output_tokens += toks.get("candidates", 0) + toks.get("thoughts", 0)
            cached_tokens += toks.get("cached", 0)
            total_tokens += toks.get("total", 0)
            
    cost = (max(0, input_tokens - cached_tokens) * PRICING["input_per_m"] / 1e6) + \
           (cached_tokens * PRICING["cached_per_m"] / 1e6) + \
           (output_tokens * PRICING["output_per_m"] / 1e6)
           
    return FreshRunResult(
        task_id=task["id"],
        task_name=task["name"],
        cli="Gemini CLI",
        model="gemini-3.5-flash",
        success=passed,
        wall_time_sec=round(elapsed, 2),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        thinking_tokens=0,
        cached_tokens=cached_tokens,
        total_tokens=total_tokens,
        cost_usd=round(cost, 6),
        files_changed=fc,
        lines_added=la,
        lines_removed=lr,
        test_output=test_out
    )

def execute_agy(task: Dict[str, Any], model_name: str, cli_label: str) -> FreshRunResult:
    reset_repo()
    prompt = open(task["prompt_path"], encoding="utf-8").read().strip()
    cmd = [
        "/Users/kimhakmin/.local/bin/agy",
        "-p", prompt,
        "--model", model_name,
        "--output-format", "json",
        "--project", "p-khm8-dev-svc",
        "--dangerously-skip-permissions"
    ]
    env = os.environ.copy()
    env["GOOGLE_CLOUD_PROJECT"] = "p-khm8-dev-svc"
    
    t0 = time.time()
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    elapsed = time.time() - t0
    
    passed, test_out = run_test(task["test_cmd"], task["env"])
    fc, la, lr = get_git_diff_stats()
    
    data = parse_json_from_output(proc.stdout)
    input_tokens, output_tokens, thinking_tokens, cached_tokens, total_tokens = 0, 0, 0, 0, 0
    if data and "usage" in data:
        u = data["usage"]
        input_tokens = u.get("input_tokens", 0)
        output_tokens = u.get("output_tokens", 0)
        thinking_tokens = u.get("thinking_tokens", 0)
        cached_tokens = u.get("cache_read_tokens", 0)
        total_tokens = u.get("total_tokens", 0)
        
    tot_out = output_tokens + thinking_tokens
    cost = (input_tokens * PRICING["input_per_m"] / 1e6) + \
           (cached_tokens * PRICING["cached_per_m"] / 1e6) + \
           (tot_out * PRICING["output_per_m"] / 1e6)

    return FreshRunResult(
        task_id=task["id"],
        task_name=task["name"],
        cli=cli_label,
        model=model_name,
        success=passed,
        wall_time_sec=round(elapsed, 2),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        thinking_tokens=thinking_tokens,
        cached_tokens=cached_tokens,
        total_tokens=total_tokens,
        cost_usd=round(cost, 6),
        files_changed=fc,
        lines_added=la,
        lines_removed=lr,
        test_output=test_out
    )

if __name__ == "__main__":
    os.makedirs("results", exist_ok=True)
    fresh_results = []
    
    print("================================================================", flush=True)
    print("STARTING FRESH FULL VERIFICATION BENCHMARK (REAL-TIME EXECUTION)", flush=True)
    print("================================================================", flush=True)
    
    for task in TASKS:
        print(f"\n################################################################", flush=True)
        print(f"### RUNNING: {task['name']}", flush=True)
        print(f"################################################################", flush=True)
        
        # 1. Gemini CLI
        print(f"\n  [1/3] Executing Gemini CLI (3.5 Flash)...", flush=True)
        res_g = execute_gemini(task)
        print(f"        -> Result: {'PASS' if res_g.success else 'FAIL'} | Time: {res_g.wall_time_sec}s | Tokens: {res_g.total_tokens:,} | Cost: ${res_g.cost_usd:.6f}", flush=True)
        print(f"        -> Test Output Snippet: {res_g.test_output.splitlines()[-1] if res_g.test_output else 'None'}", flush=True)
        fresh_results.append(asdict(res_g))
        
        # 2. Antigravity CLI (3.5 Flash)
        print(f"\n  [2/3] Executing Antigravity CLI (3.5 Flash Low)...", flush=True)
        res_a35 = execute_agy(task, "Gemini 3.5 Flash (Low)", "Antigravity CLI (3.5)")
        print(f"        -> Result: {'PASS' if res_a35.success else 'FAIL'} | Time: {res_a35.wall_time_sec}s | Tokens: {res_a35.total_tokens:,} | Cost: ${res_a35.cost_usd:.6f}", flush=True)
        print(f"        -> Test Output Snippet: {res_a35.test_output.splitlines()[-1] if res_a35.test_output else 'None'}", flush=True)
        fresh_results.append(asdict(res_a35))

        # 3. Antigravity CLI (3.7 Flash)
        print(f"\n  [3/3] Executing Antigravity CLI (3.7 Flash Low)...", flush=True)
        res_a37 = execute_agy(task, "Gemini 3.7 Flash (Low)", "Antigravity CLI (3.7)")
        print(f"        -> Result: {'PASS' if res_a37.success else 'FAIL'} | Time: {res_a37.wall_time_sec}s | Tokens: {res_a37.total_tokens:,} (Thinking: {res_a37.thinking_tokens}) | Cost: ${res_a37.cost_usd:.6f}", flush=True)
        print(f"        -> Test Output Snippet: {res_a37.test_output.splitlines()[-1] if res_a37.test_output else 'None'}", flush=True)
        fresh_results.append(asdict(res_a37))

    # Save to fresh JSON
    out_file = "results/benchmark_fresh_all_raw.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(fresh_results, f, indent=2, ensure_ascii=False)
        
    print(f"\n================================================================", flush=True)
    print(f"ALL TESTS COMPLETED SUCCESSFULLY! Saved to {out_file}", flush=True)
    print(f"================================================================", flush=True)
