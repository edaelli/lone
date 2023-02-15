################################################################################
# Dockerfile for lone
################################################################################
FROM ubuntu:22.04
MAINTAINER Edoardo Daelli <edoardo.daelli@gmail.com>

################################################################################
# Add a non-root user named "lone_user" to the image
################################################################################
RUN useradd -m -s /bin/bash lone_user

################################################################################
# Proxy configuration if requested
################################################################################
ARG http_proxy=""
ARG https_proxy=""

# Set env proxy variables
ENV HTTP_PROXY=$http_proxy
ENV http_proxy=$http_proxy
ENV HTTPS_PROXY=$https_proxy
ENV https_proxy=$https_proxy
ENV NO_PROXY="localhost,127.0.0.1"
ENV no_proxy="localhost,127.0.0.1"

# Set apt to use the proxy values
RUN touch /etc/apt/apt.conf.d/proxy.conf
RUN echo "Acquire::http::Proxy \"$http_proxy\";" >> /etc/apt/apt.conf.d/proxy.conf
RUN echo "Acquire::https::Proxy \"$https_proxy\";" >> /etc/apt/apt.conf.d/proxy.conf

################################################################################
# Install packages
################################################################################
RUN apt-get -y update
RUN apt-get -y install \
	python3-dev \
	python3-distutils \
	python3-apt \
	python3-venv \
	python3-pip \
	python3-yaml \
	pciutils \
    libhugetlbfs-dev \
    vim

################################################################################
# Copy lone to /opt/
################################################################################
ADD python3 /opt/lone
RUN chown -R lone_user:lone_user /opt/lone

################################################################################
# Switch to the lone user, and set its path
################################################################################
USER lone_user
ENV PATH=$PATH:~/.local/bin

################################################################################
# If the user set the --build-arg piptrust=1, then set pip3 to trust the default
#    locations. This is useful if building this container behind a HTTPS proxy
#    with a custom SSL certificate
################################################################################
ARG piptrust
RUN if [ "$piptrust" = "1" ]; then pip3 config set global.trusted-host \
    "pypi.org files.pythonhosted.org pypi.python.org"; fi

################################################################################
# Install lone
################################################################################
RUN pip3 install /opt/lone
