#!/usr/bin/env python
from requests   import get
from first_run  import client
from yaml       import load


def test_index():
    """Test that the root URLs respond properly."""
    response = get("http://s.cloud.tams.tech")
    assert response.ok
    assert response.history
    assert response.history[0].status_code == 301
    assert response.status_code == 200
    response = get("https://s.cloud.tams.tech")
    assert response.ok
    assert not response.history
    assert response.status_code == 200

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
