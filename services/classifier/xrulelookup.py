# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Accelerated Rule Lookup
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import operator
import logging
import cachetools
# Third-party modules
import esm
from pyparsing import *
import bitarray
# NOC modules
from noc.services.classifier.rulelookup import RuleLookup
from noc.core.perf import metrics


logger = logging.getLogger(__name__)

QSEP = "<<@>>"


class XRuleLookup(RuleLookup):
    _pattern_cache = {}
    _parser_cache = {}

    def __init__(self, rules):
        super(XRuleLookup, self).__init__(sorted(rules, key=lambda x: x.preference))
        self.index = esm.Index()
        self.kwmask = None
        self.rule_masks = []
        self.initialize(rules)

    def initialize(self, rules):
        kw_rules = defaultdict(set)
        rule_masks = {}
        # Collect keyword -> {rules} bindings
        for rule in rules:
            for p in rule.rule.patterns:
                if p.key_re in ("source", "^source$",
                                "profile", "^profile$"):
                    continue
                # Split to keywords
                for pattern in (p.key_re, p.value_re):
                    ps = "".join(self.parse_string(pattern))
                    ps = ps.replace("\\", "")
                    for keyword in ps.split(QSEP):
                        if not keyword:
                            continue
                        if not any(c for c in keyword if c in alphanums):
                            continue
                        kw_rules[keyword].add(rule)
        self.kwmask = bitarray.bitarray(len(kw_rules))
        self.kwmask.setall(False)
        # Initialize rule keyword masks
        for rule in rules:
            rule_masks[rule] = self.kwmask.copy()
        # Fill index
        for kwi, keyword in enumerate(kw_rules):
            self.index.enter(keyword, kwi)
            for rule in kw_rules[keyword]:
                rule_masks[rule][kwi] = 1
        self.index.fix()
        #
        for rule in rules:
            self.rule_masks += [(rule, rule_masks[rule])]

    def lookup_rules(self, event, vars):
        """
        Perform event lookup and return first matched rules
        """
        query = QSEP.join("%s%s%s" % (k, QSEP, vars[k]) for k in vars)
        metrics["esm_lookups"] += 1
        kwm = self.kwmask.copy()
        for _, kwi in self.index.query(query):
            kwm[kwi] = 1
        return [
            rule for rule, mask in self.rule_masks
            if mask & kwm == mask
        ]

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_pattern_cache"))
    def parse_string(cls, s):
        return cls.get_parser().parseString(s)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_parser_cache"))
    def get_parser(cls):
        """
        Python regex parser
        """
        def ignore(tokens):
            return QSEP

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

# Global parser
parser = XRuleLookup.get_parser()
