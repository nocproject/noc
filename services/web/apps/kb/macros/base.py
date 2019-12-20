# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Macros Framework
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# Args regular expression
rx_args = re.compile(r"\s*(?P<attr>\S+)\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)")


class BaseMacro(object):
    name = None

    @classmethod
    def parse_args(cls, args):
        """
        Converts a string of html-like attributes to hash
        :param args:
        :return:
        """
        if isinstance(args, dict):
            return args
        return dict((m[0], m[2]) for m in rx_args.findall(args))

    @classmethod
    def expand(cls, args, text):
        """
        Decodes args and calls handle method
        :param args:
        :param text:
        :return:
        """
        return cls.handle(cls.parse_args(args), text)

    @classmethod
    def handle(cls, args, text):
        """
        Specific macro handler to be overriden in child classes
        Accepts a hash of args and text and returns formatted HTML
        to be included in output
        """
        raise NotImplementedError
