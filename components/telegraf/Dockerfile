# Build the telegraf container with your plugins
# numpy cannot be installed on python 3.10 due to the lacking wheel
# telegraf:alpine only provides alpine version of 3.16
# alpine 3.16 only provides python 3.10
# Thus, change telegraf:alpine to telegraf:latest
FROM telegraf:latest
COPY telegraf.conf /etc/telegraf/telegraf.conf

## install python and pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.9 \
    python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# copy pipfile & pipfile.lock containing all dependencies for external plugins
COPY Pipfile Pipfile.lock /usr/local/bin/
# install micropipenv and install dependencies from pipfile and pipfile.lock
WORKDIR /usr/local/bin
RUN pip install --no-cache-dir micropipenv[toml] \
  && micropipenv install --deploy \
  && pip uninstall -y micropipenv[toml]

## add external plugins
WORKDIR /
COPY plugins /usr/local/bin/plugins

