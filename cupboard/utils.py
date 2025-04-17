import ipaddress
import socket
from collections import defaultdict

def parse_hosts_file():
    hosts_entries = defaultdict(list)
    with open('/etc/hosts', 'r') as hosts_file:
        for line in hosts_file.readlines():
            line = line.strip()
            # don't take comments or empty lines
            if not line.startswith('#') and not len(line) == 0:
                # format is "ip hostname [hostname ...]"
                ip, *hostnames = line.split(" ")
                # some lines might be split with multiple spaces, cleanup
                hostnames = [hostname for hostname in hostnames if len(hostname) > 0]
                hosts_entries[ip] = hostnames
                print(f"IP: {ip}, Hostnames: {hostnames}")
    return hosts_entries

def write_host_to_hosts_file(ip, hostname):
    with open('/etc/hosts', 'w') as hosts_file:
        hosts_file.write(f"{ip} {hostname}")


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
