FROM debian:bullseye-slim AS build

RUN apt update \
    && apt install build-essential -y \
    && apt install gdb -y