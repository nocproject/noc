# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# RADIUS Authentication backend
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from pyrad.packet import AccessAccept, AccessRequest
from pyrad.client import Client
from pyrad.dictionary import Dictionary
# NOC modules
from noc.config import config
from .base import BaseAuthBackend


class RADIUSBackend(BaseAuthBackend):
    RADIUS_DICT = Dictionary(
        "services/login/backends/radius.dict"
    )

    def authenticate(self, user=None, password=None, **kwargs):
        radius_server = config.login.radius_server
        radius_secret = config.login.radius_secret

        client = Client(
            server=radius_server,
            secret=radius_secret,
            dict=self.RADIUS_DICT
        )
        req = client.CreateAuthPacket(
            code=AccessRequest,
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
