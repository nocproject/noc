# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Detect best polling method
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import select
import logging

logger = logging.getLogger(__name__)


def has_select():
    """
    Check select() method is available

    :rtype: Bool
    """
    return True


def has_kevent():
    """
    Check kevent/kqueue method is available

    :rtype: Bool
    """
    return hasattr(select, "kqueue")


def has_poll():
    """
    Check poll() method is available

    :rtype: Bool
    """
    return hasattr(select, "poll")


def has_epoll():
    """
    Check epoll() method is available

    :rtype: Bool
    """
    return hasattr(select, "epoll")


def get_select_poller():
    from selectpoller import SelectPoller
    logger.info("Activating 'select' poller")
    return SelectPoller()


def get_poll_poller():
    from pollpoller import PollPoller
    logger.info("Activating 'poll' poller")
    return PollPoller()


def get_epoll_poller():
    from epollpoller import EpollPoller
    logger.info("Activating 'epoll' poller")
    return EpollPoller()


def get_kevent_poller():
    from keventpoller import KEventPoller
    logger.info("Activating 'kevent' poller")
    return KEventPoller()


def get_methods():
    """
    Get list of available polling methods
    :return:
    """
    r = []
    if has_kevent():
        r += ["kevent"]
    if has_epoll():
        r += ["epoll"]
    if has_poll():
        r += ["poll"]
    if has_select():
        r += ["select"]
    return r


def get_poller(method):
    logger.info("Setting up '%s' polling method" % method)
    if method == "optimal":
        # Detect possibilities
        if has_kevent():  # kevent
            return get_kevent_poller()
        elif has_epoll():
            return get_epoll_poller()  # epoll
        elif has_poll():  # poll
            return get_poll_poller()
        else:  # Fallback to select
            return get_select_poller()
    elif method == "kevent" and has_kevent():
        return get_kevent_poller()
    elif method == "epoll" and has_epoll():
        return get_epoll_poller()
    elif method == "poll" and has_poll():
        return get_poll_poller()
    else:
        # Fallback to select
        return get_select_poller()
