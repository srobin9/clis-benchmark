import json
import os
import subprocess
import time
from dataclasses import asdict, dataclass
from typing import Dict, Optional


@dataclass
class BenchmarkResult:
    task_id: str
    cli_name: str
    iteration: int
    success: bool
    execution_time_sec: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    error_message: Optional[str] = None


class BenchmarkRunner:

    def __init__(self, workspace_path: str, results_dir: str = "results"):
        self.workspace_path = workspace_path
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)

    def reset_git_state(self):
        """Clean working directory to guarantee equal starting conditions."""
        subprocess.run(
            ["git", "checkout", "--force"],
            cwd=self.workspace_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "clean", "-fdx"],
            cwd=self.workspace_path,
            check=True,
            capture_output=True,
        )

    def run_eval_test(self, test_cmd: str) -> bool:
        """Run project verification test suite (e.g., pytest, npm test)."""
        proc = subprocess.run(
            test_cmd, shell=True, cwd=self.workspace_path, capture_output=True
        )
        return proc.returncode == 0

    def execute_cli_task(
        self,
        cli_name: str,
        cli_cmd: str,
        prompt: str,
        task_id: str,
        test_cmd: str,
        iteration: int,
        pricing: Dict[str, float],
    ) -> BenchmarkResult:
        """Executes a single benchmark task with the target CLI and records metrics."""
        self.reset_git_state()

        start_time = time.time()
        # Launch CLI with prompt
        full_command = f'{cli_cmd} "{prompt}"'
        proc = subprocess.run(
            full_command, shell=True, cwd=self.workspace_path, capture_output=True, text=True
        )
        elapsed_time = time.time() - start_time

        # Validate task resolution
        passed = self.run_eval_test(test_cmd)

        # Parse token metrics (Customized according to CLI log/output format)
        input_tokens = 0
        output_tokens = 0
        total_tokens = input_tokens + output_tokens

        cost = (input_tokens * pricing.get("input_per_m", 0.0) / 1_000_000) + (
            output_tokens * pricing.get("output_per_m", 0.0) / 1_000_000
        )

        result = BenchmarkResult(
            task_id=task_id,
            cli_name=cli_name,
            iteration=iteration,
            success=passed,
            execution_time_sec=round(elapsed_time, 2),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=round(cost, 5),
            error_message=None if passed else proc.stderr[-500:],
        )

        # Save result
        out_file = os.path.join(
            self.results_dir, f"{task_id}_{cli_name}_iter{iteration}.json"
        )
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(asdict(result), f, indent=2, ensure_ascii=False)

        return result
