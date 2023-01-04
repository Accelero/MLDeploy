
FROM python:3.9-slim


RUN pip install numpy influxdb-client update pandas requests torch scipy scikit-learn
ADD components/offline_segmentation/app /app

WORKDIR /app
CMD ["/app/main.py"]
ENTRYPOINT ["python3"]