"""HU-01. Mejorar la validación de URLs.

Se incorporan pruebas automatizadas para URLs con esquemas HTTP, HTTPS
y FTP, direcciones IP y puertos personalizados.
"""

# external
import pytest

# local
from validators import ValidationError, url


@pytest.mark.parametrize(
    "value",
    [
        # esquema HTTP
        "http://example.com",
        "http://example.com/path",
        # esquema HTTPS
        "https://example.com",
        "https://example.com/path?query=1",
        # esquema FTP / FTPS
        "ftp://example.com",
        "ftp://example.com/file.txt",
        "ftps://example.com/file.txt",
        # direcciones IPv4
        "http://192.168.1.1",
        "https://10.0.0.1",
        "ftp://127.0.0.1",
        # direcciones IPv6 (entre corchetes, segun RFC 3986)
        "http://[2001:db8::1]",
        "https://[::1]",
        # puertos personalizados con hostname
        "http://example.com:8080",
        "https://example.com:8443",
        "ftp://example.com:2121",
        # puertos personalizados con direccion IP
        "http://192.168.1.1:9000",
        "https://10.0.0.1:8000",
        "ftp://127.0.0.1:2121",
        "http://[2001:db8::1]:8080",
        # puerto en limite valido
        "http://example.com:1",
        "http://example.com:65535",
    ],
)
def test_url_accepts_valid_scheme_ip_and_port_combinations(value: str):
    """Test that HTTP/HTTPS/FTP URLs with IPs and custom ports are accepted."""
    assert url(value) is True


@pytest.mark.parametrize(
    "value",
    [
        # esquema no soportado
        "gopher://example.com",
        "ftpx://example.com",
        # puerto fuera de rango (0 y > 65535)
        "http://example.com:0",
        "http://example.com:65536",
        # puerto no numerico
        "http://example.com:abc",
        # direccion IPv4 invalida con puerto
        "http://999.168.1.1:8080",
        # direccion IPv6 sin corchetes y con puerto (ambiguo, debe rechazarse)
        "http://2001:db8::1:8080",
    ],
)
def test_url_rejects_invalid_scheme_ip_or_port_combinations(value: str):
    """Test that malformed scheme/IP/port combinations raise ValidationError."""
    result = url(value)
    assert isinstance(result, ValidationError)
