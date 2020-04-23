# ----------------------------------------------------------------------
# ConfDB
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
# from ..syntax import SYNTAX
from .node import Node
from .marshall.loader import loader


class ConfDB(object):
    def __init__(self):
        self.db = Node(None)

    def insert(self, tokens):
        """
        Put tokens to database
        :param tokens: tuple of tokens
        :return:
        """
        self.db.insert(tokens)

    def insert_bulk(self, iter):
        """
        Put tokens from iterator
        :param iter: iterator
        :return:
        """
        for tokens in iter:
            self.insert(tokens)

    def marshall(self, marshaller="tree"):
        mcls = loader.get_class(marshaller)
        return mcls.marshall(self.db)

    def unmarshall(self, data, marshaller):
        mcls = loader.get_class(marshaller)
        self.db = mcls.unmarshall(data)
