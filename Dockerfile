FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN apt-get update && apt-get install -y \
    wget \
    fonts-dejavu \
    fontconfig

RUN mkdir -p /usr/share/fonts/truetype/pacifico
RUN wget https://github.com/google/fonts/raw/main/ofl/pacifico/Pacifico-Regular.ttf --directory-prefix /usr/share/fonts/truetype/pacifico
RUN fc-cache -f -v

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY backend/ ./backend/

WORKDIR /app/backend

RUN poetry lock
RUN poetry install --no-root --no-interaction

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["poetry", "run", "flask", "run"]