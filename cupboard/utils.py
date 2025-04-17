import ipaddress
import socket
from collections import defaultdict

def parse_hosts_file():
    hosts_entries = []
    with open('/etc/hosts', 'r') as hosts_file:
        for line in hosts_file:
            line = line.strip()
            print(line)

def validate_ip(ip_string):
    try:
        ip_obj = ipaddress.ip_address(ip_string)
        return True
    except ValueError:
        return False

def online_sanity_check(ip_string):
    # at least ONE of these has to be open...
    TEST_PORTS_TCP = [22, 80, 139, 443, 445, 3389]
    result_dict = defaultdict(bool)

    for port in TEST_PORTS_TCP:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip_string, port))
            yield port, True
        except ConnectionRefusedError:
            yield port, False
        except TimeoutError:
            yield port, False

    return result_dict
