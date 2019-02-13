# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Var
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class Var(object):
    def __init__(self, name):
        self.name = name

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
