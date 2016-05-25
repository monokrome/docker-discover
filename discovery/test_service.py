import mock
import os
import sys
import unittest

from .service import get_backends
from .service import get_etcd_address
from .service import polling_service


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

MOCKED_ENV_VALUE = 'mock succeeded'
MOCKED_ENV_VAR = 'MOCKED_ENV_VAR'
UNMOCKED_ENV_VAR = 'UNMOCKED_ENV_VAR'

MOCK_BACKENDS = {
    'backends': [],
}


class AttributeDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def call_with_success_return_code(*args):
    return 0


def call_with_erroneous_return_code(*args):
    return 0


def mock_get_backends():
    return MOCK_BACKENDS


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


class DiscoveryServiceTestCase(unittest.TestCase):
    cleared_env_variables = (
        'ETCD_HOST',
        UNMOCKED_ENV_VAR,
    )

    def setUp(self):
        mock.patch('etcd.Client', FakeClient)
        mock.patch('subprocess.call', call_with_success_return_code)

        for key in self.cleared_env_variables:
            if key not in os.environ:
                continue

            del os.environ[key]

        os.environ[MOCKED_ENV_VAR] = MOCKED_ENV_VALUE

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

    def test_get_etcd_address_exits_unless_port_is_integer(self):
        os.environ['ETCD_HOST'] = EXAMPLE_DOMAIN + ':invalidPort'

        with mock.patch('sys.exit'):
            get_etcd_address()
            self.assertEqual(sys.exit.call_count, 1)

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

    def test_get_backends_uses_custom_port_key(self):
        with mock.patch('etcd.Client', FakeClient):
            os.environ['EXAMPLE_PORT'] = '80'

            services = get_backends()
            serving_port = services['example']['port']

            self.assertEquals(serving_port, '80')

    @mock.patch(
        'discovery.service.generate_configuration',
        call_with_success_return_code,
    )
    @mock.patch('discovery.service.get_backends', mock_get_backends)
    @mock.patch('subprocess.call', call_with_success_return_code)
    def test_polling_service_yields_result_from_get_backends(self):
        poll = polling_service()

        for _ in xrange(10):
            self.assertIs(poll.next(), MOCK_BACKENDS)

    @mock.patch(
        'discovery.service.generate_configuration',
        call_with_success_return_code,
    )
    @mock.patch('discovery.service.get_backends', mock_get_backends)
    @mock.patch('subprocess.call', call_with_erroneous_return_code)
    def test_polling_service_yields_backends_when_subprocess_fails(self):
        self.assertIs(polling_service().next(), MOCK_BACKENDS)
