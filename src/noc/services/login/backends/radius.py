# ---------------------------------------------------------------------
# RADIUS Authentication backend
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from functools import cached_property
from pathlib import Path

# Third-party modules
from pyrad.client import Client, Timeout
from pyrad.dictionary import Dictionary
from pyrad.packet import AccessAccept, AccessRequest

# NOC modules
from noc.config import config
from noc.core.comp import smart_bytes

from .base import BaseAuthBackend


class RADIUSBackend(BaseAuthBackend):
    @cached_property
    def radius_dict(self) -> Dictionary:
        return Dictionary(str(Path(__file__).with_name("radius.dict")))

    def authenticate(self, user: str | None = None, password: str | None = None, **kwargs) -> str:
        radius_server = config.login.radius_server
        radius_secret = smart_bytes(config.login.radius_secret)

        client = Client(server=radius_server, secret=radius_secret, dict=self.radius_dict)
        req = client.CreateAuthPacket(code=AccessRequest, User_Name=user, NAS_Identifier="noc")
        req["User-Password"] = req.PwCrypt(password)
        try:
            reply = client.SendPacket(req)
        except Timeout:
            raise self.LoginError("Timed out")
        if reply.code != AccessAccept:
            raise self.LoginError("RADIUS Authentication failed. Code=%s", reply.code)
        return user
