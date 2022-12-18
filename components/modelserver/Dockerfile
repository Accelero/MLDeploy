FROM python:3.9-slim AS base


FROM base AS dev

RUN apt update && apt install build-essential -y
RUN pip install pipenv

ENV WORKON_HOME="/" \
    PIPENV_CUSTOM_VENV_NAME=".venv"


FROM dev AS build

COPY components/modelserver/Pipfile* /workspace/

WORKDIR /workspace
RUN pipenv install --deploy --ignore-pipfile


FROM base AS release

RUN useradd -s /bin/bash appuser

COPY --from=build --chmod=775 /.venv /.venv
COPY components/modelserver/app /app

ENV PATH="/.venv/bin:$PATH" \
    PYTHONPATH="/app"

WORKDIR /app
USER appuser

CMD ["python", "-u", "main.py"]