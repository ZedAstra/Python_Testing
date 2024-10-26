from server import create_cookie


def test_cookie_creation():
    cookie = create_cookie("test")
    assert "authenticatio" in cookie
