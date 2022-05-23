# ----------------------------------------------------------------------
# BaseLoader class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import inspect
import threading
import os
from typing import Iterator, Set, Generic, Tuple

# NOC modules
from noc.config import config
from noc.core.log import PrefixLoggerAdapter

logger = logging.getLogger(__name__)


class BaseLoader(object):
    name: str = None
    base_cls: "Generic" = None  # Base class to be loaded
    base_path: Tuple[str] = None  # Tuple of path components
    ignored_names: Set[str] = set()

    def __init__(self):
        self.logger = PrefixLoggerAdapter(logger, self.name)
        self.classes = {}
        self.lock = threading.Lock()
        self.all_classes: Set[str] = set()

    def find_class(self, module_name, base_cls, name):
        """
        Load subclass of *base_cls* from module

        :param module_name: String containing module name
        :param base_cls: Base class
        :param name: object name
        :return: class reference or None
        """
        try:
            sm = __import__(module_name, {}, {}, "*")
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

    def is_valid_class(self, kls: "Generic", name) -> bool:
        """
        Check `find_class` found valid class
        :param kls: Class
        :param name: Class' name
        :return: True if class is valid and should be returned
        """
        return True

    def is_valid_name(self, name: str) -> bool:
        return ".." not in name

    def get_path(self, base: str, name: str) -> str:
        """
        Get file path
        :param base: "" or custom prefix
        :param name: class name
        :return:
        """
        p = (base,) + self.base_path + ("%s.py" % name,)
        return os.path.join(*p)

    def get_module_name(self, base: str, name: str) -> str:
        """
        Get module name
        :param base: `noc` or custom prefix
        :param name: module name
        :return:
        """
        return "%s.%s.%s" % (base, ".".join(self.base_path), name)

    def get_class(self, name: str):
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
                    kls = self.find_class(module_name, self.base_cls, name)
                    if kls:
                        break
                if not kls:
                    logger.error("%s not found: %s", self.name, name)
                self.classes[name] = kls
            return kls

    def __getitem__(self, item):
        return self.get_class(item)

    def __iter__(self):
        return self.iter_classes()

    def iter_classes(self) -> Iterator[str]:
        with self.lock:
            if not self.all_classes:
                self.all_classes = self.find_classes()
        yield from sorted(self.all_classes)

    def find_classes(self) -> Set[str]:
        names = set()
        for dn in config.get_customized_paths(os.path.join(*self.base_path)):
            for fn in os.listdir(dn):
                if fn.startswith("_") or not fn.endswith(".py"):
                    continue
                name = fn[:-3]
                if name not in self.ignored_names:
                    names.add(name)
        return names
