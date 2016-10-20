#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BI service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.ui import UIService
from api.bi import BIAPI
from noc.core.service.authapi import AuthAPIRequestHandler


class BIService(UIService):
    name = "bi"
    api = [
        BIAPI
    ]
    api_request_handler = AuthAPIRequestHandler
    process_name = "noc-%(name).10s-%(instance).2s"

    def __init__(self):
        super(BIService, self).__init__()

if __name__ == "__main__":
    BIService().start()
