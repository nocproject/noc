# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Time-series database partition
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class Partition(object):
    name = None

    @classmethod
    def get_name(cls, timestamp):
        """
        Get partition name for timestamp
        :param timestamp: integer timestamp
        """
        raise NotImplementedError()

    @classmethod
    def enumerate(cls, start, end):
        """
        Yield all partitions from start to end
        Generator yields partition name, start and end timestamps
        :param start: integer start timestamp
        :param end: integer end timestamp
        """
        raise NotImplementedError
