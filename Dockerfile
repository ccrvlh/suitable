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
    python-pip \
    python-dev \
    python3.5 \
    python3-pip \
    python3-dev \
    libpython3.5-dev \
    python3.6 \
    libpython3.6-dev \
    python3.7 \
    libpython3.7-dev \
    libffi-dev \
    libvirt-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip && \
    python -m pip install --upgrade pip

RUN set -e && \
    python3 -m pip install --no-cache-dir "tox==3.20.1"

COPY . /suitable
WORKDIR /suitable

CMD ["tox","-e","py27-a24,py35-a24,py27-a28,py35-a28"]
