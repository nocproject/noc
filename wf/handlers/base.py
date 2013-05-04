# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base handlers model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging


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

    def info(self, msg):
        logging.info(msg)

    def debug(self, msg):
        logging.debug(msg)

    def handler(self, process, node):
        raise NotImplementedError()

    def run(self, process, node):
        # Calculate node params
        ctx = {}
        for p in self.params:
            v = node.params[p]
            if v.startswith("constant:"):
                x = v[9:]
            else:
                x = process.context.get(v)
            ctx[p] = self.params[p].clean(x)
        # Execute handler
        return self.handler(process, node, **ctx)
