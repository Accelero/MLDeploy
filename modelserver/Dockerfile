FROM python:3.9

RUN pip install micropipenv

COPY Pipfile.lock Pipfile.lock

RUN micropipenv install

COPY app app

WORKDIR /app

ENV DOCKERMODE 1

RUN useradd -u 1234 noadmin

USER noadmin

ENTRYPOINT ["python", "-u", "main.py"]