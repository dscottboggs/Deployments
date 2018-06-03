#!/usr/bin/env python3
from docker import DockerClient
cli = DockerClient('unix://var/run/docker.sock', version='1.27')

def get_containers():
    """Retrieve a list of container names"""
    return [c.name for c in cli.containers.list()]

def test_reverse_proxy():
    assert "reverseproxy_nginx-proxy_1" in get_containers()

def test_companion():
    assert "reverseproxy_letsencrypt-nginx-proxy-companion_1"\
        in get_containers()

