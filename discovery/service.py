#!/usr/bin/python

import etcd
import re
import signal
import subprocess
import sys

from jinja2 import Environment
from jinja2 import PackageLoader

from .settings import get_setting


env = Environment(loader=PackageLoader('haproxy', 'templates'))
signal.signal(signal.SIGCHLD, signal.SIG_IGN)


def get_etcd_address():
    host_info = get_setting('ETCD_HOST', '127.0.0.1').split(':')

    host = host_info[0]
    port = 4001

    if len(host_info) > 1:
        try:
            port = int(host_info[1])
        except ValueError:
            print((
                'port in ETCD_HOST must be an '
                'integer, but got {}'
            ).format(
                port
            ))

            sys.exit(3)

    return host, port


def get_backends():
    host, port = get_etcd_address()

    backends_path = get_setting('ETCD_BACKENDS_PATH', default='/backends')
    option_keys_env_value = get_setting('ETCD_OPTION_KEYS', default='PORT')
    option_keys = set(option_keys_env_value.upper().split(','))

    client = etcd.Client(host=host, port=port)
    backends = client.read(backends_path, recursive=True)

    services = {}

    for i in backends.children:
        if i.key[1:].count('/') != 2:
            continue

        ignore, service, key = i.key[1:].split('/')
        endpoints = services.setdefault(service, dict(port='', backends=[]))

        if key.upper() in option_keys:
            port_setting = re.sub(r'[^A-Z]', '_', service.upper()) + '_PORT'
            endpoints[key] = get_setting(port_setting, default=i.value)
            continue

        endpoints['backends'].append(dict(name=key, addr=i.value))

    return services


def generate_configuration(services):
    template = env.get_template('haproxy.cfg.tmpl')

    with open('/etc/haproxy.cfg', 'w') as f:
        f.write(template.render(services=services))


def polling_service():
    """ Polls etcd for changes and applies the changes into haproxy. """

    current_services = {}

    while True:
        try:
            services = get_backends()

            if services == current_services:
                yield current_services

            print('Updating configuration file.')
            generate_configuration(services)

            print('Configuration changed. Reloading haproxy.')

            error_code = subprocess.call([
                './reload-haproxy.sh',
            ])

            if error_code != 0:
                print('Haproxy reload aborted. Error code was {}'.format(
                    error_code,
                ))

                yield current_services

            current_services = services
            yield current_services

        except Exception, e:
            print('Error updating services: {}'.format(e))
            yield current_services
