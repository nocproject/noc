# -*- coding: utf-8 -*-
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
from base import BaseValidator

logger = logging.getLogger(__name__)


class CLIPSValidator(BaseValidator):
    # String or list of strings containing CLIPS defrule statements
    RULES = None

    def get_context(self):
        """
        Returns context for template expansion
        """
        num = self.engine.get_rule_number()
        name = "%s.%s-%s" % (
            self.__class__.__module__, self.__class__.__name__, num
        )
        name = name.replace(".", "-")
        return {
            "RULENUM": num,
            "RULENAME": name
        }

    def add_rule(self, rule):
        t = Template(rule).render(Context(self.get_context()))
        logger.debug("ADD RULE: %s", t)
        self.engine.add_rule(t)

    def prepare(self, **kwargs):
        if isinstance(self.RULES, (list, tuple)):
            for r in self.RULES:
                self.add_rule(r)
        else:
            self.add_rule(self.RULES)
