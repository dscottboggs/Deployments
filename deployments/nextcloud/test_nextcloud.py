#!/usr/bin/env python
from requests               import get, put, delete
from requests.exceptions    import SSLError
from yaml                   import load
from deployments.nextcloud  import user_info, client, occ, THIS_DIR
from deployments.misc       import wait
from subprocess             import check_call


def test_index():
    """Test that the root URLs respond properly."""
    for url in user_info['urls']:
        try:
            response = get("http://{}/".format(url))
            assert response.ok
            assert response.history
            assert response.history[0].status_code == 301
            assert response.history[0].url == "http://{}/".format(url)
            assert response.history[1].status_code == 302
            assert response.history[1].url == "https://{}/".format(url)
            assert response.status_code == 200
            assert response.url == "https://{}/login".format(url)
            response = get("https://{}/".format(url))
            assert response.ok
            assert response.history
            assert response.history[0].status_code == 302
            assert response.history[0].url == "https://{}/".format(url)
            assert response.status_code == 200
            assert response.url == "https://{}/login".format(url)
        except SSLError:
            ...


def test_user():
    """Test that the user is present and all."""
    assert {'scott': 'scott'} in load(occ(None, "user:list"))
    uinfostr = occ(None, "user:info", "scott")
    assert uinfostr
    uinfo = load(uinfostr)
    assert {'user_id': 'scott'} in uinfo
    assert {'display_name': 'scott'} in uinfo
    assert {'enabled': True} in uinfo
    assert {'groups': ['admin']} in uinfo
    assert {'quota': 'none'} in uinfo


def test_upload():
    """Test that uploading a file works.

    This test uses the backend WebDAV REST api and hence contains no
    checks for the actual GUI interface.
    """
    for url in user_info['urls']:
        try:
            user = user_info['admin'][0]
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
        except:
            ...


def test_upload_survives():
    """Test that an uploaded file survives container destruction."""
    for url in user_info['urls']:
        try:
            user = user_info['admin'][0]
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
                "docker-compose down && docker volume prune -f"
                + "&& docker-compose up -d",
                shell=True,
                cwd=THIS_DIR
            )
            wait(20)
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
        except SSLError:
            ...


def test_container_presence():
    """Test that the right containers are present."""
    assert client.containers.list(filters={"name": "nextcloud_frontend_1"})
    assert client.containers.list(filters={"name": "nextcloud_database_1"})
