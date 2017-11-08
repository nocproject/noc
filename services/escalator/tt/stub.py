# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
#  Stub TT System
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import logging
# Python modules
import uuid

# NOC modules
from noc.core.tt.base import BaseTTSystem


class StubTTSystem(BaseTTSystem):
    """
    Stub TT system responds as a valid one, generating unique TT ids.
    For debugging purposes only
    """
    promote_group_tt = True

    def __init__(self, name, connection):
        self.logger = logging.getLogger("StubTTSystem.%s" % name)
        pass

    def create_tt(self, queue, obj, reason=None,
                  subject=None, body=None, login=None, timestamp=None):
        self.logger.info(
            "create_tt(queue=%s, obj=%s, reason=%s, subject=%s, body=%s, login=%s, timestamp=%s)",
            queue, obj, reason, subject, body, login, timestamp
        )
        return str(uuid.uuid4())

    def add_comment(self, tt_id, subject=None, body=None, login=None):
        self.logger.info(
            "add_comment(tt_id=%s, subject=%s, body=%s, login=%s)",
            tt_id, subject, body, login
        )
        return True

    def create_group_tt(self, tt_id, timestamp=None):
        """
        Promote tt as the group tt.
        Called only when promote_group_tt is set
        :param tt_id: tt_id as returned by create_tt
        """
        return tt_id

    def add_to_group_tt(self, gtt_id, obj):
        """
        Add object to the group tt
        :param gtt_id: Group tt id, as returned by create_group_tt
        :param obj: Supported object's identifier
        """
        self.logger.info("Object %s appended to group TT %s", obj, gtt_id)

    def close_tt(self, tt_id, subject=None, body=None,
                 reason=None, login=None):
        """
        Close TT
        :param tt_id: TT id, as returned by create_tt
        :param subject: Closing message subject
        :param body: Closing message body
        :param reason: Final reason
        :param login: User login
        :returns: Boolean. True, when alarm is closed properly
        :raises TTError:
        """
        self.logger.info("TT %s closed", tt_id)
