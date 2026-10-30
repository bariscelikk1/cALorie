cALorie in Docker (for another computer)

1. Install Docker Desktop (free): https://www.docker.com/products/docker-desktop/  and start it.
2. Unzip this folder, open a terminal in it (Windows: PowerShell; Mac: Terminal).
3. Run:      docker compose up --build
   The first build takes about 5-10 minutes (it downloads Python packages, about 1.5 GB).
4. Open http://localhost:8501 in a browser, upload a workout video, and wait for the analysis.
5. Stop with Ctrl+C. Next time, `docker compose up` is quick.

Notes
- Everything runs on this computer; the video is not uploaded anywhere.
- It runs on the CPU, so it is slower than on a Mac with Apple GPU: expect roughly the length of the video or less.
- Give Docker at least 4 GB of memory (Docker Desktop -> Settings -> Resources).
- Research prototype: see FINAL_REPORT.md in the project for accuracy and limits.
