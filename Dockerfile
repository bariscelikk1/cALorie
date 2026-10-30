# cALorie web page in a container: one command on any computer that has Docker Desktop.
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libgl1 libglib2.0-0 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY ml/app/requirements-app.txt /tmp/requirements-app.txt
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu && pip install -r /tmp/requirements-app.txt
COPY ml ./ml
# Download the pose model at build time so the page also works without internet afterwards.
RUN python -c "import urllib.request as u; u.urlretrieve('https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task', 'ml/app/pose_landmarker_full.task')"
WORKDIR /app/ml/app
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"]
