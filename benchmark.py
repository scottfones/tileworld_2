"""benchmark.py: Run the project multiple times and calculate statistics."""

import argparse
import re
import statistics
import subprocess

parser = argparse.ArgumentParser(
    description="stats for your tileworld runs",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("-r", "--runs", type=int, default=10)
args = parser.parse_args()

p1_scores: list[int] = []
p2_scores: list[int] = []

for run_num in range(args.runs):
    print(f"Run {run_num + 1} of {args.runs}:")

    run_cap = subprocess.run(["python", "main.py"], capture_output=True, text=True, check=True)

    score1_re = re.compile(r"Score of Player 1: (-?\d*)")
    if p1_search_tmp := score1_re.search(run_cap.stdout):
        if p1_score_tmp := p1_search_tmp.group(1):
            p1_scores.append(int(p1_score_tmp))
    else:
        raise Exception("Could not find Player 1 score")

    score2_re = re.compile(r"Score of Player 2: (-?\d*)")
    if p2_search_tmp := score2_re.search(run_cap.stdout):
        if p2_score_tmp := p2_search_tmp.group(1):
            p2_scores.append(int(p2_score_tmp))
    else:
        raise Exception("Could not find Player 2 score")

    print(f"  Player 1: {p1_scores[-1]}")
    print(f"  Player 2: {p2_scores[-1]}")


print("\nSummary:")

print("Player 1 Scores:")
print(f"  Scores: {p1_scores}")
print(f"  Sorted: {sorted(p1_scores)}")
print(f"  Mean: {statistics.mean(p1_scores)}")
print(f"  Median: {statistics.median(p1_scores)}")
print(f"  Std Dev: {statistics.stdev(p1_scores):.2f}")

print("Player 2 Scores:")
print(f"  Scores: {p2_scores}")
print(f"  Sorted: {sorted(p2_scores)}")
print(f"  Mean: {statistics.mean(p2_scores)}")
print(f"  Median: {statistics.median(p2_scores)}")
print(f"  Std Dev: {statistics.stdev(p2_scores):.2f}")
