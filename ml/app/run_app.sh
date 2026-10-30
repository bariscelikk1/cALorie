#!/bin/bash
# Starts the cALorie page on this computer only (http://localhost:8501). Needs: pip install -r ml/requirements-macos.txt and ffmpeg.
cd "$(dirname "$0")" && exec streamlit run app.py --server.address 127.0.0.1
