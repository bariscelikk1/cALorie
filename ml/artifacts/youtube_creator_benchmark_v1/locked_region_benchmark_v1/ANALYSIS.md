# Locked creator region benchmark v1 — result

Notebook 36 was run in Colab on 2026-10-22. The returned archive is preserved
unchanged as `calorie_locked_creator_region_benchmark_v1_report.zip` with outer
SHA-256 `f85531da08a989f4796e8743b53e19a2c66a85c7151fd15e21bcf263eb49594a`.
All 13 hashes listed inside `SHA256SUMS.txt` pass.

The run matches the locked contract: 36 regions, six reserved creator videos,
32 supported-exercise regions, four compound `unknown` regions, all 15 labels,
and 616 deterministic windows. Pose coverage is not the limiting factor: the
minimum region detection rate is 99.86% and the other 35 regions are 100%.

## Frozen head-to-head

| Metric | V6-C | V6-F | V6-F minus V6-C | Paired creator-bootstrap 95% interval |
| --- | ---: | ---: | ---: | ---: |
| Accuracy | 52.78% | 69.44% | +16.67 pp | +3.57 to +36.38 pp |
| 15-label Macro F1 | 44.59% | 67.11% | +22.52 pp | +0.48 to +29.27 pp |
| Supported accuracy | 53.13% | 71.88% | +18.75 pp | +3.57 to +38.10 pp |
| Unknown recall | 50.00% | 50.00% | 0.00 pp | 0.00 to 0.00 pp |
| Gate balanced accuracy | 56.25% | 60.94% | +4.69 pp | 0.00 to +9.68 pp |

V6-F wins the frozen comparison and is the preferred recognition candidate.
It is not production-ready and this decision does not authorize tuning on the
locked benchmark.

V6-F is correct on 25/36 regions versus 19/36 for V6-C. It fixes V6-C failures
on both dumbbell-row regions, the Criticalbench deadlift, jumping jack, both
lunges, and one Michelle deadlift. It regresses one Michelle lat-pulldown
region to `unknown`.

The remaining weakness is concentrated rather than random. V6-F has zero
recall on lateral raise (0/2), sit-up (0/1), squat (0/3), and tricep extension
(0/2). It recognizes only two of four true `unknown` regions and predicts
`unknown` for nine supported regions, so unknown precision is only 18.18%.
The two TIFF compound unknown regions are confidently mapped to lateral raise,
showing that the current gate does not reliably reject mixed motions.

Creator-level coverage is small and uneven (one to 13 regions per creator),
and most classes have only one to four examples. The result is valid for this
locked region-classification contract, not an estimate of continuous-video or
production accuracy.

## Decision and next development boundary

Freeze this result. Do not change labels, thresholds, fusion, or model weights
in response to these 36 predictions, and never train on these benchmark rows.
Continue development away from the benchmark with V6-F as the candidate:

1. target the gate's false-unknown problem using development-only known and
   unknown data;
2. add genuinely independent creator data for lateral raise, sit-up, squat,
   and tricep extension;
3. retain compound/mixed-motion negatives for development without copying the
   locked TIFF regions;
4. evaluate future changes on a new untouched benchmark or a separately
   completed full-timeline set, not by repeatedly consulting this result.
