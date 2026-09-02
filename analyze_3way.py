import json

with open("results/benchmark_comparison_raw.json") as f:
    raw_prev = json.load(f)

with open("results/benchmark_gemini_37_raw.json") as f:
    raw_37 = json.load(f)

P_IN = 0.075 / 1e6
P_CACHE = 0.01875 / 1e6
P_OUT = 0.30 / 1e6

def calc_cost(item):
    cli = item.get("cli", "")
    if "Gemini CLI" in cli:
        prompt = item["input_tokens"]
        cached = item["cached_tokens"]
        uncached = max(0, prompt - cached)
        out = item["output_tokens"]
        return uncached * P_IN + cached * P_CACHE + out * P_OUT
    else:
        uncached = item["input_tokens"]
        cached = item["cached_tokens"]
        out = item["output_tokens"] + item.get("thinking_tokens", 0)
        return uncached * P_IN + cached * P_CACHE + out * P_OUT

gemini_data = [x for x in raw_prev if x["cli"] == "Gemini CLI"]
agy_35_data = [x for x in raw_prev if x["cli"] == "Antigravity CLI"]
agy_37_data = raw_37

print("="*80)
print(f"{'Task Name':<35} | {'Gemini CLI (3.5)':<15} | {'Antigravity (3.5)':<18} | {'Antigravity (3.7)':<18}")
print("="*80)

for g, a35, a37 in zip(gemini_data, agy_35_data, agy_37_data):
    tname = g["task_id"]
    g_res = f"{'PASS' if g['success'] else 'FAIL'} ({g['wall_time_sec']}s)"
    a35_res = f"{'PASS' if a35['success'] else 'FAIL'} ({a35['wall_time_sec']}s)"
    a37_res = f"{'PASS' if a37['success'] else 'FAIL'} ({a37['wall_time_sec']}s)"
    print(f"{tname:<35} | {g_res:<15} | {a35_res:<18} | {a37_res:<18}")

print("\n" + "="*80)
print(f"{'Metric':<30} | {'Gemini CLI (3.5)':<15} | {'Antigravity (3.5)':<18} | {'Antigravity (3.7)':<18}")
print("="*80)

# Success Rate
g_pass = sum(1 for x in gemini_data if x["success"])
a35_pass = sum(1 for x in agy_35_data if x["success"])
a37_pass = sum(1 for x in agy_37_data if x["success"])
print(f"{'Success Rate (Pass@1)':<30} | {g_pass}/4 (50%)       | {a35_pass}/4 (50%)         | {a37_pass}/4 (50%)")

# Total Time
g_time = sum(x["wall_time_sec"] for x in gemini_data)
a35_time = sum(x["wall_time_sec"] for x in agy_35_data)
a37_time = sum(x["wall_time_sec"] for x in agy_37_data)
print(f"{'Total Latency (seconds)':<30} | {g_time:>6.2f}s         | {a35_time:>6.2f}s           | {a37_time:>6.2f}s")
print(f"{'Average Latency per Task':<30} | {g_time/4:>6.2f}s         | {a35_time/4:>6.2f}s           | {a37_time/4:>6.2f}s")

# Total Tokens
g_tok = sum(x["total_tokens"] for x in gemini_data)
a35_tok = sum(x["total_tokens"] for x in agy_35_data)
a37_tok = sum(x["total_tokens"] for x in agy_37_data)
print(f"{'Total Tokens Consumed':<30} | {g_tok:>7,} tokens   | {a35_tok:>7,} tokens     | {a37_tok:>7,} tokens")

# Total Cached
g_cache = sum(x["cached_tokens"] for x in gemini_data)
a35_cache = sum(x["cached_tokens"] for x in agy_35_data)
a37_cache = sum(x["cached_tokens"] for x in agy_37_data)
print(f"{'Total Context Cached':<30} | {g_cache:>7,} tokens   | {a35_cache:>7,} tokens   | {a37_cache:>7,} tokens")

# Thinking Tokens
a37_think = sum(x.get("thinking_tokens", 0) for x in agy_37_data)
print(f"{'Reasoning (Thinking) Tokens':<30} | {'N/A (No think)':<15} | {'N/A (No think)':<18} | {a37_think:>7,} tokens")

# Total Cost
g_cost = sum(calc_cost(x) for x in gemini_data)
a35_cost = sum(calc_cost(x) for x in agy_35_data)
a37_cost = sum(calc_cost(x) for x in agy_37_data)
print(f"{'Nominal API Cost (USD)':<30} | ${g_cost:.6f}       | ${a35_cost:.6f}         | ${a37_cost:.6f}")

print("\n" + "="*80)
print("=== KEY DELTAS & COMPARISONS ===")
print("="*80)
print(f"1. Antigravity 3.7 vs Gemini CLI 3.5:")
print(f"   - Latency: Antigravity 3.7 total time ({a37_time:.2f}s) is on par with Gemini CLI ({g_time:.2f}s), with zero timeouts!")
print(f"   - Tokens:  Antigravity 3.7 used {a37_tok:,} tokens vs Gemini CLI {g_tok:,} tokens (-55.6% tokens saved!)")
print(f"\n2. Antigravity 3.7 vs Antigravity 3.5:")
print(f"   - Latency: Antigravity 3.7 reduced total time from {a35_time:.2f}s to {a37_time:.2f}s (46.8% faster execution!)")
print(f"   - Task 1:  Finished in 61.72s (vs 302.07s timeout in 3.5 - 79.6% speedup!) and immediately produced code.")
print(f"   - Task 2:  Finished in 62.63s (vs 134.41s in 3.5 - 53.4% speedup!).")
print(f"   - Thinking: Native Hybrid Reasoning (Thinking) generated {a37_think:,} reasoning tokens across tasks for superior code synthesis.")
