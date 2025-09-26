# ---------------------------------------------------------------------
# Accelerated Rule Lookup
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import operator
import logging
import cachetools
import sre_parse

# Third-party modules
# Manually setup esmre==1.0.0
try:
    import esmre as esm
except (ModuleNotFoundError, ImportError):
    raise NotImplementedError(
        "XRuleLookup needed ESMRE library for worked. Please, install it from pip"
    )
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
        super().__init__(sorted(rules, key=lambda x: x.preference))
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
                if p.key_re in ("source", "^source$", "profile", "^profile$"):
                    continue
                # Split to keywords
                for pattern in (p.key_re, p.value_re):
                    for keyword in self.parse(pattern):
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
        for rule, mask in self.rule_masks:
            if mask & kwm == mask:
                yield rule

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_pattern_cache"))
    def parse(cls, s):
        keywords = []
        current = []
        quoted = False
        for t, x in sre_parse.parse(s):
            if t == "literal":
                if x == 92:  # \
                    if quoted:
                        current += ["\\"]
                        quoted = False
                    else:
                        quoted = True
                else:
                    current += [chr(x)]
            elif current:
                keywords += ["".join(current)]
                current = []
        if current:
            keywords += ["".join(current)]
        return keywords
