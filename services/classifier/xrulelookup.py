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
import itertools
# Third-party modules
import esm
from pyparsing import *
# NOC modules
from noc.services.classifier.rulelookup import RuleLookup
from noc.core.perf import metrics


logger = logging.getLogger(__name__)

QSEP = "<<@>>"


class XRuleLookup(RuleLookup):
    _pattern_cache = {}
    _parser_cache = {}

    def __init__(self, rules):
        self.index = esm.Index()
        self.keyword_rules = defaultdict(set)  # keyword index -> {rules}
        self.rule_keywords = {}  # Rule -> {keyword indices}
        self.initialize(rules)
        super(XRuleLookup, self).__init__(rules)

    def initialize(self, rules):
        # Process all rules and insert keywords to index
        keyword_index = {}  # keyword -> index
        for rule in rules:
            keywords = set()
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
                        kwi = keyword_index.get(keyword)
                        if kwi is None:
                            kwi = len(keyword)
                            keyword_index[keyword] = kwi
                            self.index.enter(keyword, kwi)
                        keywords.add(kwi)
                # Update forward and back references
                self.rule_keywords[rule] = keywords
                for kwi in keywords:
                    self.keyword_rules[kwi].add(rule)
        # Finally fix index
        self.index.fix()

    def lookup_rules(self, event, vars):
        """
        Perform event lookup and return first matched rules
        """
        query = QSEP.join("%s%s%s" % (k, QSEP, vars[k]) for k in vars)
        metrics["esm_lookups"] += 1
        keywords = set(kwi for _, kwi in self.index.query(query))
        rules = itertools.chain(*tuple(self.keyword_rules[kwi] for kwi in keywords))
        matched = [rule for rule in rules if self.rule_keywords[rule] <= keywords]
        return sorted(matched, key=lambda y: y.preference)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_pattern_cache"))
    def parse_string(self, s):
        return self.get_parser().parseString(s)

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
