# Build the telegraf container with your plugins
# numpy cannot be installed on python 3.10 due to the lacking wheel
# telegraf:alpine only provides alpine version of 3.16
# alpine 3.16 only provides python 3.10
# Thus, change telegraf:alpine to telegraf:latest
FROM telegraf:latest
COPY telegraf.conf /etc/telegraf/telegraf.conf

# copy requirements.txt containing all dependencies for external plugins
COPY requirements.txt /usr/local/bin/requirements.txt

## install python, pip and packages from requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.9 \
    python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r /usr/local/bin/requirements.txt

## add external plugins
COPY rabbitmq_output_plugin /usr/local/bin/rabbitmq_output_plugin



# # Build the telegraf container with your plugins
# FROM telegraf:alpine
# COPY telegraf.conf /etc/telegraf/telegraf.conf
# COPY rabbitmq_output_plugin /usr/local/bin/rabbitmq_output_plugin

# # install python, pip and packages from requirements.txt
# RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python &&\
#     python3 -m ensurepip &&\
#     pip3 install --no-cache --upgrade pip setuptools
# ENV PIP_ROOT_USER_ACTION=ignore


# # Get repo for amqp_ext plugin
# FROM bitnami/git AS git-amqp_ext
# WORKDIR /app
# RUN git clone --depth 1 --branch v0.3.0 https://github.com/HuitianYu/telegraf-output-plugin-amqp_ext.git telegraf-output-plugin-amqp_ext


# # Build amqp_ext binary
# FROM golang:alpine3.6
# WORKDIR /go/src/app/
# COPY --from=git-amqp_ext /app/ ./
# WORKDIR /go/src/app/telegraf-output-plugin-amqp_ext
# # RUN go mod init cmd/main.go &&\
# #     go mod tidy &&\
# #     go build -o amqp_ext cmd/main.go
# RUN go build -o amqp_ext cmd/main.go

# # Build the telegraf container with your plugins
# FROM telegraf:alpine
# COPY telegraf.conf /etc/telegraf/telegraf.conf
# COPY telegraf-output-plugin-amqp_ext.conf /etc/telegraf/telegraf-output-plugin-amqp_ext.conf
# COPY --from=binary-amqp_ext /go/src/app/telegraf-output-plugin-amqp_ext/amqp_ext /usr/local/bin/amqp_ext



# # Get repo for telegraf
# FROM bitnami/git AS git-telegraf
# WORKDIR /app
# RUN git clone --depth 1 --branch v2.0.0 https://github.com/HuitianYu/telegraf.git telegraf

# # Build telegraf binary
# # FROM golang:alpine AS binary-telegraf
# FROM golang:alpine
# WORKDIR /go/src/app/
# COPY --from=git-telegraf /app/ ./
# WORKDIR /go/src/app/telegraf
# RUN apk update \
# && apk add make \
# && make build

# COPY telegraf.conf /etc/telegraf/telegraf.conf
# CMD ["/go/src/app/telegraf/telegraf", "-config", "/etc/telegraf/telegraf.conf"]

# # # Build the telegraf container with your plugins
# # FROM telegraf:alpine
# # COPY telegraf.conf /etc/telegraf/telegraf.conf
# # COPY --from=binary-telegraf /go/src/app/telegraf/telegraf /usr/bin/telegraf