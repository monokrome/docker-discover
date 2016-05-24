import mock
import os
import sys
import unittest

from . import get_setting
from . import get_etcd_address


EXAMPLE_DOMAIN = 'example.com'
EXAMPLE_PORT = '7373'

DEFAULT_ENV_VALUE = {}
MOCKED_ENV_VALUE = 'mock succeeded'
MOCKED_ENV_VAR = 'MOCKED_ENV_VAR'
UNMOCKED_ENV_VAR = 'UNMOCKED_ENV_VAR'


class DiscoveryTestCase(unittest.TestCase):
    cleared_env_variables = (
        'ETCD_HOST',
        UNMOCKED_ENV_VAR,
    )

    def setUp(self):
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
        os.environ['ETCD_HOST'] = EXAMPLE_DOMAIN + ':' + EXAMPLE_PORT

        self.assertEquals(get_etcd_address(), (
            EXAMPLE_DOMAIN,
            int(EXAMPLE_PORT),
        ))
