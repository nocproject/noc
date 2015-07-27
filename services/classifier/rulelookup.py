# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Rule lookup table
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class RuleLookup(object):
    def __init__(self, rules):
        self.rules = rules

    def lookup_rules(self, msg):
        """
        Returns a list of events to lookup
        """
        return self.rules
