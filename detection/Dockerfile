FROM python:3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install -U numpy
RUN pip install -U Cython
RUN pip install -U scikit-multiflow


COPY app .

CMD [ "python", "main.py" ]