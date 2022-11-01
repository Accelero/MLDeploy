FROM debian:bullseye-slim AS build

RUN apt update \
    && apt install build-essential -y

COPY ./src /src

WORKDIR /src

RUN g++ -o test helloworld.cpp

FROM debian:bullseye-slim AS release

RUN apt update

RUN adduser appuser
USER appuser

COPY --from=build /src/test /usr/local/dockertest/test
WORKDIR /usr/local/dockertest

CMD ["./test"]