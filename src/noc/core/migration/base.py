# ----------------------------------------------------------------------
# BaseMigration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# NOC modules
from noc.core.mongo.connection import get_db, Database
from .db import db


class BaseMigration:
    depends_on: list[tuple[str, str]] = []
    db = db
    aliases: list[str] | None = None

    def __init__(self) -> None:
        # @todo: set_comprehensions
        self.dependencies = {f"{x[0]}.{x[1]}" for x in self.depends_on}

    def __str__(self) -> str:
        return self.get_name()

    def add_dependency(self, name: str) -> None:
        self.dependencies.add(name)

    def is_resolved(self, dependencies: set[str]) -> bool:
        """
        Check if all dependencies are resolved.

        Args:
            dependencies: Set of seen dependencies

        Returns:
            True: if all dependencies are resolved.
        """
        return not bool(self.dependencies - dependencies)

    def is_applied(self, applied: set[str]) -> bool:
        """
        Check if migration is applied.

        Args:
            applied: Set of already applied migrations.

        Returns:
            True: if migration is already applied.
        """
        return self.get_name() in applied or (
            bool(self.aliases) and any(a in applied for a in self.aliases)
        )

    @classmethod
    def get_name(cls) -> str:
        parts = cls.__module__.split(".")
        return f"{parts[1]}.{parts[3]}"

    @property
    def mongo_db(self) -> Database:
        return get_db()

    def migrate(self) -> None:
        """Actual migration code."""
