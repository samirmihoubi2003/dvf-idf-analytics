FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY sql ./sql
RUN pip install --no-cache-dir .
CMD ["python", "-m", "dvf_etl.cli", "--year", "2025", "--departments", "75"]
