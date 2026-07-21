# ----------------------------------------------------------------------
# CloningRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.services.classifier.exception import InvalidPatternException


class CloningRule:
    class Pattern:
        def __init__(self, key_re, value_re) -> None:
            self.key_re = key_re
            self.value_re = value_re

        def __str__(self):
            return f"{self.key_re} : {self.value_re}"

    def __init__(self, rule) -> None:
        self.re_mode = rule.re != r"^.*$"  # Search by "re"
        self.name = rule.name
        try:
            self.re = re.compile(rule.re)
        except Exception as why:
            raise InvalidPatternException(f"Error in '{rule.re}': {why}")
        try:
            self.key_re = re.compile(rule.key_re)
        except Exception as why:
            raise InvalidPatternException(f"Error in '{rule.key_re}': {why}")
        try:
            self.value_re = re.compile(rule.value_re)
        except Exception as why:
            raise InvalidPatternException(f"Error in '{rule.value_re}': {why}")
        try:
            self.rewrite_from = re.compile(rule.rewrite_from)
        except Exception as why:
            raise InvalidPatternException(f"Error in '{rule.rewrite_from}': {why}")
        self.rewrite_to = rule.rewrite_to

    def match(self, rule):
        """
        Check cloning rule matches classification rule
        """
        if self.re_mode:
            return any(
                x
                for x in rule.rule.patterns
                if self.re.search(x.key_re) or self.re.search(x.value_re)
            )
        return any(
            x
            for x in rule.rule.patterns
            if self.key_re.search(x.key_re) and self.value_re.search(x.value_re)
        )

    def rewrite(self, pattern):
        return CloningRule.Pattern(
            self.rewrite_from.sub(self.rewrite_to, pattern.key_re),
            self.rewrite_from.sub(self.rewrite_to, pattern.value_re),
        )
