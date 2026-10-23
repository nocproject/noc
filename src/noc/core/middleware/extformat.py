# ----------------------------------------------------------------------
# ExtFormat middleware
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


def ext_format_middleware(get_response):
    """
    Set request.is_extjs according to __format=ext

    :param get_response: Callable returning response from downstream middleware
    :return:
    """

    def middleware(request):
        if request.GET and request.GET.get("__format") == "ext":
            request.is_extjs = True
        elif request.POST and request.POST.get("__format") == "ext":
            request.is_extjs = True
        else:
            request.is_extjs = False
        return get_response(request)

    return middleware
