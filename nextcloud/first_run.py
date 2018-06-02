#!/usr/bin/env python2
from docker     import DockerClient
from jinja2     import Template
from yaml       import load, dump
from subprocess import run
from time       import sleep
from misc       TerminalOutputModifiers
from os         import execlpe as switch_to_cmd

client = DockerClient(u"unix://var/run/docker.sock", version=u"1.30")
font   = TerminalOutputModifiers()
with open("passwords.yml", 'r') as password_file:
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
        {u"password": passwords['db']}
    )
with open(u"docker-compose.yml", u'w') as compose_file:
    compose_file.write(composition_text)

run(u"docker-compose up -d", shell=True, check=True)
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
nextcloud_container.exec_run(
      u'cd /var/www/html && php occ maintenance:install --database "mysql" '
    + u'--database-name "nextcloud" --database-user "nextcloud" '
    + u'--database-pass "%s" --admin-user "scott"' % passwords['db']
    + u'--admin-pass "%s"' % passwords['admin'],
      user=u'www-data',
)
wait(15)    # can I add a check to see if the previous command is done?
# will it block until it's done? I think it will...
run(u'docker-compose down && docker-compose up -d')
print(
    font.START, font.FOREGROUND_COLOR['CYAN'], font.WEIGHT['BOLD']
    "The nextcloud container should be ready now.",
    font.START, font.WEIGHT['NORMAL'],
    "Switching to Apache log output..."
    font.START, font.RESET,
    sep='')

switch_to_cmd("docker-compose", 'logs', '-f')
