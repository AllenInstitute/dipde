#
# dipde miniconda Dockerfile
#
# https://github.com/nicain/dipde_dev

# Pull base image.
FROM continuumio/miniconda3:latest

# Allows plotting tests
RUN apt-get update
RUN apt-get install -y xvfb
USER root
SHELL ["/bin/bash", "-c"]

RUN conda update -y conda
RUN conda install -y pytest
RUN conda install -y -c nicholasc dipde

# Should pass all tests when image is built
RUN /usr/bin/xvfb-run py.test $(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")/dipde/test 2> /dev/null
