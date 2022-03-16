# syntax=docker/dockerfile:1

FROM python:3.9

WORKDIR /app

RUN pip install micropipenv

#COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN micropipenv install

COPY app .

CMD ["python", "modelserver/modelserver.py"]