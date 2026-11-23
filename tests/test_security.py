import pytest

from devpulse.security import assert_public_target


def test_rejects_localhost_and_private_ip_addresses():
    for url in ("http://localhost", "http://127.0.0.1", "http://10.0.0.5", "http://169.254.169.254"):
        with pytest.raises(ValueError):
            assert_public_target(url)


def test_rejects_non_http_schemes():
    with pytest.raises(ValueError):
        assert_public_target("file:///etc/passwd")
