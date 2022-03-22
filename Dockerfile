# syntax=docker/dockerfile:1

FROM python:3.9

RUN pip install micropipenv

COPY Pipfile.lock Pipfile.lock

RUN micropipenv install

COPY app app

WORKDIR /app

CMD ["python", "main.py"]