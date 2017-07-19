FROM fedora:24

MAINTAINER Nicholas Cain <nicholasc@alleninstitute.org>

RUN dnf -y install \
           python \
	   python-matplotlib \
	   python-pip \
	   python-scipy \
	   python-pytest

RUN pip install sympy
ENV PYTHONPATH /python/dipde
WORKDIR /python/dipde
