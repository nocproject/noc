# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## BI Extractor
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime


class BaseExtractor(object):
    """
    Extract data between timestamps
    """
    name = None
    # Time in seconds to delay extraction
    extract_delay = 0
    # Time in seconds to delay cleaning
    # counting from last extraction
    clean_delay = 0

    def __init__(self, prefix, start, stop):
        self.prefix = prefix
        self.start = start
        self.stop = stop
        self.clean_ts = stop - datetime.timedelta(seconds=self.clean_delay)
        self.last_ts = None

    def extract(self):
        pass

    def clean(self):
        pass

    @classmethod
    def get_start(cls):
        """
        Returns timestamp of first record
        or None when no data found
        :return:
        """
        return None
