# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Docker image used for running tests the under all the supported Python
# versions
FROM ubuntu:20.04

# Base
RUN set -e && \
    apt-get clean && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    wget ssh software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update

RUN apt-get -y install \
    python3-pip \
    libffi-dev \
    libvirt-dev

# Workaround for zipp import error issue - https://github.com/pypa/virtualenv/issues/1630
RUN python3 -m pip install --upgrade pip
RUN set -e && \
    python3 -m pip install --no-cache-dir "tox==3.20.1"

COPY . /suitable
WORKDIR /suitable

CMD ["tox","py36-ansible28"]
