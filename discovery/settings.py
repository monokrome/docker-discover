import sys
import os


def get_setting(key, default=None, as_type=None):
    if default is None and key not in os.environ:
        print(' not set'.format(key))
        sys.exit(2)

    value = os.environ.get(key, default)

    if as_type is not None:
        try:
            value = as_type(value)
        except ValueError:
            print('"{}" is not a valid value for {}'.format(key))

    return value
