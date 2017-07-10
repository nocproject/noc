# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# RADIUS Authentication backend
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from pyrad.packet import AccessAccept
from pyrad.client import Client
from pyrad.dictionary import Dictionary
# NOC modules
from base import BaseAuthBackend


class RADIUSBackend(BaseAuthBackend):
    RADIUS_DICT = Dictionary(
        "service/login/backends/radius.dict"
    )

    def authenticate(self, user=None, password=None, **kwargs):
        radius_server = self.service.config.radius_server
        radius_secret = self.service.config.radius_secret

        client = Client(
            server=radius_server,
            secret=radius_secret,
            dict=self.RADIUS_DICT
        )
        req = client.CreateAuthPacket(
            code=packet.AccessRequest,
            User_Name=user,
            NAS_Identifier="noc"
        )
        req["User-Password"] = req.PwCrypt(password)
        try:
            reply = client.SendPacket(req)
        except client.Timeout:
            raise self.LoginError("Timed out")
        if reply.code != AccessAccept:
            raise self.LoginError(
                "RADIUS Authentication failed. Code=%s", reply.code
            )
        return user
