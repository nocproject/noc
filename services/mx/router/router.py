# ----------------------------------------------------------------------
# Router
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from collections import defaultdict
from typing import List, DefaultDict, Iterator

# NOC modules
from noc.core.liftbridge.message import Message
from noc.core.mx import MX_MESSAGE_TYPE
from noc.main.models.messageroute import MessageRoute
from noc.core.comp import smart_bytes
from .route import Route

logger = logging.getLogger(__name__)


class Router(object):
    def __init__(self):
        self.chains: DefaultDict[bytes, List[Route]] = defaultdict(list)

    def load(self):
        """
        Load up all the rules and populate the chains
        :return:
        """
        num = 0
        for num, route in enumerate(
            MessageRoute.objects.filter(is_active=True).order_by("order"), start=1
        ):
            self.chains[smart_bytes(route.type)] += [Route.from_route(route)]
        logger.info("Loading %s route", num)

    def iter_route(self, msg: Message) -> Iterator[Route]:
        mt = msg.headers.get(MX_MESSAGE_TYPE)
        if not mt:
            return
        for route in self.chains[mt]:
            if route.is_match(msg):
                yield route
