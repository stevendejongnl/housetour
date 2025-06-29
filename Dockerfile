FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY backend/pyproject.toml backend/poetry.lock* ./
RUN poetry install --no-root --no-interaction

COPY backend/ ./backend/
COPY public/ ./backend/public/

WORKDIR /app/backend

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["poetry", "run", "flask", "run"]