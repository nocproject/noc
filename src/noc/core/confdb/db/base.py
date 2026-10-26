# ----------------------------------------------------------------------
# ConfDB
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
# from ..syntax import SYNTAX
from .marshall.base import marshaller_loader
from .node import Node


class ConfDB:
    def __init__(self) -> None:
        self.db = Node(None)

    def insert(self, tokens):
        """Put tokens to database

        Args:
            tokens: tuple of tokens
        """
        self.db.insert(tokens)

    def insert_bulk(self, iter):
        """Put tokens from iterator

        Args:
            iter: iterator
        """
        for tokens in iter:
            self.insert(tokens)

    def marshall(self, marshaller="tree"):
        mcls = marshaller_loader.get(marshaller)
        return mcls.marshall(self.db)

    def unmarshall(self, data, marshaller):
        mcls = marshaller_loader.get(marshaller)
        self.db = mcls.unmarshall(data)
