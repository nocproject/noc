#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Card service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.service.ui import UIService
from card import CardRequestHandler


class CardService(UIService):
    name = "card"

    def get_handlers(self):
        return super(CardService, self).get_handlers() + [
            ("^/card/(\S+)/$", CardRequestHandler)
        ]


if __name__ == "__main__":
    CardService().start()
