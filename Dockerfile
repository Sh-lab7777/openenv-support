FROM python:3.11-slim-bookworm

WORKDIR /app

# Upgrade pip first for a clean install environment
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY env/         ./env/
COPY graders/     ./graders/
COPY server/      ./server/
COPY app.py       .
COPY inference.py .
COPY openenv.yaml .

EXPOSE 7860

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]