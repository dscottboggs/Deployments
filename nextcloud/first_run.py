#!/usr/bin/env python2
from docker     import DockerClient
from jinja2     import Template
from yaml       import load, dump
from subprocess import check_call
from time       import sleep
from misc       import TerminalOutputModifiers
from os         import execlp                                  as switch_to_cmd

client = DockerClient(u"unix://var/run/docker.sock", version=u"1.30")
font   = TerminalOutputModifiers()
with open(u"passwords.yml", u'r') as password_file:
    passwords = load(password_file)


class ContainerDidNotStartException(Exception): pass


def wait(until, condition=lambda: False, throw=False):
    u"""Wait for `until` seconds, or for `condition` to be true.

    By default `condition` is false, causing this function to wait the whole
    time specified by until.

    If throw is a truthy value, it's expected to be a throwable callable,
    i.e. the constructor of a class that extends Exception.
    """
    i = 0
    while i < until:
        if condition():
            return
        sleep(1)
    if throw:
        raise throw()


with open(u"docker-compose.yml.j2", u'r') as compose_file:
    composition_text = Template(compose_file.read()).render(
        {u"password": passwords[u'database']}
    )
with open(u"docker-compose.yml", u'w') as compose_file:
    compose_file.write(composition_text)

check_call(u"docker-compose up -d", shell=True)
wait(
    60,
    lambda: len(client.containers.list(
        filters={u"name": u"nextcloud_frontend_1"}
    )),
    ContainerDidNotStartException
)


nextcloud_container = client.containers.list(
    filters={u"name": u"nextcloud_frontend_1"}
)[0]
assert nextcloud_container.status == u"running"
install_command = (
    u'php occ maintenance:install --database "mysql" '
    + u'--database-name "nextcloud" --database-user "nextcloud" '
    + u'--database-host "nextcloud_database_1" --database-port "3306" '
    + u'--database-pass "%s" --admin-user "scott" ' % passwords[u'database']
    + u'--admin-pass "%s"' % passwords[u'admin']
)
install_result = nextcloud_container.exec_run(
    install_command, user=u'www-data',
)   # ^^ blocks until done.
if install_result.exit_code:
    print "Installation command: %s" % install_command
    print "resulted in the following error:"
    print install_result.output
    exit(install_result.exit_code)
check_call(u'docker-compose down && docker-compose up -d', shell=True)
print(
      font.build(FOREGROUND_COLOR=b"CYAN", WEIGHT=b"BOLD")
    + b"The nextcloud container should be ready now."
    + font.build(WEIGHT=b'NORMAL')
    + b"Switching to Apache log output..."
    + font.build(b'RESET')
)

switch_to_cmd(u"docker-compose", u"docker-compose", u'logs', u'-f')

help(Container.exec_run)
