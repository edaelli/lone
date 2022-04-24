################################################################################
# Dockerfile for stdk
################################################################################
FROM ubuntu:22.04
MAINTAINER Edoardo Daelli <edoardo.daelli@gmail.com>

################################################################################
# Add the stdk_user user/group to the image
################################################################################
ARG HOME_PATH=''
RUN groupadd -g 1000 -o stdk_user
RUN useradd -m -u 1000 -g 1000 -o -s /bin/bash stdk_user
ENV PATH="/home/stdk_user/.local/bin:${PATH}"

################################################################################
# Create local working directory to mount the host system's fs
################################################################################
RUN install -d /local_fs/

################################################################################
# Install base packages
################################################################################
RUN apt-get -y update
RUN apt-get -y install software-properties-common
RUN apt-get -y install \
	apt-utils \
	curl \
	pciutils \
    build-essential \
    vim

################################################################################
# Install python3-10 from deadsnakes/ppa and pip with get-pip.py
################################################################################
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install -y \
	python3.10 \
	python3.10-dev \
	python3.10-distutils \
	python3.10-apt \
	python3.10-venv
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

################################################################################
# Install libhugetlbfs to use hugepages in c extension
################################################################################
RUN apt-get -y install libhugetlbfs-dev

################################################################################
# Install stdk
################################################################################
ADD python3 /opt/stdk
RUN chown -R stdk_user:stdk_user /opt/stdk
USER stdk_user
RUN pip install /opt/stdk
RUN cd /opt/stdk && tox --color=yes
