# cALorie experiment backbone

This sequence is the fixed post-v5 development order. Do not silently combine
later stages with earlier ones. Every model comparison uses the V6-A group
split, seed, report schema, and evaluation protocol.

| Order | Experiment | Change | Status |
| ---: | --- | --- | --- |
| 1a | V6-A | Fully equal class -> source group -> window sampling plus Notebook 13 hard-positive weights | Completed; rejected because equal group mass hurt generalization |
| 1b | V6-A.1 | Class-balanced sampling with square-root-tempered group mass plus the same hard-positive weights | Completed; recovered V6-A regression and retained as sampling base |
| 2 | V6-B | V6-A.1 plus train-only flip, rotation, speed, frame-drop, and coordinate-noise augmentation | Completed; accepted as augmentation base |
| 3 | V6-C | V6-B plus velocity, bone-vector, and joint-angle features | Completed; retained as gate/feature candidate |
| 4 | Calibration | Select and calibrate the gate threshold on a separate creator/person-separated validation set | Notebook 17 ready; provisional creator evidence requires timeline spot-check |
| 5 | Dense decoder | Denser inference, hysteresis, minimum action duration, and short-gap merging | Planned |
| 6 | G1 | Small ST-GCN comparison on the identical split | Planned |
| 7 | Multi-scale/refinement | If still justified, compare 32/64/128-frame TCN branches and MS-TCN-style smoothing | Conditional |

The active recognition target contains 14 dynamic exercises. `plank` is retired
after v5 and maps to `unknown` in every new experiment. `unknown` supports
rejection of rest, transitions, unsupported movement, and retired plank data;
it is not the product's central output.

The product path remains:

1. recognize the exercise on a long mixed video timeline;
2. stabilize adjacent predictions into action segments;
3. count complete repetitions with exercise-specific phase logic;
4. estimate calories from recognized exercise, repetitions, duration, and user
   inputs;
5. run the complete pipeline in a simple local Python application.

## Experiment rules

- Change only the block named by the current experiment.
- Split by original person/creator/source group before augmentation.
- Never use the locked external test to choose a threshold or hyperparameter.
- Report Macro F1 and per-class recall; accuracy alone cannot promote a model.
- Save split assignments, sampler diagnostics, configuration, checkpoint,
  learning curves, confusion matrices, and window predictions in every report.
- Keep historical v1-v5 artifacts immutable.
- A failed controlled experiment remains archived and is never silently used as
  the base for the next stage.
