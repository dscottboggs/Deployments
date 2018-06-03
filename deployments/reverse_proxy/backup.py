"""Backup the certificates and configurations stored in ./mounts/"""
from subprocess import check_call
from time       import time


test_backup_dir = "/home/scott/Documents/code/Deployments/test_backups"
reverse_proxy_dir = '.'
now = datetime.now().ctime()
print now
check_call("rsync -aqX --partial %(rpd)s/mounts/ %(tbd)s/staging/reverse_proxy/")
