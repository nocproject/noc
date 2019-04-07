# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Node
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class Node(object):
    __slots__ = ["token", "children"]

    def __init__(self, token):
        self.token = token
        self.children = None

    def __repr__(self):
        return "<Node %s>" % self.token

    def find(self, token):
        """
        Find children Node by token

        :param token: token as string
        :return: Child Node or None
        """
        if not self.children:
            return None
        return self.children.get(token)

    @staticmethod
    def clean_token(token):
        if isinstance(token, bool):
            return "on" if token else "off"
        return str(token)

    def insert(self, tokens):
        """
        Populate children with tokens
        :param tokens: tuple of tokens
        :return: None
        """
        if self.children is None:
            self.children = {}
        token = self.clean_token(tokens[0])
        to_replace = False
        if len(tokens) == 2 and isinstance(tokens[1], dict):
            cfg = tokens[1]
            tokens = None
            to_replace = cfg.get("replace", False)
        cn = self.children.get(token)
        if not cn:
            cn = Node(token)
            if to_replace and self.children:
                self.children = {token: cn}
            else:
                self.children[token] = cn
        if tokens and len(tokens) > 1:
            cn.insert(tokens[1:])

    def iter_nodes(self):
        if self.children:
            for name in sorted(self.children):
                yield self.children[name]

    def has_children(self):
        return bool(self.children)

    def trim(self):
        self.children = None
