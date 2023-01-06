FROM python:3.9-slim


RUN pip install matplotlib numpy pickle-mixin torch pandas scikit-learn scipy
RUN pip install influxdb-client requests
ADD components/preprocessor/app /app

WORKDIR /app
CMD ["/app/main.py"]
ENTRYPOINT ["python3"]