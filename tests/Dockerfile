FROM ubuntu:18.04

ARG DEBIAN_FRONTEND=noninteractive

RUN set -e && \
    apt-get clean && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    wget ssh software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update

RUN apt-get -y install \
    python2.7 \
    python3.5 \
    python3.6 \
    python3.7 \
    python3.8 \
    python3.9 \
    python3.10 \
    python-pip \
    python3-pip3 \
    libffi-dev \
    libvirt-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip3 install --upgrade pip3 && \
    python -m pip install --upgrade pip

RUN set -e && \
    python3 -m pip install --no-cache-dir "tox==3.20.1"

COPY . /suitable
WORKDIR /suitable

CMD ["tox","-a"]
