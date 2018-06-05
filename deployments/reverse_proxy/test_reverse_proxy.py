#!/usr/bin/env python3
from docker import DockerClient
cli = DockerClient('unix://var/run/docker.sock', version='1.27')


def get_containers():
    """Retrieve a list of container names"""
    return [c.name for c in cli.containers.list()]


def get_container_images():
    """Retrieve a list of the images that the available containers have."""
    images = []
    for container in cli.containers.list():
        for image in container.image.tags:
            images.append(image)
    return images


def test_reverse_proxy():
    assert u"reverse_proxy_nginx-proxy_1" in get_containers()
    assert u"jwilder/nginx-proxy:latest" in get_container_images()


def test_companion():
    assert u"reverse_proxy_letsencrypt-nginx-proxy-companion_1"\
        in get_containers()
    assert u"jrcs/letsencrypt-nginx-proxy-companion:latest" \
        in get_container_images()
