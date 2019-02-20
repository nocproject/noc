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

    def insert(self, tokens):
        """
        Populate children with tokens
        :param tokens: tuple of tokens
        :return: None
        """
        if self.children is None:
            self.children = {}
        token = tokens[0]
        cn = self.children.get(token)
        if not cn:
            cn = Node(token)
            self.children[token] = cn
        if len(tokens) > 1:
            cn.insert(tokens[1:])

    def iter_nodes(self):
        if self.children:
            for name in sorted(self.children):
                yield self.children[name]
