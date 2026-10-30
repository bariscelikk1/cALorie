# Evaluation

Record consented videos and place them in `examples/videos/`. Update
`manifest.csv` with manual counts and player-reported durations. Then run:

```bash
python evaluation/run_evaluation.py
```

`results.csv` records count error, duration error, valid-pose ratio, calorie
estimate, runtime and failures. Failed rows document real limitations.
