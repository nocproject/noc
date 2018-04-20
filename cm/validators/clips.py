# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# CLIPS rule-based validator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import re
# Django modules
from django.template import Template, Context
# NOC modules
=======
##----------------------------------------------------------------------
## CLIPS rule-based validator
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Django modules
from django.template import Template, Context
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from base import BaseValidator

logger = logging.getLogger(__name__)


class CLIPSValidator(BaseValidator):
    # String or list of strings containing CLIPS defrule statements
    RULES = None

<<<<<<< HEAD
    rx_assert_error = re.compile(
        r"\(assert\s+\(error\s+\(",
        re.MULTILINE | re.DOTALL
    )

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def get_context(self):
        """
        Returns context for template expansion
        """
        num = self.engine.get_rule_number()
        name = "%s.%s-%s" % (
            self.__class__.__module__, self.__class__.__name__, num
        )
        name = name.replace(".", "-").lower()
        r = self.get_config()
        r.update({
            "RULENUM": num,
<<<<<<< HEAD
            "RULENAME": name,
            "RULEID": self.rule_id
=======
            "RULENAME": name
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        })
        return r

    def add_rule(self, rule):
        ctx = self.get_context()
        # CLIPS Escape
        for n in ctx:
            v = ctx[n]
            if isinstance(v, basestring):
                v = v.replace("\\", "\\\\").replace("\"", "\\\"")
                ctx[n] = v
<<<<<<< HEAD
        # Insert rule number to (assert (error ..))
        match = self.rx_assert_error.search(rule)
        if match:
            mr = match.group(0) + "rule \"{{RULEID}}\") ("
            rule = rule[:match.start()] + mr + rule[match.end():]
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        #
        t = Template(rule).render(Context(ctx))
        logger.debug("ADD RULE: %s", t)
        self.engine.add_rule(t)

    def prepare(self, **kwargs):
        if isinstance(self.RULES, (list, tuple)):
            for r in self.RULES:
                self.add_rule(r)
        else:
            self.add_rule(self.RULES)
