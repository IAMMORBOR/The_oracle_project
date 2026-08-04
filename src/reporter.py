import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from config.settings import RESULTS_DB

def generate_report():
    """Read results from DB and produce summary + chart"""

    # Load results from database
    conn    = sqlite3.connect(RESULTS_DB)
    df      = pd.read_sql("SELECT * FROM results", conn)
    conn.close()

    # Calculate averages per context level
    summary = df.groupby("context_level").agg(
        compilation_rate   = ("compiled",       "mean"),
        accuracy           = ("accurate",       "mean"),
        bug_detection_rate = ("catches_bug",    "mean"),
        false_positive_rate= ("false_positive", "mean"),
    ).reset_index()

    # Convert to percentages
    for col in ["compilation_rate", "accuracy",
                "bug_detection_rate", "false_positive_rate"]:
        summary[col] = (summary[col] * 100).round(2)

    # Print to terminal
    print("\n========== RESULTS SUMMARY ==========")
    print(summary.to_string(index=False))
    print("=====================================\n")

    # Save as CSV
    summary.to_csv("results/summary.csv", index=False)
    print("CSV saved to results/summary.csv")

    # Create bar charts
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Effect of Code Context on LLM Oracle Quality", fontsize=14)

    axes[0].bar(
        summary["context_level"],
        summary["compilation_rate"],
        color="#028090"
    )
    axes[0].set_title("Compilation Rate (%)")
    axes[0].set_xlabel("Context Level")
    axes[0].set_ylabel("Rate (%)")
    axes[0].set_ylim(0, 100)

    axes[1].bar(
        summary["context_level"],
        summary["accuracy"],
        color="#1E2761"
    )
    axes[1].set_title("Accuracy (%)")
    axes[1].set_xlabel("Context Level")
    axes[1].set_ylabel("Accuracy (%)")
    axes[1].set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig("results/results_chart.png")
    print("Chart saved to results/results_chart.png")

if __name__ == "__main__":
    generate_report()