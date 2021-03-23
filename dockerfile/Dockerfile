FROM ubuntu
MAINTAINER "Carlos Brandt <carloshenriquebrandt gmail"

RUN DEBIAN_FRONTEND='noninteractive' \
    apt-get update \
    && apt-get install -y python3-pip \
                          git-core \
                          vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install ipython \
                             jupyterlab \
                             matplotlib \
                             numpy \
                             pandas \
                             scipy

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

# Install EADA
RUN pip3 install https://github.com/chbrandt/eada/archive/refs/tags/v1.1.tar.gz

CMD ["jupyter-lab", "--allow-root", "--no-browser", "--ip", "0.0.0.0"]
