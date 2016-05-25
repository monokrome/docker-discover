import os
import mock
import sys
import unittest

from .settings import get_setting


DEFAULT_ENV_VALUE = {}
MOCKED_ENV_VALUE = 'mock succeeded'
MOCKED_ENV_VAR = 'MOCKED_ENV_VAR'
UNMOCKED_ENV_VAR = 'UNMOCKED_ENV_VAR'

MOCK_STR_VALUE = 'str'
MOCK_INT_VALUE = '42'


class SettingsTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['MOCK_STR_SETTING'] = MOCK_STR_VALUE
        os.environ['MOCK_INT_SETTING'] = MOCK_INT_VALUE

    def tearDown(self):
        del os.environ['MOCK_STR_SETTING']
        del os.environ['MOCK_INT_SETTING']

    def test_get_setting_exits_program_when_no_default_provided(self):
        with mock.patch('sys.exit'):
            get_setting('FAKE_ENV_VAR')
            self.assertEquals(sys.exit.call_count, 1)

    def test_get_setting_exits_returns_default_when_provided(self):
        result = get_setting(UNMOCKED_ENV_VAR, default=DEFAULT_ENV_VALUE)
        self.assertIs(result, DEFAULT_ENV_VALUE)

    def test_get_setting_returns_value_if_in_environment(self):
        result = get_setting(MOCKED_ENV_VAR, default=DEFAULT_ENV_VALUE)
        self.assertEqual(result, MOCKED_ENV_VALUE)

    def test_get_setting_returns_as_type_when_provided(self):
        self.assertEqual(
            get_setting('MOCK_INT_SETTING', as_type=int),
            int(MOCK_INT_VALUE),
        )

    def test_get_setting_exits_process_when_invalid_value_in_environment(self):
        with mock.patch('sys.exit'):
            get_setting('MOCK_STR_SETTING', as_type=int)
            self.assertEquals(sys.exit.call_count, 1)
