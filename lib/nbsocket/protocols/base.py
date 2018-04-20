# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Abstract PDU parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class Protocol(object):
    """
    Abstract protocol parser. Accepts raw data via feed() method,
    populating internal buffer and calling parse_pdu()
    """
    def __init__(self, parent, callback):
        """
        :param parent: Socket instance
        :param callback: Callable accepting single pdu argument
        """
        self.parent = parent
        self.callback = callback
        self.in_buffer = ""

    def feed(self, data):
        """
        Feed raw data into protocols. Calls callback for each
        completed PDU.

        :param data: Raw data portion
        :type data: str
        """
        self.in_buffer += data
        for pdu in self.parse_pdu():
            self.callback(pdu)

    def parse_pdu(self):
        """
        Scan self.in_buffer, detect all completed PDUs, then remove
        them from buffer and return as list or yield them

        :return: List of PDUs
        :rtype: list
        """
        return []
