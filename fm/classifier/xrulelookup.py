## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Accelerated Rule Lookup
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
import re
import logging
## Third-party modules
import esm
from pyparsing import *
## NOC modules
from rulelookup import RuleLookup


logger = logging.getLogger(__name__)


class XRuleLookup(RuleLookup):
    RE_SEP = "\x00RE@SEP\x00"

    def __init__(self, rules):
        super(XRuleLookup, self).__init__(rules)
        self.l_index = None
        self.r_index = {}
        self.cond_rules = defaultdict(set)  # Condition -> [Rules]
        self.rule_cond = {}  # Rule -> {conditions}
        self.conditions = {}  # id -> (left_re, right_re)
        self.parser = parser
        self.initialize(rules)

    def enter(self, index, regex, obj):
        def is_applicable(h):
            if not h:
                return False
            return len([c for c in h if c in alphanums]) > 1

        hints = [
            h for h
            in "".join(self.parser.parseString(regex))
                .replace("\\", "")
                .split(self.RE_SEP)
            if is_applicable(h)
        ]
        for hint in hints:
            index.enter(hint, obj)

    def initialize(self, rules):
        self.l_index = esm.Index()
        conds = {}  # (left, right) -> condition
        lpatterns = {}  # Left
        for rule in rules:
            rc = set()
            for p in rule.rule.patterns:
                if p.key_re in ("source", "^source$",
                                "profile", "^profile$"):
                    continue
                pd = (p.key_re, p.value_re)
                cond = conds.get(pd)
                if not cond:
                    cond = len(conds)
                    conds[pd] = cond
                    self.conditions[cond] = (
                        p.key_re,
                        p.value_re
                    )
                    li = lpatterns.get(p.key_re)
                    if not li:
                        li = len(lpatterns)
                        lpatterns[p.key_re] = li
                        self.enter(self.l_index, p.key_re, li)
                        self.r_index[li] = esm.Index()
                    self.enter(self.r_index[li], p.value_re, cond)
                rc.add(cond)
            self.rule_cond[rule] = rc
            for c in rc:
                self.cond_rules[c].add(rule)
        # Fix all indexes
        self.l_index.fix()
        for i in self.r_index.itervalues():
            i.fix()

    def lookup_rules(self, event):
        """
        Perform event lookup and return first matched rules
        """
        msg = event.raw_vars
        conds = set()
        for k in msg:
            for _, x in self.l_index.query(k):
                conds.update(y for _, y in self.r_index[x].query(msg[k]))
        matched = set()
        for c in conds:
            for rule in self.cond_rules[c]:
                rc = self.rule_cond[rule]
                if rc <= conds:
                    matched.add(rule)
        return sorted(matched, key=lambda y: y.preference)

    @classmethod
    def get_parser(cls):
        """
        Python regex parser
        """
        def ignore(tokens):
            return cls.RE_SEP

        # ParserElement.setDefaultWhitespaceChars("")
        macro_codes = "AbBdDsSwWZ0123456789"
        literal_chars = [c for c in printables if c not in r"\[]{}().*?+|$^"] + list(" \t")
        LBRACK, RBRACK, LBRACE, RBRACE, LPAREN, RPAREN, PIPE = map(Literal, "[]{}()|")
        MACRO = Combine("\\" + oneOf(list(macro_codes))).setParseAction(ignore)
        ESCAPED = Combine("\\" + oneOf([c for c in printables if c not in macro_codes]))
        LITERAL = (ESCAPED | oneOf(list(literal_chars))).leaveWhitespace()
        RANGE = Combine(LBRACK + SkipTo(RBRACK, ignore=ESCAPED) + RBRACK).setParseAction(ignore)
        REPETITION = (
            (LBRACE + Word(nums) + RBRACE) |
            (LBRACE + Word(nums) + "," + Word(nums) + RBRACE) |
            (oneOf(list("*+?")) + Optional(Literal("?")))
        )
        SPECIAL = oneOf(list(".^$")).setParseAction(ignore)
        GROUP_OPT = Literal("?") + (oneOf(list("iLmsux:#=!<P")))

        RE = Forward()
        GROUP = (LPAREN + Optional(GROUP_OPT) + RE + RPAREN).setParseAction(ignore)
        ELEMENTARY_RE = (LITERAL | MACRO | RANGE | SPECIAL | GROUP)
        SIMPLE_RE = OneOrMore((ELEMENTARY_RE + REPETITION).setParseAction(ignore) | ELEMENTARY_RE).leaveWhitespace()
        RE << SIMPLE_RE + ZeroOrMore(PIPE + RE)
        return RE

## Global parser
parser = XRuleLookup.get_parser()