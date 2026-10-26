# ----------------------------------------------------------------------
# BaseMigration
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pathlib import Path

# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.config import config
from noc.core.mongo.connection import Database, get_db
from noc.settings import INSTALLED_APPS

from .db import db


def _has_migrations(app: str) -> bool:
    """Check whether an application has a repository or custom migrations package."""
    custom_path = Path(config.path.custom_path) if config.path.custom_path else None
    for path in config.get_customized_paths(app, "migrations"):
        root = Path(path)
        is_custom = custom_path is not None and root.is_relative_to(custom_path)
        if not root.is_absolute() and not is_custom:
            root = config.noc_base / root
        if root.is_dir():
            return True
    return False


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
        return f"{parts[-3]}.{parts[-1]}"

    @property
    def mongo_db(self) -> Database:
        return get_db()

    def migrate(self) -> None:
        """Actual migration code."""


migration_loaders: dict[str, Loader[type[BaseMigration]]] = {
    app[4:]: Loader[type[BaseMigration]](
        bases=config.iter_customized_bases(f"{app}.migrations"),
    )
    for app in INSTALLED_APPS
    if app.startswith("noc.") and _has_migrations(app[4:])
}
