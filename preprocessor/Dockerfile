FROM python:3.9.12-slim

RUN apt-get update && apt-get install build-essential -y

RUN adduser appuser
USER appuser
WORKDIR /home/appuser

RUN pip install --user micropipenv

ENV PATH="/home/appuser/.local/bin:${PATH}"

COPY --chown=appuser:appuser Pipfile.lock Pipfile.lock
RUN micropipenv install -- --user

COPY --chown=appuser:appuser app app

WORKDIR /home/appuser/app

ENTRYPOINT ["python", "-u", "main.py"]