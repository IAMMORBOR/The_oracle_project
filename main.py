import json
from datetime import datetime
from tqdm     import tqdm

from src.context_extractor import ContextExtractor
from src.oracle_generator  import OracleGenerator
from src.test_runner       import TestRunner
from src.database          import init_db, save_result
from config.settings       import RUNS_PER_CONFIG

CONTEXT_LEVELS = ["L1", "L2", "L3", "L4", "L5", "L6"]

def get_context(extractor, level):
    if level == "L1":
        return {"test_prefix": extractor.get_test_prefix()}
    elif level == "L2":
        p, m = extractor.get_prefix_plus_mut()
        return {"test_prefix": p, "mut": m}
    elif level == "L3":
        p, c = extractor.get_prefix_plus_cut()
        return {"test_prefix": p, "cut": c}
    elif level == "L4":
        p, t = extractor.get_prefix_plus_full_test_file()
        return {"test_prefix": p, "full_test_file": t}
    elif level == "L5":
        p, c, d = extractor.get_prefix_plus_dependencies()
        return {"test_prefix": p, "cut": c, "dependencies": d}
    elif level == "L6":
        p, c, j = extractor.get_prefix_plus_javadoc()
        return {"test_prefix": p, "cut": c, "javadoc": j}

def run_experiment():
    print("Setting up database...")
    init_db()

    print("Loading bugs...")
    with open("data/selected_bugs.json") as f:
        bugs = json.load(f)

    generator = OracleGenerator()

    for bug in tqdm(bugs, desc="Running experiments"):
        extractor = ContextExtractor(bug)

        for level in CONTEXT_LEVELS:

            try:
                context_data = get_context(extractor, level)
            except Exception as e:
                print(f"  ERROR getting context {bug['id']} {level}: {e}")
                continue

            for run in range(1, RUNS_PER_CONFIG + 1):
                print(f"\n  Bug: {bug['id']} | Level: {level} | Run: {run}")

                try:
                    oracle = generator.generate(level, context_data)
                    print(f"  Oracle: {oracle[:80]}...")

                    runner = TestRunner(
                        project    = bug["project"],
                        bug_number = bug["bug_number"]
                    )
                    eval_result = runner.run_full_check()

                    print(
                        f"  Compiled: {eval_result['compiled']} | "
                        f"Accurate: {eval_result['accurate']} | "
                        f"False Positive: {eval_result['false_positive']}"
                    )

                    save_result({
                        "bug_id":           bug["id"],
                        "context_level":    level,
                        "run_number":       run,
                        "generated_oracle": oracle,
                        "timestamp":        datetime.now().isoformat(),
                        **eval_result
                    })

                except Exception as e:
                    print(f"  ERROR on {bug['id']} {level} run {run}: {e}")
                    continue

    print("\nAll experiments complete!")
    print("Run: python3 src/reporter.py to see your results")

if __name__ == "__main__":
    run_experiment()
