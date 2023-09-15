# Docker container for running OGDF Jupyter notebooks on mybinder.org
# based on https://mybinder.readthedocs.io/en/latest/tutorials/dockerfile.html

FROM python:3.11

RUN pip install --no-cache-dir ogdf-python[quickstart]

ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}
WORKDIR ${HOME}
