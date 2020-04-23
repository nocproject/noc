# ----------------------------------------------------------------------
# RemoteUser Middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.utils.functional import SimpleLazyObject

# NOC modules
from noc.aaa.models.user import User
from noc.core.perf import metrics

HEADER = "HTTP_REMOTE_USER"


def remote_user_middleware(get_response):
    """
    Authenticate against REMOTE_USER request header

    Middleware for utilizing Web-server-provided authentication.

    If request.user is not authenticated, then this middleware attempts to
    authenticate the username passed in the ``REMOTE_USER`` request header.
    If authentication is successful, the user is automatically logged in to
    persist the user in the session.

    :param get_response: Callable returning response from downstream middleware
    :return:
    """

    def user_getter(user):
        def getter():
            u = User.get_by_username(user)
            if not u:
                metrics["error", ("type", "user_not_found")] += 1
            return u

        return getter

    def middleware(request):
        # Get username from REMOTE_USER
        user_name = request.META.get(HEADER)
        if user_name:
            request.user = SimpleLazyObject(user_getter(user_name))
        else:
            request.user = None

        return get_response(request)

    return middleware
