FROM python:3.9-slim


RUN pip install matplotlib numpy pickle torch pandas scikit-learn scipy
ADD components/offline_segmentation/app /app

WORKDIR /app
CMD ["/app/main.py"]
ENTRYPOINT ["python3"]