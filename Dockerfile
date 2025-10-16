FROM python:3.13.9-alpine3.22

WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main
ENV PYTHONPATH="${PYTHONPATH}:$(pwd)"
COPY . .

ENTRYPOINT [  "poetry", "run", "python", "anomaly_detector/main.py"  ]


