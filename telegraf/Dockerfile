# Build the telegraf container with your plugins
# numpy cannot be installed on python 3.10 due to the lacking wheel
# telegraf:alpine only provides alpine version of 3.16
# alpine 3.16 only provides python 3.10
# Thus, change telegraf:alpine to telegraf:latest
FROM telegraf:latest
COPY telegraf.conf /etc/telegraf/telegraf.conf

# copy requirements.txt containing all dependencies for external plugins
COPY Pipfile Pipfile.lock /usr/local/bin/

## install python, pip and packages from requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.9 \
    python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

## add external plugins
COPY plugins /usr/local/bin/plugins

# open micropipenv
WORKDIR /usr/local/bin
RUN pip install --no-cache-dir micropipenv[toml] \
  && micropipenv install --deploy \
  && pip uninstall -y micropipenv[toml]

WORKDIR /