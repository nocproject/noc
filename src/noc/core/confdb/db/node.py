# ----------------------------------------------------------------------
# Node
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.text import alnum_key


class Node:
    __slots__ = ["children", "token"]

    def __init__(self, token) -> None:
        self.token = token
        self.children = None

    def __repr__(self) -> str:
        return f"<Node {self.token}>"

    def find(self, token):
        """Find children Node by token

        Args:
            token: token as string

        Returns:
            Child Node or None
        """
        if not self.children:
            return None
        return self.children.get(token)

    def find_path(self, tokens):
        """Recursively find by path

        Args:
            tokens: Iterable containing tokens
        """
        current = self
        for p in tokens:
            current = current.find(p)
            if not current:
                return None
        return current

    def merge_children(self, children):
        """Apply children

        Args:
            children: Dict of children
        """
        if not children:
            return
        if not self.children:
            self.children = {}
        self.children.update(children)

    @staticmethod
    def clean_token(token):
        return token

    def insert(self, tokens):
        """Populate children with tokens

        Args:
            tokens: tuple of tokens

        Returns:
            Inserted node
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
            return cn.insert(tokens[1:])
        return cn

    def iter_nodes(self):
        if self.children:
            for name in sorted(self.children, key=lambda x: alnum_key(str(x or ""))):
                yield self.children[name]

    def has_children(self):
        return bool(self.children)

    def trim(self):
        self.children = None
