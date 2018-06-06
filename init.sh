#!/usr/bin/env bash
yum install epel-release
yum install python34-pip python34-docker python34-pytest python34-PyYAML      \
            python34-jinja2 docker docker-compose vim zsh rsync git
mkdir /home/scott/.ssh
ssh-keygen -t ed25519 -f .ssh/id_ed25519 -q
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICa1xQPW/kFnPrO51Mp5gWpEpRZO8d6vtrWxIIpOoFd4 scott@scotts-server
' > /home/scott/.ssh/authorized_keys
cd /home/scott && \
    git clone --recursive https://github.com/dscottboggs/Deployments.git
cd /home/scott/Deployments      &&\
    python3.4 setup.py install   &&\
    python3.4 run.py
