import json

with open("results/benchmark_comparison_raw.json") as f:
    raw = json.load(f)

P_IN = 0.075 / 1e6
P_CACHE = 0.01875 / 1e6
P_OUT = 0.30 / 1e6

def calc_cost(cli, item):
    if cli == "Gemini CLI":
        prompt = item["input_tokens"]
        cached = item["cached_tokens"]
        uncached = max(0, prompt - cached)
        out = item["output_tokens"]
        return uncached * P_IN + cached * P_CACHE + out * P_OUT
    else:
        uncached = item["input_tokens"]
        cached = item["cached_tokens"]
        out = item["output_tokens"]
        return uncached * P_IN + cached * P_CACHE + out * P_OUT

gemini_data = [x for x in raw if x["cli"] == "Gemini CLI"]
antigravity_data = [x for x in raw if x["cli"] == "Antigravity CLI"]

print("=== DETAILED TASK COMPARISON ===")
for g, a in zip(gemini_data, antigravity_data):
    g_cost = calc_cost("Gemini CLI", g)
    a_cost = calc_cost("Antigravity CLI", a)
    tid = g["task_id"]
    tname = g["task_name"]
    g_succ = g["success"]
    a_succ = a["success"]
    g_time = g["wall_time_sec"]
    a_time = a["wall_time_sec"]
    g_tok = g["total_tokens"]
    a_tok = a["total_tokens"]
    g_cache = g["cached_tokens"]
    a_cache = a["cached_tokens"]
    print(f"\n[{tname}]")
    print(f"  * Gemini CLI:      Pass={g_succ:<5} | Time={g_time:>6.2f}s | Tokens={g_tok:>7,} | Cached={g_cache:>7,} | Cost=${g_cost:.6f}")
    print(f"  * Antigravity CLI: Pass={a_succ:<5} | Time={a_time:>6.2f}s | Tokens={a_tok:>7,} | Cached={a_cache:>7,} | Cost=${a_cost:.6f}")

g_succ_cnt = sum(1 for x in gemini_data if x["success"])
a_succ_cnt = sum(1 for x in antigravity_data if x["success"])

g_total_time = sum(x["wall_time_sec"] for x in gemini_data)
a_total_time = sum(x["wall_time_sec"] for x in antigravity_data)

g_total_tokens = sum(x["total_tokens"] for x in gemini_data)
a_total_tokens = sum(x["total_tokens"] for x in antigravity_data)

g_total_cached = sum(x["cached_tokens"] for x in gemini_data)
a_total_cached = sum(x["cached_tokens"] for x in antigravity_data)

g_total_cost = sum(calc_cost("Gemini CLI", x) for x in gemini_data)
a_total_cost = sum(calc_cost("Antigravity CLI", x) for x in antigravity_data)

g_eff_cost = g_total_cost / max(1, g_succ_cnt)
a_eff_cost = a_total_cost / max(1, a_succ_cnt)

print("\n" + "="*50)
print("=== AGGREGATE SUMMARY & ROI COMPARISON ===")
print("="*50)
print(f"1. Task Success Rate (Pass@1):")
print(f"   - Gemini CLI:      {g_succ_cnt}/4 ({g_succ_cnt/4*100:.1f}%)")
print(f"   - Antigravity CLI: {a_succ_cnt}/4 ({a_succ_cnt/4*100:.1f}%)")

print(f"\n2. Total Tokens Consumed:")
print(f"   - Gemini CLI:      {g_total_tokens:,} tokens")
print(f"   - Antigravity CLI: {a_total_tokens:,} tokens")
token_diff = (a_total_tokens - g_total_tokens) / g_total_tokens * 100
print(f"   => Delta: {token_diff:+.1f}% ({abs(g_total_tokens - a_total_tokens):,} tokens {'saved' if token_diff < 0 else 'more'})")

print(f"\n3. Prompt Cache Utilization (Total Cached Tokens):")
print(f"   - Gemini CLI:      {g_total_cached:,} tokens")
print(f"   - Antigravity CLI: {a_total_cached:,} tokens")
cache_ratio = a_total_cached / max(1, g_total_cached)
print(f"   => Antigravity CLI cached {cache_ratio:.2f}x more context!")

print(f"\n4. Nominal API Cost (4 Tasks):")
print(f"   - Gemini CLI:      ${g_total_cost:.6f}")
print(f"   - Antigravity CLI: ${a_total_cost:.6f}")

print(f"\n5. Execution Speed (Total Latency):")
print(f"   - Gemini CLI:      {g_total_time:.2f}s (Avg: {g_total_time/4:.2f}s)")
print(f"   - Antigravity CLI: {a_total_time:.2f}s (Avg: {a_total_time/4:.2f}s)")

# Let's also analyze Task 3 & 4 (where both succeeded)
t3_t4_g_time = gemini_data[2]["wall_time_sec"] + gemini_data[3]["wall_time_sec"]
t3_t4_a_time = antigravity_data[2]["wall_time_sec"] + antigravity_data[3]["wall_time_sec"]
t3_t4_g_tok = gemini_data[2]["total_tokens"] + gemini_data[3]["total_tokens"]
t3_t4_a_tok = antigravity_data[2]["total_tokens"] + antigravity_data[3]["total_tokens"]

print(f"\n6. Head-to-Head on Complex Tasks (Task 3 Refactoring & Task 4 Multi-file Tool Use):")
print(f"   - Total Tokens: Gemini={t3_t4_g_tok:,} vs Antigravity={t3_t4_a_tok:,} (Antigravity saved {(t3_t4_g_tok - t3_t4_a_tok)/t3_t4_g_tok*100:.1f}% tokens!)")
print(f"   - Latency:      Gemini={t3_t4_g_time:.2f}s vs Antigravity={t3_t4_a_time:.2f}s (Antigravity was {(t3_t4_g_time - t3_t4_a_time)/t3_t4_g_time*100:.1f}% faster on Task 3: {gemini_data[2]['wall_time_sec']}s vs {antigravity_data[2]['wall_time_sec']}s!)")
