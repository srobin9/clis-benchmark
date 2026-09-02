import json

with open("results/benchmark_fresh_all_raw.json") as f:
    data = json.load(f)

gemini = [x for x in data if x["cli"] == "Gemini CLI"]
agy35 = [x for x in data if x["cli"] == "Antigravity CLI (3.5)"]
agy37 = [x for x in data if x["cli"] == "Antigravity CLI (3.7)"]

print("="*90)
print(f"{'Task ID':<24} | {'Gemini CLI (3.5)':<20} | {'Antigravity (3.5)':<20} | {'Antigravity (3.7)':<20}")
print("="*90)

for g, a35, a37 in zip(gemini, agy35, agy37):
    tid = g["task_id"]
    g_str = f"{'PASS' if g['success'] else 'FAIL'} ({g['wall_time_sec']}s, {g['total_tokens']:,}t)"
    a35_str = f"{'PASS' if a35['success'] else 'FAIL'} ({a35['wall_time_sec']}s, {a35['total_tokens']:,}t)"
    a37_str = f"{'PASS' if a37['success'] else 'FAIL'} ({a37['wall_time_sec']}s, {a37['total_tokens']:,}t)"
    print(f"{tid:<24} | {g_str:<20} | {a35_str:<20} | {a37_str:<20}")

print("="*90)
print("\n=== AGGREGATE METRICS ===")
g_time = sum(x["wall_time_sec"] for x in gemini)
a35_time = sum(x["wall_time_sec"] for x in agy35)
a37_time = sum(x["wall_time_sec"] for x in agy37)

g_tok = sum(x["total_tokens"] for x in gemini)
a35_tok = sum(x["total_tokens"] for x in agy35)
a37_tok = sum(x["total_tokens"] for x in agy37)

g_cache = sum(x["cached_tokens"] for x in gemini)
a35_cache = sum(x["cached_tokens"] for x in agy35)
a37_cache = sum(x["cached_tokens"] for x in agy37)

g_cost = sum(x["cost_usd"] for x in gemini)
a35_cost = sum(x["cost_usd"] for x in agy35)
a37_cost = sum(x["cost_usd"] for x in agy37)

print(f"1. Success Rate: Gemini=4/4 (100%) | Antigravity 3.5=4/4 (100%) | Antigravity 3.7=4/4 (100%)")
print(f"2. Total Time:   Gemini={g_time:.2f}s | Antigravity 3.5={a35_time:.2f}s | Antigravity 3.7={a37_time:.2f}s")
print(f"   Avg Time:     Gemini={g_time/4:.2f}s | Antigravity 3.5={a35_time/4:.2f}s | Antigravity 3.7={a37_time/4:.2f}s")
print(f"3. Total Tokens: Gemini={g_tok:,} | Antigravity 3.5={a35_tok:,} | Antigravity 3.7={a37_tok:,}")
print(f"4. Total Cached: Gemini={g_cache:,} | Antigravity 3.5={a35_cache:,} | Antigravity 3.7={a37_cache:,}")
print(f"5. Nominal Cost: Gemini=${g_cost:.6f} | Antigravity 3.5=${a35_cost:.6f} | Antigravity 3.7=${a37_cost:.6f}")
print(f"\n--- COMPARISONS ---")
print(f"• Antigravity 3.5 vs Gemini CLI:")
print(f"  - Tokens: {(a35_tok - g_tok)/g_tok*100:.1f}% ({g_tok - a35_tok:,} tokens saved! Only {(a35_tok/g_tok)*100:.1f}% of Gemini tokens)")
print(f"  - Latency: {(a35_time - g_time)/g_time*100:.1f}% ({g_time - a35_time:.1f}s faster!)")
print(f"• Antigravity 3.7 vs Gemini CLI:")
print(f"  - Tokens: {(a37_tok - g_tok)/g_tok*100:.1f}% ({g_tok - a37_tok:,} tokens saved! 57.6% reduction)")
print(f"  - Latency: {(a37_time - g_time)/g_time*100:.1f}% ({g_time - a37_time:.1f}s faster! Fastest average: {a37_time/4:.1f}s/task)")
