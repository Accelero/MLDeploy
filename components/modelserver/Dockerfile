FROM python:3.9-slim AS build

RUN apt-get update && apt-get install build-essential -y
RUN pip install micropipenv
COPY custom_packages/dist /tmp/custom_packages/dist
COPY modelserver/Pipfile.lock /tmp/modelserver/Pipfile.lock

WORKDIR /tmp/modelserver
RUN micropipenv install -- --user

FROM python:3.9-slim AS release

RUN adduser appuser
USER appuser
WORKDIR /home/appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"

COPY --from=build --chown=appuser:appuser /root/.local .local
COPY modelserver/app app

WORKDIR /home/appuser/app

CMD ["python", "-u", "main.py"]