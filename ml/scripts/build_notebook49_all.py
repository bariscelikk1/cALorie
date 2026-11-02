#!/usr/bin/env python3
"""Build Notebook 49 all-in-one: runs the five fold notebooks one after another in a single Colab tab (seed 42 throughout).

Each fold notebook is fetched at a pinned commit and its cells are run in the same kernel, so the training code is exactly the
one in 49_cv_fold<k>.ipynb. Every fold downloads its own ZIP when it finishes, so a disconnect loses at most the running fold;
set START_FOLD to resume.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--", "ml/notebooks"], check=True)
COMMIT = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
for k in range(5):  # the pinned commit must already contain the fold notebooks
    subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{COMMIT}:ml/notebooks/49_cv_fold{k}.ipynb"], check=True)

RUN = f'''
import os, json, time, urllib.request
from IPython import get_ipython

COMMIT = "{COMMIT}"
START_FOLD = 0                                   # after a disconnect, set this to the first fold whose ZIP did not download
FOLDS = [int(f) for f in os.environ.get("CALORIE_FOLDS", "0,1,2,3,4").split(",") if int(f) >= START_FOLD]

for fold in FOLDS:
    started = time.time()
    url = f"https://raw.githubusercontent.com/bariscelikk1/cALorie/{{COMMIT}}/ml/notebooks/49_cv_fold{{fold}}.ipynb"
    cells = json.load(urllib.request.urlopen(url))["cells"]
    print(f"===== FOLD {{fold}} of 4 =====", flush=True)
    for cell in cells:
        if cell["cell_type"] == "code":
            result = get_ipython().run_cell("".join(cell["source"]))
            result.raise_error()
    print(f"fold {{fold}} done in {{(time.time() - started) / 60:.0f}} min; nb49_fold{{fold}}.zip downloaded", flush=True)
print("All folds done. Send the five nb49_fold*.zip files.")
'''
nb = {"cells": [
    {"cell_type": "markdown", "metadata": {}, "source": [
        "# cALorie Notebook 49: all five cross-validation folds in one tab\n\n",
        "**Runtime: T4 GPU. Run all, then leave the tab open (about 4-5 hours in total).** Each fold downloads `nb49_foldN.zip` by itself ",
        "when it finishes. If Colab disconnects, set `START_FOLD` in the cell below to the first fold whose ZIP did not arrive and run again. ",
        "Same code and data as the five single-fold notebooks (`ml/data/improvement_cv_v1/PLAN.md`)."]},
    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": RUN.lstrip().splitlines(True)}],
    "metadata": {"colab": {"name": "49_cv_all_folds.ipynb", "provenance": []}, "kernelspec": {"display_name": "Python 3", "name": "python3"},
                 "language_info": {"name": "python", "version": "3"}}, "nbformat": 4, "nbformat_minor": 5}
out = ROOT / "ml/notebooks/49_cv_all_folds.ipynb"
out.write_text(json.dumps(nb, indent=1) + "\n")
print(out, COMMIT[:8])
