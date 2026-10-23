# ----------------------------------------------------------------------
# Var
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class Var:
    def __init__(self, name) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Var '{self.name}' at {id(self)}>"

    def get(self, ctx):
        return ctx.get(self.name)

    def set(self, ctx, value):
        if not self.is_placeholder:
            ctx[self.name] = value

    def is_bound(self, ctx):
        return self.name in ctx

    @property
    def is_placeholder(self):
        return self.name.startswith("_")
