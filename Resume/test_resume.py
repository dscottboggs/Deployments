from requests import get, Response
help(Response.text)

urls = "scott.tams.tech", "resume.tams.tech"


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


def hash_of_str(val: str, enc='utf-8') -> str:
    """Get the md5 hash of a string."""
    return hash_data(val) if enc == 'bin' else hash_data(val.encode(enc))


def hash_data(data: bytes) -> str:
    """Get the md5 hash of some binary data."""
    return md5(data).hexdigest()


def test_requests():
    """Test that making a request returns the right values."""
    for url in urls:
        for page in files.values():
            response = get(f"http://{url}/{page.filename}")
            assert response.ok
            assert response.status_code == 301
            response = get(f"https://{url}/{page.filename}")
            assert response.ok
            assert response.status_code == 200
            assert hash_of_str(
                response.text, page.encoding
            ) == page.hash


def test_disallowed():
    """Check that attempting to access disallowed URLs is denied."""
    for url in urls:
        response = get(f"https://{url}/.git/FETCH_HEAD")
        assert not response.ok
