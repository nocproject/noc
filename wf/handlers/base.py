# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base handlers model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import math
import random
## NOC modules
from noc.sa.interfaces import Parameter


class ExprParameter(Parameter):
    pass


class ContextVarParameter(Parameter):
    pass


class ContextRef(object):
    def __init__(self, process, name):
        self.process = process
        self.name = name

    def get(self):
        return self.process.context.get(self.name)

    def set(self, value):
        self.process.update_context(self.name, value)


class BaseHandler(object):
    #
    # Mapping of parameter name -> Parameter() instance
    #
    params = {}
    #
    # When False - follow next_node
    # When True - follow next_true_node when handler returns True
    #           - follow next_false_node otherwise
    #
    conditional = False

    GLOBALS = {
        "math": math,
        "random": random
    }

    def info(self, msg):
        logging.info(msg)

    def debug(self, msg):
        logging.debug(msg)

    def handler(self, process, node, *args, **kwargs):
        raise NotImplementedError()

    def run(self, process, node):
        # Calculate node params
        ctx = {}
        for p in self.params:
            v = node.params[p]
            if isinstance(self.params[p], ExprParameter):
                # Evaluate expression
                ctx[p] = eval(v, self.GLOBALS, process.context)
            elif isinstance(self.params[p], ContextVarParameter):
                # Return context reference
                ctx[p] = ContextRef(process, v)
            else:
                ctx[p] = self.params[p].clean(v)
        # Execute handler
        return self.handler(process, node, **ctx)
