FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY env/        ./env/
COPY graders/    ./graders/
COPY app.py      .
COPY inference.py .
COPY openenv.yaml .

# HuggingFace Spaces runs on port 7860
EXPOSE 7860

# Start FastAPI via uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
