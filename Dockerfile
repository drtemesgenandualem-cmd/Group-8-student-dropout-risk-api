# Same Python family that trained the model (Colab used Python 3.13)
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# 1) Install the packages first. Docker caches this step, so rebuilds stay fast
#    as long as requirements-docker.txt does not change.
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# 2) Copy the application and the saved model
COPY evidence/app ./app
COPY model_artifacts ./model_artifacts
RUN chmod -R a+rX /code

# 3) Do not run as root inside the container
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Docker calls /health to see whether the service is working
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# --host 0.0.0.0 lets traffic from outside the container reach the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
