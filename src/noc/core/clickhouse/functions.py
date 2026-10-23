# ----------------------------------------------------------------------
# ClickHouse functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class AggregateFunction:
    db_name = None

    def __init__(self, function: str | None = None, **params) -> None:
        self.function = self.db_name or function
        self.params = params

    def __repr__(self) -> str:
        return self.function

    # get expression
    def get_expression(self, field, combinator: str | None = None, **params):
        expr = field.expression
        if combinator == "Merge":
            expr = field.name
        return f"{self.function}{combinator or ''}({expr})"

    def get_db_type(self, field):
        return field.get_db_type()


class ArgMax(AggregateFunction):
    db_name = "argMax"

    def get_expression(self, field, combinator: str | None = None, **params):
        if combinator == "Merge":
            return f"{self.function}{combinator or ''}({field.name})"
        return f"{self.function}{combinator or ''}({field.expression}, ts)"

    def get_db_type(self, field):
        return f"{field.get_db_type()}, DateTime"
