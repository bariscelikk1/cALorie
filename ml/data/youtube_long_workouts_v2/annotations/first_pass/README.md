# First-pass visual timeline review

These timelines were produced on 2026-10-15 from 360p review copies sampled
every four seconds, with the videos' visible countdowns and movement previews
used to refine interval changes. The original 720p videos remain the source for
landmark extraction.

The rows cover both videos without gaps and separate repeated movement from
intros, rests, previews, equipment changes, and position changes. Unsupported
and compound movements remain `unknown`; they were not forced into the current
14-class ontology.

This is a real visual first pass, but not an independent adjudication. Every
row therefore keeps `use_for_training=false` and `needs_second_review=true`.
Before training, a second reviewer should inspect at least all supported-class
rows and all medium-confidence boundaries, resolve disagreements, assign each
source video to a split, and explicitly enable accepted exercise intervals.
