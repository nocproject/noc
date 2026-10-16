# ----------------------------------------------------------------------
# BaseLoader class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import importlib
import logging
import inspect
import threading
import os
from collections.abc import Iterator
from typing import cast

# NOC modules
from noc.config import config
from noc.core.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class BaseLoader:
    name: str | None = None
    base_cls: type | None = None  # Base class to be loaded
    base_path: tuple[str, ...] | None = None  # Tuple of path components
    ignored_names: set[str] = set()

    def __init__(self) -> None:
        """Initialize the loader's logger, cache, and lock.

        Returns:
            This method initializes the instance in place.
        """
        self.logger = PrefixLoggerAdapter(logger, self.name)
        self.classes: dict[str, type | None] = {}
        self.lock = threading.Lock()
        self.all_classes: set[str] = set()

    def find_class(self, module_name: str, base_cls: type, name: str) -> type | None:
        """Load a subclass of ``base_cls`` from a module.

        Args:
            module_name: Fully qualified name of the module to inspect.
            base_cls: Base class that the candidate must inherit from.
            name: Object name passed to :meth:`is_valid_class`.

        Returns:
            The first valid class found, or ``None`` if loading fails or the
            module contains no matching class.
        """
        try:
            sm = importlib.import_module(module_name)
            for n in dir(sm):
                o = getattr(sm, n)
                if (
                    inspect.isclass(o)
                    and issubclass(o, base_cls)
                    and o.__module__ == sm.__name__
                    and self.is_valid_class(o, name)
                ):
                    return o
        except ImportError as e:
            self.logger.error("Failed to load %s %s: %s", self.name, name, e)
        return None

    def is_valid_class(self, kls: type, name: str) -> bool:
        """Check whether a discovered class should be returned.

        Args:
            kls: Candidate class discovered by :meth:`find_class`.
            name: Object name requested by the caller.

        Returns:
            ``True`` if the candidate is valid.
        """
        return True

    def is_valid_name(self, name: str) -> bool:
        """Check whether an object name is safe to use in a module path.

        Args:
            name: Object name to validate.

        Returns:
            ``True`` if the name does not contain a parent path segment.
        """
        return ".." not in name

    def get_path(self, base: str, name: str) -> str:
        """Build the source file path for an object.

        Args:
            base: Empty string for the repository root, or the configured
                custom path.
            name: Class name whose source file is requested.

        Returns:
            Path to the object's Python source file.
        """
        p = (base or "src/noc", *cast(tuple[str, ...], self.base_path), f"{name}.py")
        return os.path.join(*p)

    def get_module_name(self, base: str, name: str) -> str:
        """Build the fully qualified module name for an object.

        Args:
            base: ``noc`` or a custom package name.
            name: Module name of the object.

        Returns:
            Fully qualified module name.
        """
        return f"{base}.{'.'.join(cast(tuple[str, ...], self.base_path))}.{name}"

    def get_class(self, name: str) -> type | None:
        """Load and cache the class identified by ``name``.

        Args:
            name: Object name to load.

        Returns:
            Loaded class, or ``None`` if the name is invalid or no matching
            class can be loaded.
        """
        with self.lock:
            kls = self.classes.get(name)
            if not kls:
                self.logger.info("Loading %s", name)
                if not self.is_valid_name(name):
                    self.logger.error("Invalid name: %s", name)
                    return None
                for p in config.get_customized_paths("", prefer_custom=True):
                    path = self.get_path(p, name)
                    if not os.path.exists(path):
                        continue
                    base_name = os.path.basename(os.path.dirname(p)) if p else "noc"
                    module_name = self.get_module_name(base_name, name)
                    kls = self.find_class(module_name, cast(type, self.base_cls), name)
                    if kls:
                        break
                if not kls:
                    logger.error("%s not found: %s", self.name, name)
                self.classes[name] = kls
            return kls

    def __getitem__(self, item: str) -> type | None:
        """Return the class associated with a key.

        Args:
            item: Object name to load.

        Returns:
            Loaded class, or ``None`` if no matching class exists.
        """
        return self.get_class(item)

    def __iter__(self) -> Iterator[str]:
        """Iterate over the names of available classes.

        Returns:
            Iterator yielding available class names.
        """
        return self.iter_classes()

    def iter_classes(self) -> Iterator[str]:
        """Iterate over cached or discovered class names.

        Returns:
            Iterator yielding available class names in order.
        """
        with self.lock:
            if not self.all_classes:
                self.all_classes = self.find_classes()
        yield from sorted(self.all_classes)

    def find_classes(self) -> set[str]:
        """Discover class names in the configured loader paths.

        Returns:
            Names of Python modules not listed in ``ignored_names``.
        """
        names = set()
        base_path = cast(tuple[str, ...], self.base_path)
        for dn in config.get_customized_paths(os.path.join(*base_path)):
            for fn in os.listdir(dn):
                if fn.startswith("_") or not fn.endswith(".py"):
                    continue
                name = fn[:-3]
                if name not in self.ignored_names:
                    names.add(name)
        return names
