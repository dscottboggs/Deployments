#!/usr/bin/env python
from requests   import get, put, delete
from misc       import client, occ
from yaml       import load
from first_run  import user_info
from time       import sleep


def test_index():
    """Test that the root URLs respond properly."""
    response = get("http://s.cloud.tams.tech")
    assert response.ok
    assert response.history
    assert response.history[0].status_code == 301
    assert response.history[0].url == "http://s.cloud.tams.tech/"
    assert response.history[1].status_code == 302
    assert response.history[1].url == "https://s.cloud.tams.tech/"
    assert response.status_code == 200
    assert response.url == "https://s.cloud.tams.tech/login"
    response = get("https://s.cloud.tams.tech")
    assert response.ok
    assert response.history
    assert response.history[0].status_code == 302
    assert response.history[0].url == "https://s.cloud.tams.tech/"
    assert response.status_code == 200
    assert response.url == "https://s.cloud.tams.tech/login"

def test_user():
    """Test that the user is present and all."""
    assert {'scott': 'scott'} in load(occ(None, "user:list"))
    unifostr = occ(None, "user:info", "scott")
    assert uinfostr
    uinfo = load(uinfostr)
    assert {'user_id': 'scott'} in uinfo
    assert {'display_name': 'scott'} in uinfo
    assert {'enabled': True} in uinfo
    ugroups = [
        elem for elem in uinfo if tuple(elem.keys()) == ('groups')
    ][0]['groups']
    assert 'admin' in ugroups
    assert {'quota': 'none'} in uinfo

def test_upload():
    """Test that uploading a file works.

    This test uses the backend WebDAV REST api and hence contains no
    checks for the actual GUI interface.
    """
    user = user_info['admin'][0]
    url = "s.cloud.tams.tech"
    response = put(
        url="https://%s/remote.php/dav/files/%s/testfile.txt" % (
            url, user['user_id']
        ),
        auth=(user['user_id'], user['password']),
        data=b"Test text text that tests."
    )
    assert response.ok
    response = get(
        url="https://%s/remote.php/dav/files/%s/testfile.txt" % (
            url, user['user_id']
        ),
        auth=(user['user_id'], user['password'])
    )
    assert response.ok
    assert response.content == b"Test text text that tests."
    response = delete(
        url="https://%s/remote.php/dav/files/%s/testfile.txt" % (
            url, user['user_id']
        ),
        auth=(user['user_id'], user['password'])
    )
    assert response.ok



def test_upload_survives():
    """Test that an uploaded file survives container destruction."""
    user = user_info['admin'][0]
    url = "s.cloud.tams.tech"
    response = put(
        url="https://%s/remote.php/dav/files/%s/testfile.txt" % (
            url, user['user_id']
        ),
        auth=(user['user_id'], user['password']),
        data=b"Test text text that tests."
    )
    assert response.ok
    response = get(
        url="https://%s/remote.php/dav/files/%s/testfile.txt" % (
            url, user['user_id']
        ),
        auth=(user['user_id'], user['password'])
    )
    assert response.ok
    assert response.content == b"Test text text that tests."
    check_call(
        "docker-compose down && docker volume prune -y && docker-compose up -d"
    )
    sleep(15)
    response = get(
        url="https://%s/remote.php/dav/files/%s/testfile.txt" % (
            url, user['user_id']
        ),
        auth=(user['user_id'], user['password'])
    )
    assert response.ok
    assert response.content == b"Test text text that tests."
    response = delete(
        url="https://%s/remote.php/dav/files/%s/testfile.txt" % (
            url, user['user_id']
        ),
        auth=(user['user_id'], user['password'])
    )
    assert response.ok
