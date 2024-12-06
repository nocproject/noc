# ----------------------------------------------------------------------
# MatcherRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.matcher import match
from .loader import load_rule


class MatcherRule(object):
    """
    Multiple items for single metric
    """

    name = "match"

    def __init__(self, oids, matchers):
        self.oids = oids
        self.matchers = matchers

    def iter_oids(self, script, metric):
        ctx = script.version
        for matcher, rule in self.oids:
            # match(ctx, []) always True, Priority in metrics matcher config matcher
            if (
                matcher is None
                or (match(ctx, self.matchers.get(matcher, {})) and matcher in self.matchers)
                or getattr(script, matcher, None)
            ):
                yield from rule.iter_oids(script, metric)
                # Only one match
                break

    @classmethod
    def from_json(cls, data):
        if "$match" not in data:
            raise ValueError("Matcher is required")
        if not isinstance(data["$match"], list):
            raise ValueError("$match must be list")
        return MatcherRule(
            oids=[(d.get("$match"), load_rule(d)) for d in data["$match"]],
            matchers=data.get("$matchers", {}),
        )
