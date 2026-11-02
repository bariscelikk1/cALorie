#!/usr/bin/env python3
"""Build Notebook 50: the Notebook 49 cross-validation with a wider residual network (final width 512) for the NEW models only.

Our SmallTCN is already a small residual temporal network (4 residual blocks, widths 64-96-128-128). Notebook 50 trains the same
recipe, folds, seed and data, but the classifier and the three gates use WideTCN (widths 128-256-384-512). Only the architecture
changes, so the comparison with Notebook 49 is fair. The frozen reference models stay SmallTCN. Pass rule: ml/data/improvement_cv_v1/PLAN.md.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--", "ml/notebooks/49_cv_fold0.ipynb"], check=True)

WIDE = '''class WideTCN(nn.Module):
    """Same residual blocks as SmallTCN, wider: final feature size 512."""
    def __init__(self, input_features, num_classes):
        super().__init__()
        blocks, current = [], input_features
        for level, output in enumerate([128, 256, 384, 512]):
            blocks.append(TemporalBlock(current, output, dilation=2 ** level))
            current = output
        self.features = nn.Sequential(*blocks)
        self.classifier = nn.Linear(current, num_classes)

    def forward(self, x):
        return self.classifier(self.features(x).mean(dim=-1))


'''

def patch(src, old, new):
    assert src.count(old) == 1, (old[:50], src.count(old))
    return src.replace(old, new)

for fold in range(5):
    nb = json.loads((ROOT / f"ml/notebooks/49_cv_fold{fold}.ipynb").read_text())
    hits = 0
    for cell in nb["cells"]:
        src = "".join(cell["source"])
        if cell["cell_type"] == "code" and "class SmallTCN(nn.Module):" in src:
            src = patch(src, "class SmallTCN(nn.Module):", WIDE + "class SmallTCN(nn.Module):")
            src = patch(src, "    model = SmallTCN(input_features, num_classes).to(DEVICE)", "    model = WideTCN(input_features, num_classes).to(DEVICE)")
            hits += 1
        elif cell["cell_type"] == "code" and "49_cv_fold{FOLD}.ipynb" in src:
            src = patch(src, 'f"49_cv_fold{FOLD}.ipynb"', 'f"50_wide512_fold{FOLD}.ipynb"')
            src = patch(src, 'f"nb49_fold{FOLD}"', 'f"nb50_fold{FOLD}"')
            src = patch(src, '"seed": RUN_SEEDS[0],', '"seed": RUN_SEEDS[0], "architecture": "WideTCN 128-256-384-512",')
            hits += 1
        elif cell["cell_type"] == "markdown" and "Notebook 49" in src:
            src = (src.replace("Notebook 49, fold", "Notebook 50 (wide 512 network), fold").replace("nb49_fold", "nb50_fold")
                   .replace("Trains the classifier and the three gates (seed 42)", "Trains the classifier and the three gates (seed 42, widths 128-256-384-512)"))
            hits += 1
        else:
            continue
        cell["source"] = src.splitlines(True)
    assert hits == 3, (fold, hits)
    out = ROOT / f"ml/notebooks/50_wide512_fold{fold}.ipynb"
    nb["metadata"]["colab"]["name"] = out.name
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
    print(out)
