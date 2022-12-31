#Docker image pyton 3.9 wird verwendet
FROM python:3.9-slim AS base


FROM base AS dev

RUN apt update && apt install build-essential -y
RUN pip install pipenv

#sind nur Variablen oder?
ENV WORKON_HOME="/"
ENV PIPENV_CUSTOM_VENV_NAME=".venv"


FROM dev AS build

COPY ./Pipfile* /workspace/

WORKDIR /workspace


#RUN pipenv install --deploy --ignore-pipfile
RUN pipenv install
#RUN pipenv lock



FROM base AS release

RUN useradd -s /bin/bash appuser

COPY --from=build --chmod=775 /.venv /.venv
# COPY components/offline_segmentation/app /app
# COPY components/offline_segmentation/app/CSV_SDMflex /app/CSV_SDMflex

COPY ./app /app
COPY ./app/CSV_SDMflex /app/CSV_SDMflex

ENV PATH="/.venv/bin:$PATH" \
    PYTHONPATH="/app"

WORKDIR /app
USER appuser

#Programm main.py wird nach start des Containers ausgeführt

CMD ["python", "-u", "main.py"]
