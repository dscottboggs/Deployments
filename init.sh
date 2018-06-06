#!/usr/bin/env bash

function handle_error() {
    echo "Error while executing"
    echo $1
    exit $2
}

function install_ubuntu() {
    apt install -y python3-pip python3-docker python3-pytest python3-jinja2 \
        vim zsh rsync git apt-transport-https ca-certificates \
        software-properties-common
    wget -qO - https://get.docker.com | sh\
        && systemctl enable docker \
        && systemctl start docker \
        || handle_error "Docker installation" $PIPESTATUS
    python3 -m pip install -U pip
    python3 -m pip install docker-compose PyYAML
}
function install_centos() {
    yum install -y epel-release
    yum install -y python34-pip python34-docker python34-pytest \
        python34-PyYAML python34-jinja2 vim zsh rsync git
    wget -qO - https://get.docker.com | sh \
        && systemctl enable docker \
        && systemctl start docker \
        || handle_error "Docker installation" $PIPESTATUS
    python3 -m pip install -U pip
    python3 -m pip install docker-compose
}

apt update \
    && install_ubuntu \
    || install_centos

mkdir /home/scott/.ssh
ssh-keygen -t ed25519 -f .ssh/id_ed25519 -q
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICa1xQPW/kFnPrO51Mp5gWpEpRZO8d6vtrWxIIpOoFd4 scott@scotts-server
' > /home/scott/.ssh/authorized_keys
cd /home/scott && \
    git clone --recursive https://github.com/dscottboggs/Deployments.git
cd /home/scott/Deployments      &&\
    python3 setup.py install   &&\
    python3 run.py
