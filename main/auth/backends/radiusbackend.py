# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RADIUS Authentication backend
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import settings
import logging
import types
## Third-party modules
try:
    import pyrad.packet
    from pyrad.client import Client
    from pyrad.dictionary import Dictionary
except ImportError:
    pass
## NOC modules
from base import NOCAuthBackend
from noc.settings import config


class NOCRadiusBackend(NOCAuthBackend):
    """
    RADIUS Authentication backend
    """
    def __init__(self):
        super(NOCRadiusBackend, self).__init__()
        self.server = config.get("authentication", "radius_server")
        self.secret = config.get("authentication", "radius_secret")
        self.nas_identifier = config.get("authentication", "radius_nas_identifier")
        self.superuser_attribute = config.get("authentication", "radius_superuser_attribute")
        self.superuser_value = config.get("authentication", "radius_superuser_value")

    def authenticate(self, username=None, password=None, **kwargs):
        """
        Authenticate user against user and password
        """
        logging.debug("RADIUS authenticatation: username=%s" % username)
        is_active = True  # User activity flag
        is_superuser = False  # Superuser flag
        
        srv=Client(server=self.server, secret=self.secret,
              dict=Dictionary("main/auth/backends/radiusbackend.dict"))

        req=srv.CreateAuthPacket(code=pyrad.packet.AccessRequest,
                      User_Name=username, NAS_Identifier=self.nas_identifier)
        req["User-Password"]=req.PwCrypt(password)

        reply=srv.SendPacket(req)
        if reply.code==pyrad.packet.AccessAccept:
            logging.debug("RADIUS access accepted for '%s'" % username)
        else:
            logging.debug("RADIUS access denied for '%s'" % username)
            return None
        
        logging.debug("RADIUS Attributes returned by server: %s" % reply)

        logging.debug("RADIUS Check superuser_value of superuser_attribute '%s' to contain '%s'" % (self.superuser_attribute, self.superuser_value))
        for i in reply.keys():
            if str(i) == self.superuser_attribute and self.superuser_value in reply[i]:
                is_superuser = True
        
        # Successfull bind
        user = self.get_or_create_db_user(username=username,
                                          is_active=is_active,
                                          is_superuser=is_superuser)

        # Authentication passed
        return user
