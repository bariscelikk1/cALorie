# V2 design research

The V2 interface was informed by a short review of open-source fitness and
timeline interfaces. We used the references for interaction ideas only; no
source code or branded assets were copied.

- [shadcn-timeline](https://github.com/timDeHof/shadcn-timeline): compact,
  scannable event/timeline treatment.
- [ReUI](https://github.com/MagnanGG/reui-app): restrained component surfaces
  and typography hierarchy.
- [Tracky](https://github.com/fraineralex/tracky) and
  [Stable](https://github.com/trevorpfiz/stable): workout-progress patterns
  and data-first dashboards.
- [Fitness Dashboard Next.js](https://github.com/shay122990/fitness-dashboard-nextjs):
  exercise summary and metric grouping references.

The resulting UI intentionally avoids generic AI chat patterns: one primary
video surface, thin separators, compact controls, explicit activity labels, and
an explainable timeline. The classifier and segmentation logic are heuristic
and should be calibrated against labeled videos before making health claims.
