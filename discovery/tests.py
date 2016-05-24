import mock
import os
import sys
import unittest

from . import get_setting
from . import get_backends
from . import get_etcd_address


def container_path(container_id):
    return '/backends/example/' + container_id


EXAMPLE_DOMAIN = 'example.com'
EXAMPLE_PORT = '7373'

MOCKED_CONTAINER_ID = 'gVH71U3c'
MOCKED_CONTAINER_ID_2 = 'FUBaFSMz'
MOCKED_CONTAINER_PATH = container_path(MOCKED_CONTAINER_ID)
MOCKED_SERVER_ADDRESS = EXAMPLE_DOMAIN + ':' + EXAMPLE_PORT
MOCKED_SERVER_ADDRESS_2 = EXAMPLE_DOMAIN + ':' + EXAMPLE_PORT + '2'
MOCKED_SERVICE_PORT = '80'

DEFAULT_ENV_VALUE = {}
MOCKED_ENV_VALUE = 'mock succeeded'
MOCKED_ENV_VAR = 'MOCKED_ENV_VAR'
UNMOCKED_ENV_VAR = 'UNMOCKED_ENV_VAR'


class AttributeDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def call_with_success_return_code():
    return 0


def call_with_erroneous_return_code():
    return 0


class FakeClient(object):
    def __init__(self, host, port):
        pass

    def read(self, *args, **kwargs):
        return AttributeDict(children=[
            AttributeDict({
                'key': MOCKED_CONTAINER_PATH,
                'value': MOCKED_SERVER_ADDRESS,
            }),

            AttributeDict({
                'key': container_path(MOCKED_CONTAINER_ID_2),
                'value': MOCKED_SERVER_ADDRESS_2,
            }),

            AttributeDict({
                'key': container_path('port'),
                'value': '80',
            })
        ])


class DiscoveryTestCase(unittest.TestCase):
    cleared_env_variables = (
        'ETCD_HOST',
        UNMOCKED_ENV_VAR,
    )

    def setUp(self):
        mock.patch('subprocess.call', call_with_success_return_code)

        for key in self.cleared_env_variables:
            if key not in os.environ:
                continue

            del os.environ[key]

        os.environ[MOCKED_ENV_VAR] = MOCKED_ENV_VALUE

    def test_get_setting_exits_program_when_no_default_provided(self):
        with mock.patch('sys.exit'):
            get_setting('FAKE_ENV_VAR')
            self.assertEquals(sys.exit.call_count, 1)

    def test_get_setting_exits_returns_default_when_provided(self):
        with mock.patch('sys.exit'):
            result = get_setting(UNMOCKED_ENV_VAR, default=DEFAULT_ENV_VALUE)
            self.assertIs(result, DEFAULT_ENV_VALUE)

    def test_get_setting_returns_value_if_in_environment(self):
        with mock.patch('sys.exit'):
            result = get_setting(MOCKED_ENV_VAR, default=DEFAULT_ENV_VALUE)
            self.assertIs(result, MOCKED_ENV_VALUE)

    def test_get_etcd_address_returns_localhost_as_default(self):
        self.assertEquals(get_etcd_address(), (
            '127.0.0.1',
            4001,
        ))

    def test_get_etcd_address_returns_4001_as_default_port(self):
        os.environ['ETCD_HOST'] = DOMAIN = 'example.com'

        self.assertEquals(get_etcd_address(), (
            DOMAIN,
            4001,
        ))

    def test_get_etcd_address_returns_provided_port_with_domain(self):
        os.environ['ETCD_HOST'] = MOCKED_SERVER_ADDRESS

        self.assertEquals(get_etcd_address(), (
            EXAMPLE_DOMAIN,
            int(EXAMPLE_PORT),
        ))

    def test_get_backends(self):
        with mock.patch('etcd.Client', FakeClient):
            self.assertEquals(get_backends(), {
                'example': {
                    'port': MOCKED_SERVICE_PORT,
                    'backends': [
                        {
                            'addr': 'example.com:7373',
                            'name': MOCKED_CONTAINER_ID,
                        },

                        {
                            'addr': MOCKED_SERVER_ADDRESS_2,
                            'name': MOCKED_CONTAINER_ID_2,
                        }
                    ],
                },
            })
