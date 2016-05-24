#!/usr/bin/python


import time

from discovery import get_setting
from discovery import polling_service


if __name__ == '__main__':
    """ Poll etcd at a regular interval.

    Polls etcd for changes and applies them to haproxy at a regular interval.
    The interval is in seconds and can be changed with the POLL_TIMEOUT
    environment variable.

    """

    poll_timeout = get_setting('POLL_TIMEOUT', default=5, as_type=int)

    while polling_service():
        time.sleep(poll_timeout)
