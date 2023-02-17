FROM python:3.9

ARG USER DIR

RUN apt-get update && \
    apt-get -y install sudo &&\
    apt-get -y install build-essential

RUN adduser --disabled-password --gecos '' $USER
RUN adduser $USER sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
ENV PATH="/home/$USER/.local/bin:${PATH}"
USER $USER
WORKDIR /home/appuser/$DIR

RUN pip install --user pip-tools