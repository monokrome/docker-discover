#!/usr/bin/python


import time

from .settings import get_setting
from . import service


def main():
    """ Poll etcd at a regular interval.

    Polls etcd for changes and applies them to haproxy at a regular interval.
    The interval is in seconds and can be changed with the POLL_TIMEOUT
    environment variable.

    """

    poll_timeout = get_setting('POLL_TIMEOUT', default=5, as_type=int)
    poll = service.polling_service()

    while poll.next():
        time.sleep(poll_timeout)


if __name__ == '__main__':
    main()
