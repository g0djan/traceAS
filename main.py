import sys
import subprocess
import itertools
import json
from urllib.error import URLError, HTTPError
from urllib.parse import quote
from urllib.request import urlopen

local_prefixes = ['10', '100.64', '172.16', '192.168', '127.0.0.1']
output = '{0: > 5} {1: >16} {2: >9} {3: >8} {4: >20}'


def main():  # TODO: add check input correctness
    domain = '127.0.0.1'
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    trace_info = trace_route(domain)
    index = 0
    print('index          address   country      asn             provider')
    for line in itertools.islice(trace_info, 2, None):
        index += 1
        address = fetch_domain(line)
        is_white = is_white_ip(address)
        content = get_content(address) if is_white else None
        asn, provider = content['org'].split(' ', 1) if is_white else ('*', '*')
        country = content['country'] if is_white else '*'
        print(output.format(index, address, country, asn, provider))


def is_white_ip(address):
    return not (address == '*' or any(address.startswith(prefix) for prefix in local_prefixes))


def trace_route(address: str) -> list:
    proc = subprocess.Popen(f'tracert {address}', stdout=subprocess.PIPE)
    info = []
    while True:
        line = proc.stdout.readline().strip().decode(encoding='utf-8')
        if proc.poll() is not None: break
        if not line: continue
        yield line
    proc.wait()
    return info


def fetch_domain(info: str) -> str:
    last_field = info.split()[-1]
    if last_field[0] == '[' and last_field[-1] == ']':
        return last_field[1:-1]
    if not str.isdigit(last_field[0]):
        return '*'
    return last_field


def get_content(address):
    try:
        with urlopen('https://ipinfo.io/' + quote(address) + '/json') as page:
            content = json.loads(page.read(), encoding='utf-8')
    except (URLError, HTTPError):
        return None
    return content


if __name__ == '__main__':
    main()
