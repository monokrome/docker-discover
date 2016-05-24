import mock
import os
import sys
import unittest

from . import get_setting


DEFAULT_ENV_VALUE = {}
MOCKED_ENV_VALUE = 'mock succeeded'
MOCKED_ENV_VAR = 'MOCKED_ENV_VAR'
UNMOCKED_ENV_VAR = 'UNMOCKED_ENV_VAR'


class DiscoveryTestCase(unittest.TestCase):
    def setUp(self):
        if UNMOCKED_ENV_VAR in os.environ:
            del os.environ[UNMOCKED_ENV_VAR]

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
