FROM python:3.9

RUN pip install micropipenv

COPY Pipfile.lock Pipfile.lock

RUN micropipenv install

COPY app app

WORKDIR /app

RUN useradd -u 1234 noadmin

USER noadmin

ENTRYPOINT ["python", "-u", "main.py"]