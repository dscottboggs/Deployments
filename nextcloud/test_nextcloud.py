#!/usr/bin/env python
from requests import get

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
