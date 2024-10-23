import socket

import nmap
import pytest

from tts.extensions import config_tts


@pytest.fixture
def scanner():
    """Fixture for creating a PortScanner instance."""
    return nmap.PortScanner()


@pytest.fixture
def target():
    """Fixture for getting the resolved target URL from configuration."""
    domain = config_tts.resources.external_server_url
    domain = domain.split("//")[-1]
    resolved_ip = socket.gethostbyname(domain)
    return resolved_ip


def test_ports_open(scanner, target):
    """Test that ports 80 and 443 are open."""
    scanner.scan(target, "80,443")
    open_ports = [
        port
        for port in scanner[target]["tcp"]
        if scanner[target]["tcp"][port]["state"] == "open"
    ]

    assert 80 in open_ports, "Port 80 should be open"
    assert 443 in open_ports, "Port 443 should be open"


def test_all_other_ports_closed(scanner, target):
    """Test that all other ports (except 22, 80 and 443) are closed."""
    scanner.scan(target, "1-1024")
    open_ports = [
        port
        for port in scanner[target]["tcp"]
        if scanner[target]["tcp"][port]["state"] == "open"
    ]

    for port in open_ports:
        assert port in [22, 80, 443], f"Port {port} should be closed"
