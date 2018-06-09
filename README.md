# Deployments
Containerized deployments, tested with pytest, and secured with LetsEncrypt.

Deploy in a single step on a CentOS7 or Ubuntu 18.04 system:

    wget -O - https://raw.githubusercontent.com/dscottboggs/Deployments/master/init.sh | bash

This installs the base dependencies with aptitude or yum, clones
the repository into `./Deployments`, installs the python module,
then finally performs the deployment and initial backup with
`run.py`. Obviously you should review it and the script it pulls
before piping it to your shell.

I have been doing testing in an otherwise blank, up-to-date Ubuntu
18.04 on qemu.
