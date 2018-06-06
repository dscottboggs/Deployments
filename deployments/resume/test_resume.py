#!/usr/bin/env python3
""""Up-ness monitoring for the Resume service."""
from requests               import get
from requests.exceptions    import SSLError
from hashlib                import md5

urls = ["s.scott.tams.tech"]


class FileData:
    """A container for information about a file"""
    def __init__(self, filename, encoding, hashval):
        self.filename = filename
        self.encoding = encoding
        self.hash = hashval


files = {
        'index.html': FileData(
            'index.html', 'utf-8', '71f0d1e46d80f2878ce076fae5c225d3'),
        'animation.js': FileData(
            'animation.js', 'ascii', '45026ef4c286b90f867fab53646d6424'),
        'stylesheet.css': FileData(
            'stylesheet.css', 'ascii', '5ed611d01c7f87c1b5d1d6830b1c4a82'),
        'jquery-3.2.1.min.js': FileData(
            'jquery-3.2.1.min.js', 'ascii', 'c9f5aeeca3ad37bf2aa006139b935f0a'
        ),
        'Quicksand-Medium.ttf': FileData(
            'Quicksand-Medium.ttf', 'bin', "0c64233241ead44bffbec54eb9d1d164"),
        'WorkSans-Regular.ttf': FileData(
            'WorkSans-Regular.ttf', 'bin', '92bbabfda96fb9e73100d90404d5383a'),
}


def hash_data(data):
    """Get the md5 hash of some binary data."""
    return md5(data).hexdigest()


def test_requests():
    """Test that making a request returns the right values."""
    for url in urls:
        for page in files.values():
            try:
                response = get("http://%s/%s" % (url, page.filename))
                assert response.ok
                assert len(response.history) == 1
                assert response.history[0].status_code == 301
                assert response.status_code == 200
            except SSLError:
                ...
            try:
                response = get("https://%s/%s" % (url, page.filename))
                assert response.ok
                assert not response.history
                assert response.status_code == 200
                assert hash_data(
                    response.content
                ) == page.hash
            except SSLError:
                ...


def test_disallowed():
    """Check that attempting to access disallowed URLs is denied."""
    for url in urls:
        try:
            response = get("https://%s/.git/FETCH_HEAD" % url)
            assert not response.ok
        except SSLError:
            ...
