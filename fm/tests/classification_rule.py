# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Check classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.lib.test import NOCTestCase
from noc.fm.models import EventClassificationRule


class ClassificationRuleTestCase(NOCTestCase):
    def test_patterns(self):
        def check_re(r, s):
            try:
                re.compile(s)
            except re.error, why:
                errors += ["%s: %s: %s" % (r.name, s, why)]

        errors = []
        for rule in EventClassificationRule.objects.all():
            for left, right in rule.patterns:
                check_re(rule, left)
                check_re(rule, right)
        l = len(errors)
        assert not l, ("%d errors in classification rules:\n\t%s" % (l,
                                                        "\n\t".join(errors)))
