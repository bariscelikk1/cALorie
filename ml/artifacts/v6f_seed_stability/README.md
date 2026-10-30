# V6-F three-seed stability audit

This directory preserves the unchanged Notebook 31 report returned on
2026-10-19. `SHA256SUMS.txt` verifies every original report file; the README is
repository context and is intentionally outside that original manifest.

The gate recipe was repeated with run seeds 42, 137, and 2026 while the data,
split, frozen temporal classifier, mean-probability fusion, and threshold
`0.65` remained fixed. End-to-end Macro F1 was 81.72%, 81.88%, and 81.33%
(mean 81.64%, population standard deviation 0.23 percentage points). The
predeclared mean-of-seeds ensemble reached 82.09% Macro F1, 85.34% accuracy,
and 92.04% unknown recall on the reused 1,971-window internal development
test.

The research stability gate failed. The held-out YouTube creator's mean
present-class Macro F1 was 12.06 percentage points below V6-C even though its
accuracy increased because most windows were unknown. The ensemble rejected
220 supported windows as unknown, led by lunge (88), squat (47), push-up (45),
and dumbbell row (26). This localizes the next experiment to validation-only
gate calibration; it does not authorize model promotion.

