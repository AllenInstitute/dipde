FROM ubuntu:16.04

MAINTAINER Nicholas Cain <nicholasc@alleninstitute.org>

RUN apt-get update
RUN apt-get -y install python python-pip python-scipy python-pytest python-matplotlib

RUN pip install sympy
ENV PYTHONPATH /python/dipde
WORKDIR /python/dipde
