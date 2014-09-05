# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Basic poller class
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class Poller(object):
    def add_reader(self, sock):
        """
        Add reader to poller
        :param sock: Socket instance
        :type sock: Socket
        :return:
        """

    def add_writer(self, sock):
        """
        Add writer to poller
        :param sock: Socket instance
        :type sock: Socket
        :return:
        """

    def remove_reader(self, sock):
        """
        Remove reader from poller
        :param sock: Socket instance
        :type sock: Socket
        :return:
        """

    def remove_writer(self, sock):
        """
        Remove writer from poller
        :param sock: Socket instance
        :type sock: Socket
        :return:
        """

    def get_active(self, timeout):
        """
        Returns a tuple of active [readers], [writers]
        :return:
        """
