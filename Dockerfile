#
# dipde miniconda Dockerfile
#
# https://github.com/nicain/dipde_dev

# Pull base image.
FROM continuumio/miniconda:4.1.11

ARG DIPDE_BRANCH=release_0.2.0
RUN apt-get install -y xvfb
USER root
SHELL ["/bin/bash", "-c"]

RUN wget https://raw.githubusercontent.com/nicain/dipde_dev/$DIPDE_BRANCH/environment.yml
RUN conda update -y conda
RUN conda env update -f environment.yml -n root
RUN pip install https://github.com/nicain/dipde_dev/zipball/$DIPDE_BRANCH

RUN /usr/bin/xvfb-run py.test /opt/conda/lib/python2.7/site-packages/dipde/test 2> /dev/null

#RUN py.test /opt/conda/lib/python2.7/site-packages/dipde/test

## Install.
#RUN \
#  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
#  apt-get update && \
#  apt-get -y upgrade && \
#  apt-get install -y build-essential && \
#  apt-get install -y software-properties-common && \
#  apt-get install -y byobu curl git htop man unzip vim wget && \
#  rm -rf /var/lib/apt/lists/*
#
## Add files.
#ADD root/.bashrc /root/.bashrc
#ADD root/.gitconfig /root/.gitconfig
#ADD root/.scripts /root/.scripts
#
## Set environment variables.
#ENV HOME /root
#
## Define working directory.
#WORKDIR /root
#
## Define default command.
