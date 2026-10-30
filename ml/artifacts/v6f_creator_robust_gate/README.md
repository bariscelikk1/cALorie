# V6-F equal-creator / group-CVaR gate result

Notebook 33 completed on 2026-10-19. The returned archive
`calorie_v6f_creator_robust_gate_report.zip` had SHA-256
`1627f54698687be5624bc1a571b4a0ccf24b379c0014eb0968cf773b6bfff7ac`.
ZIP structure passed and every entry listed in `SHA256SUMS.txt` verified.

The predeclared equal-creator recipe is rejected. Its three-seed ensemble
reached 73.53% end-to-end Macro F1, 72.10% accuracy, 80.55% unknown recall,
and 67.91% supported accuracy. Notebook 31's fixed V6-F reference was 82.09%,
85.34%, 92.04%, and 82.02%, respectively. Seed-level Macro F1 was stable, so
the failure is systematic rather than one unlucky initialization.

The sampler audit explains the regression. WorkoutFitness contributed 321 of
341 source groups, and many contained only one to three windows. Giving every
group equal mass assigned about 84% of total sampler mass to the two
WorkoutFitness sources, despite their much smaller window count. Bicep-curl F1
fell from 95.40% to 15.57%; MM-Fit w13 and w18 present-class F1 fell from
90.89% to 63.57% and from 83.73% to 55.98%.

The checkpoint is not promoted. Threshold 0.65 and Notebook 31 remain the
reference. Notebook 34 is a development-only correction with square-root
creator mass, a four-times-median per-window weight cap, and a 20% group-CVaR
mixture. Because that correction was motivated by this reused internal-test
diagnostic, its test result cannot establish production generalization.
