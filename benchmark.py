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

p1_scores = []
p2_scores = []
t_scores = []

for run_num in range(args.runs):
    print(f"Run {run_num + 1} of {args.runs}:")

    run_cap = subprocess.run(["python", "main.py"], capture_output=True, text=True)

    score1_re = re.compile("Score of Player 1: (-?\d*)")
    p1_scores.append(int(score1_re.search(run_cap.stdout).groups()[0]))

    score2_re = re.compile("Score of Player 2: (-?\d*)")
    p2_scores.append(int(score2_re.search(run_cap.stdout).groups()[0]))

    total_re = re.compile("Total Score: (-?\d*)")
    t_scores.append(int(total_re.search(run_cap.stdout).groups()[0]))

    print(f"  Player 1: {p1_scores[-1]}")
    print(f"  Player 2: {p2_scores[-1]}")
    print(f"  Total: {t_scores[-1]}")


print("\nSummary:")

print(f"Player 1 Scores:")
print(f"  Scores: {p1_scores}")
print(f"  Sorted: {sorted(p1_scores)}")
print(f"  Mean: {statistics.mean(p1_scores)}")
print(f"  Median: {statistics.median(p1_scores)}")
print(f"  Std Dev: {statistics.stdev(p1_scores):.2f}")

print(f"Player 2 Scores:")
print(f"  Scores: {p2_scores}")
print(f"  Sorted: {sorted(p2_scores)}")
print(f"  Mean: {statistics.mean(p2_scores)}")
print(f"  Median: {statistics.median(p2_scores)}")
print(f"  Std Dev: {statistics.stdev(p2_scores):.2f}")

print(f"Total Scores:")
print(f"  Scores: {t_scores}")
print(f"  Sorted: {sorted(t_scores)}")
print(f"  Mean: {statistics.mean(t_scores)}")
print(f"  Median: {statistics.median(t_scores)}")
print(f"  Std Dev: {statistics.stdev(t_scores):.2f}")
