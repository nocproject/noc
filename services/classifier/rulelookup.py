# ---------------------------------------------------------------------
# Rule lookup table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator


class RuleLookup(object):
    def __init__(self, rules):
        self.rules = rules

    def lookup_rules(self, msg, vars):
        """
        Returns a list of events to lookup
        """
        return self.rules

    def delete_rule(self, rid: str):
        """Remove Rules from Chain"""
        rules = []
        for r in self.rules:
            if r.id == rid:
                continue
            rules.append(r)
        if len(rules) != len(rules):
            self.rules = rules

    def update_rule(self, rule):
        """Replace Rules on chain"""
        changed, rules = False, []
        for r in self.rules:
            if r.id == rule.id:
                rules.append(rule)
                changed |= True
                continue
            rules.append(r)
        if changed:
            self.rules = rules
        return changed

    def add_rule(self, rule):
        """Add Rule to Chain"""
        self.rules = sorted(self.rules + [rule], key=operator.attrgetter("preference"))
