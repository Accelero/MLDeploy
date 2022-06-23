FROM python:3.9-slim

RUN apt-get update && apt-get install -y build-essential \
    python3-numpy

RUN adduser appuser
USER appuser
WORKDIR /home/appuser

RUN pip install --user micropipenv \
    pip install --user cython pybind11 \
    pip install --user numpy==1.23.0

ENV PATH="/home/appuser/.local/bin:${PATH}"

COPY --chown=appuser:appuser Pipfile.lock Pipfile.lock
RUN micropipenv install -- --user

COPY --chown=appuser:appuser app app

WORKDIR /home/appuser/app

ENTRYPOINT ["python", "-u", "main.py"]