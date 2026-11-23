import hmac
import ipaddress
import socket
from urllib.parse import urlsplit

from fastapi import Header, HTTPException, status

from devpulse.core.config import get_settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = get_settings().api_key
    if not expected or not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid X-API-Key header is required",
        )


def assert_public_target(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only HTTP and HTTPS targets are supported")
    host = parsed.hostname.rstrip(".").lower()
    if host in {"localhost", "metadata.google.internal"} or host.endswith((".localhost", ".local", ".internal")):
        raise ValueError("Private and local network targets are not allowed")
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            addresses = [
                ipaddress.ip_address(item[4][0])
                for item in socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
            ]
        except socket.gaierror as exc:
            raise ValueError("Target hostname could not be resolved") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("Targets must resolve exclusively to public IP addresses")
