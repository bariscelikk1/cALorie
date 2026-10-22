# Independent confirmation UI

Local, dependency-free reviewer for the 17-item creator benchmark confirmation queue.

## Run

From this directory:

```bash
python3 -m http.server 8765
```

Then open `http://127.0.0.1:8765/`.

Progress is saved in browser local storage. When all 17 items are complete, download
`calorie_creator_independent_confirmation_completed.csv` and place it next to the source queue for audit.

The UI intentionally shows the source proposal because the reviewer is confirming a narrow adjudication queue,
but the instruction remains to judge visible motion only. It never loads model logits or predictions.
