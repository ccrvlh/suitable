FROM ubuntu:18.04

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN set -e && \
    apt-get clean && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    wget ssh software-properties-common sshpass && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update

RUN apt-get -y install \
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

RUN python3 -m pip install --upgrade pip

RUN set -e && \
    python3 -m pip install --no-cache-dir tox

COPY . /suitable
WORKDIR /suitable

# CMD ["tox","-e","py35-a28"]
# CMD ["sleep","99999999"]
