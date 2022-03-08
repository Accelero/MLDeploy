# syntax=docker/dockerfile:1

FROM python:3.9.10-bullseye

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system --deploy --ignore-pipfile

COPY . .

CMD ["python", "Inference.py"]