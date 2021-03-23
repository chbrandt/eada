FROM continuumio/miniconda3
MAINTAINER "Carlos Brandt <carloshenriquebrandt gmail"

RUN conda update -y conda

ARG WORKDIR="/work"
ARG DOCKER_USERNAME="user"
ARG DOCKER_USERGROUP="users"
ARG DOCKER_UID=1000
ARG DOCKER_GID=100

ENV WORKDIR="$WORKDIR"
ENV DOCKER_USERNAME="$DOCKER_USERNAME"
ENV DOCKER_USERGROUP="$DOCKER_USERGROUP"
ENV DOCKER_UID="$DOCKER_UID"
ENV DOCKER_GID="$DOCKER_GID"

RUN test `groupadd -r -g "$DOCKER_GID" "$DOCKER_USERGROUP" 2> /dev/null` \
    || echo "Group $DOCKER_USERGROUP/$DOCKER_GID already exist" \
    && useradd --no-log-init -m -s /bin/bash \
                                -g "$DOCKER_USERGROUP" \
                                -u "$DOCKER_UID" "$DOCKER_USERNAME"

# Set the container user from now on
USER "$DOCKER_USERNAME:$DOCKER_USERGROUP"

# WORKDIR (maybe give by the user, in relative path -- we then set relative to '/')
WORKDIR "/"
WORKDIR "$WORKDIR"

VOLUME "$WORKDIR/volume"

# Managing envs is done with conda
RUN conda create -n "$DOCKER_USERNAME" \
      -c conda-forge \
      -y python=3.8 pip jupyterlab \
    && conda init bash

# # Install EADA
# RUN pip install https://github.com/chbrandt/eada/archive/refs/tags/v1.0a2.tar.gz
#
# ENV JUPYTER_ENABLE_LAB="yes"
# ENTRYPOINT ["conda", "activate", "$DOCKER_USERNAME"]
# CMD ["jupyter-lab", "--allow-root", "--no-browser", "--ip", "0.0.0.0"]
# ENTRYPOINT ["conda", "run", "-n", "user", "jupyter-lab", "--allow-root", "--no-browser", "--ip", "0.0.0.0"]

RUN echo "#!/bin/bash" > /tmp/run.sh &&\
    echo "jupyter-lab --allow-root --no-browser --ip=0.0.0.0 &> /tmp/run.log" \
        > /tmp/run.sh \
    && chmod +x /tmp/run.sh
ENTRYPOINT ["/bin/bash","-c","conda run -n user /tmp/run.sh"]
# ENTRYPOINT exec conda run -n user /tmp/run.sh & tail -f /tmp/run.log

# ENTRYPOINT exec conda run -n user conda env list
# ENTRYPOINT exec conda run -n user jupyter-lab --allow-root --no-browser --ip=0.0.0.0
# CMD [ "--allow-root","--no-browser","--ip","0.0.0.0" ]
