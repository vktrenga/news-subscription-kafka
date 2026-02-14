FROM python:3.11-slim

WORKDIR /app

# Copy shared lib first
COPY shared-lib /shared-lib

# Install shared lib
RUN pip install /shared-lib

# Copy service code
COPY news-service/ .

RUN pip install -r requirements.txt

# CMD ["python", "main.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

