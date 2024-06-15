FROM python:3.11-slim-bookworm as base

ENV PYTHONBUFFERED=1
ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

RUN apt-get update \
    && apt-get upgrade -y
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
		&& $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /mini_sedric

COPY ../poetry.lock ../pyproject.toml .

FROM base as dev
COPY --from=base /mini_sedric /mini_sedric
RUN poetry install --no-interaction --no-cache
COPY ./mini_sedric/ .

FROM base as prod
COPY --from=base /mini_sedric /mini_sedric
RUN poetry install --no-interaction --no-cache --without dev
COPY ./mini_sedric/ .
EXPOSE 80
CMD ["poetry", "run", "fastapi", "run", "main.py", "--port", "80"]
