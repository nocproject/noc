# ----------------------------------------------------------------------
# Custom python module importer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

"""
Custom module importer for NOC dynamic modules.

The importer provides support for:
- noc.custom.* modules loaded from filesystem
- noc.pyrules.* modules loaded from MongoDB

The implementation uses PEP 451 import protocol and requires Python 3.11+.
"""

# Python modules
import importlib
import importlib.abc
import importlib.util
import os
import sys
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Any
from collections.abc import Sequence

# NOC modules
from noc.config import config


class NOCLoader(importlib.abc.Loader):
    """
    Base loader for NOC-specific module namespaces.

    Subclasses must implement :meth:`get_source`.

    The loader follows PEP 451 import protocol and uses ``exec_module()``
    for module initialization.
    """

    PREFIX: str
    INIT_SOURCE = ""

    def __init__(self, path_entry: str | None = None) -> None:
        """
        Initialize loader.

        Args:
            path_entry: Import search path entry.
        """
        self.base_path = Path(path_entry or "")
        self.packages: set[str] = {self.PREFIX}

    def get_source(self, fullname: str) -> str | None:
        """
        Return source code for module.

        Args:
            fullname: Full module name.

        Returns:
            Module source code.

        Raises:
            ModuleNotFoundError: If module does not exist.
        """
        raise NotImplementedError()

    def is_package(self, fullname: str) -> bool:
        """
        Check if module is a package.

        Args:
            fullname: Full module name.

        Returns:
            True if module is a package.
        """
        return fullname in self.packages

    def get_filename(self, fullname: str) -> str:
        """
        Get synthetic filename for module.

        Args:
            fullname: Full module name.

        Returns:
            Module filename.
        """
        base = self.base_path / Path(*fullname.split("."))

        if self.is_package(fullname):
            return str(base / "__init__.py")

        return str(base.with_suffix(".py"))

    def create_module(self, spec: ModuleSpec) -> ModuleType | None:
        """
        Create module instance.

        Returning None delegates creation to Python import machinery.

        Args:
            spec: Module specification.

        Returns:
            Custom module instance or None.
        """
        return None

    def exec_module(self, module: ModuleType) -> None:
        """
        Execute module code.

        Args:
            module: Module object to initialize.

        Raises:
            ModuleNotFoundError: If module source is unavailable.
        """
        fullname = module.__name__

        source = self.get_source(fullname)
        if source is None:
            raise ModuleNotFoundError(
                f"No module named '{fullname}'",
                name=fullname,
            )

        filename = self.get_filename(fullname)

        code = compile(
            source,
            filename,
            "exec",
            dont_inherit=True,
        )

        exec(code, module.__dict__)

    @classmethod
    def is_match(cls, fullname: str) -> bool:
        """
        Check whether loader handles module name.

        Args:
            fullname: Full module name.

        Returns:
            True if module belongs to loader namespace.
        """
        return fullname == cls.PREFIX or fullname.startswith(f"{cls.PREFIX}.")


class NOCPyruleLoader(NOCLoader):
    """
    Loader for dynamic Python rules stored in MongoDB.
    """

    PREFIX = "noc.pyrules"
    COLLECTION_NAME = "pyrules"

    def __init__(self, path_entry: str | None = None) -> None:
        """
        Initialize pyrule loader.

        Args:
            path_entry: Import search path entry.
        """
        super().__init__(path_entry)
        self._collection: Any | None = None

    def _get_collection(self) -> Any:
        """
        Get MongoDB collection.

        Returns:
            MongoDB collection instance.
        """
        if self._collection is None:
            from noc.core.mongo.connection import get_db

            self._collection = get_db()[self.COLLECTION_NAME]

        return self._collection

    def get_source(self, fullname: str) -> str:
        """
        Load module source from MongoDB.

        Args:
            fullname: Full module name.

        Returns:
            Python source code.

        Raises:
            ModuleNotFoundError: If module is absent.
        """
        key = fullname[len(self.PREFIX) + 1 :]

        if not key:
            return self.INIT_SOURCE

        collection = self._get_collection()

        document = collection.find_one(
            {"name": key},
            {"_id": 0, "source": 1},
        )

        if document:
            source = document.get("source")
            if source is not None:
                return source

        escaped = key.replace(".", r"\.")

        package = collection.find_one(
            {"name": {"$regex": rf"^{escaped}\."}},
        )

        if package:
            self.packages.add(fullname)
            return self.INIT_SOURCE

        raise ModuleNotFoundError(
            f"No module named '{fullname}'",
            name=fullname,
        )


class NOCCustomLoader(NOCLoader):
    """
    Loader for custom filesystem modules.
    """

    PREFIX = "noc.custom"

    def get_source(self, fullname: str) -> str:
        """
        Load module source from custom directory.

        Args:
            fullname: Full module name.

        Returns:
            Python source code.

        Raises:
            ModuleNotFoundError: If module is absent.
        """
        key = fullname[len(self.PREFIX) + 1 :].split(".")

        path = Path(config.path.custom_path) / Path(*key)

        if self.is_package(fullname):
            path /= "__init__.py"
        else:
            path = path.with_suffix(".py")

        if path.exists():
            return path.read_text(encoding="utf-8")

        raise ModuleNotFoundError(
            f"No module named '{fullname}'",
            name=fullname,
        )

    def is_package(self, fullname: str) -> bool:
        """
        Check whether filesystem object is a package.

        Args:
            fullname: Full module name.

        Returns:
            True if module is a package.
        """
        if super().is_package(fullname):
            return True

        key = fullname[len(self.PREFIX) + 1 :].split(".")

        path = Path(config.path.custom_path) / Path(*key)

        if path.is_dir() and (path / "__init__.py").exists():
            self.packages.add(fullname)
            return True

        return False


class NOCImportRouter(importlib.abc.MetaPathFinder):
    """
    Meta path finder routing NOC module namespaces to custom loaders.
    """

    def __init__(self) -> None:
        """
        Initialize importer router.
        """
        custom_path = config.path.custom_path

        self._check_custom = bool(custom_path and os.path.exists(custom_path))

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: Any | None = None,
    ) -> ModuleSpec | None:
        """
        Find module specification.

        Args:
            fullname: Requested module name.
            path: Parent package search path.
            target: Import target.

        Returns:
            Module specification or None.
        """

        def get_spec(loader_cls: type[NOCLoader]) -> ModuleSpec:
            loader = loader_cls(
                path_entry=path[0] if path else None,
            )

            return importlib.util.spec_from_loader(
                fullname,
                loader,
                is_package=loader.is_package(fullname),
            )

        if self._check_custom and NOCCustomLoader.is_match(fullname):
            return get_spec(NOCCustomLoader)

        if NOCPyruleLoader.is_match(fullname):
            return get_spec(NOCPyruleLoader)

        return None


# Install importer
sys.meta_path.append(NOCImportRouter())
