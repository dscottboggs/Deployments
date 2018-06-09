#!/usr/bin/env bash

username=$USER

function handle_error() {
    echo "Error while executing"
    echo $1
    exit $2
}

function install_docker_wget() {
    sudo su -c ' \
        wget -qO - https://get.docker.com | sh \
            && systemctl enable docker  \
            && systemctl start docker ' \
        || handle_error "Docker installation" $PIPESTATUS
}

function install_ubuntu() {
    sudo apt install -y python3-pip python3-docker python3-pytest
        python3-jinja2 vim zsh rsync git apt-transport-https ca-certificates \
        software-properties-common
    install_docker_wget
    sudo python3 -m pip install -U pip
    sudo python3 -m pip install docker-compose PyYAML
}
function install_centos() {
    sudo yum install -y epel-release
    sudo yum install -y python34-pip python34-docker python34-pytest \
        python34-PyYAML python34-jinja2 vim zsh rsync git
    install_docker_wget
    sudo python3 -m pip install -U pip
    sudo python3 -m pip install docker-compose
}


which sudo || apt install -y sudo || yum install -y sudo \
    || handle_error "Installation of sudo" $?

if [ $USER = "root" ]; then
    echo "This script will elevate itself to SU privileges when necessary."
    echo "Please run as a regular user."
    exit 1
fi

sudo apt update  \
    && install_ubuntu \
    || install_centos

mkdir $HOME/.ssh || handle_error "Creating $HOME/.ssh" $?
ssh-keygen -t ed25519 -f $HOME/.ssh/id_ed25519 -q || handle_error "Creating cryptographic identity" $?
chmod 700 $HOME/.ssh
    && chmod 600 $HOME/.ssh/id_ed25519
    && chmod 444 $HOME/.ssh/id_ed25519.pub
    || handle_error "Changing permissions of the $HOME/.ssh/ dir" $?
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICa1xQPW/kFnPrO51Mp5gWpEpRZO8d6vtrWxIIpOoFd4 scott@scotts-server
' > $HOME/.ssh/authorized_keys
cd /opt && \
    git clone --recursive https://github.com/dscottboggs/Deployments.git
cd /opt/Deployments      &&\
    python3 setup.py install   &&\
    python3 run.py
