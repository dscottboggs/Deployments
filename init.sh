#!/usr/bin/env bash

wd=$PWD

function handle_error() {
    echo "Error while ${@:2}."
    cd $wd
    exit $1
}

function install_docker_wget() {
    sudo su -c ' \
        wget -qO - https://get.docker.com | sh \
            && systemctl enable docker  \
            && systemctl start docker ' \
        || handle_error $? installing docker
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
    || handle_error $? installing sudo

if [ $USER = "root" ]; then
    echo "This script will elevate itself to SU privileges when necessary."
    echo "Please run as a regular user."
    exit 1
fi

sudo apt update  \
    && install_ubuntu \
    || install_centos \
    || handle_error $? installing dependencies

parent_dir=$HOME/.local/share
mkdir -p parent_dir || handle_error $? creating parent directory

cd $parent_dir && \
    git clone --recursive https://github.com/dscottboggs/Deployments.git \
    || handle_error $? cloning repository.

sudo python3 $parent_dir/Deployments/setup.py install \
    || handle_error $? running python\'s setup.py installation.

echo Installation complete. Running...
sudo python3 $parent_dir/Deployments/run.py \
    || handle_error $? running the installed script.

cd $wd
