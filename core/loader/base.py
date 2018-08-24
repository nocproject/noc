# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseLoader class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import inspect
# NOC modules
from noc.core.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class BaseLoader(object):
    name = None

    def __init__(self):
        self.logger = PrefixLoggerAdapter(logger, self.name)

    def find_class(self, module_name, base_cls, name):
        """
        Load subclass of *base_cls* from module

        :param module_name: String containing module name
        :param base_cls: Base class
        :param name: object name
        :return: class reference or None
        """
        try:
            sm = __import__(module_name, {}, {}, "*")
            for n in dir(sm):
                o = getattr(sm, n)
                if (
                    inspect.isclass(o) and
                    issubclass(o, base_cls) and
                    o.__module__ == sm.__name__
                ):
                    return o
        except ImportError as e:
            self.logger.error("Failed to load %s %s: %s", self.name, name, e)
        return None
