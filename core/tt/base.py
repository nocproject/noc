# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Base TT System
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017, The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
# NOC modules
from .error import TTError, TemporaryTTError


class BaseTTSystem(object):
    promote_group_tt = False

    TTError = TTError
    TemporaryTTError = TemporaryTTError

    def __init__(self, name, connection):
        """
        Initialize TT System
        :param name: TT System name
        :param connection: Connection settings string, as defined
            in TTSystem.connection
        """
        self.connection = connection
        self.name = name
        self.logger = logging.getLogger("tt.%s" % self.name)

    def create_tt(self, queue, obj, reason=None,
                  subject=None, body=None, login=None,
                  timestamp=None):
        """
        Create TT
        :param queue: ticket queue
        :param obj: Supported object's identifier
        :param reason: Preliminary reason
        :param subject: TT Subject
        :param body: TT body
        :param login: User login
        :param timestamp: Escalated alarm timestamp
        :returns: TT id as string
        :raises TTError:
        """
        raise NotImplementedError()

    def get_tt(self, tt_id):
        """
        Get TT information
        :param tt_id: TT id, as returned by create_tt
        :returns: dict with keys
            *tt_id* - tt id
            *queue* - internal queue id
            *obj* - Supported object's identifier
            *resolved* - True if TT has been resolved
            *stage_id* - Current TT stage id (in terms of external system)
            *stage* - Current TT stage text
            *open_ts* - TT creation timestamp
            *close_ts* - TT closing timestamp (only if resolved)
            *stage_ts* - Current stage starting timestamp
            *owner* - Login of TT owner (if any)
            *dept* - Department currently holding TT (only if not resolved)
            *close_dept* - Department which closed TT (only for resolved)
            *pre_reason_id* - Internal pre reason id
            *pre_reason* - Pre-reason name
            *final_reason_id* - Internal final reason id
            *final_reason* - Final reason name
            *subject* - TT subject
            *body* - TT body
            *comments*: dict of TT comments
                *id* - Comment id
                *reply_to* - id of parent comment
                *ts* - timestamp
                *login* - Login of user leaving comment
                *subject* - Comment subject
                *body* - Comment body
        :raises TTError:
        """
        raise NotImplementedError()

    def get_object_tts(self, obj):
        """
        Get list of TTs, open for object obj
        :param obj: Supported object id, as passed to create_tt
        :raises TTError:
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

    def add_comment(self, tt_id, subject=None, body=None, login=None):
        """
        Append comment to TT
        :param tt_id: TT id, as returned by create_tt
        :param subject: Closing message subject
        :param body: Closing message body
        :param login: User login
        :raises TTError:
        """
        raise NotImplementedError()

    def create_group_tt(self, tt_id, timestamp=None):
        """
        Promote tt as the group tt.
        Called only when promote_group_tt is set
        :param tt_id: tt_id as returned by create_tt
        """
        raise NotImplementedError()

    def add_to_group_tt(self, gtt_id, obj):
        """
        Add object to the group tt
        :param gtt_id: Group tt id, as returned by create_group_tt
        :param obj: Supported object's identifier
        """
        raise NotImplementedError()
