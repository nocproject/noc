# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base TT System
##----------------------------------------------------------------------
## Copyright (C) 2007-2016, The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging


class BaseTTSystem(object):
    class TTError(Exception):
        pass

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
                  subject=None, body=None, login=None):
        """
        Create TT
        :param queue: ticket queue
        :param obj: Supported object's identifier
        :param reason: Preliminary reason
        :param subject: TT Subject
        :param body: TT body
        :param login: User login
        :returns: TT id as string
        :raises TTError:
        """
        raise NotImplementedError()

    def get_tt(self, tt_id):
        """
        Get TT information
        :param tt_id: TT id, as returned by create_tt
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
