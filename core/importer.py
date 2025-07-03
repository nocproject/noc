# ----------------------------------------------------------------------
# Custom python module importer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
import os
import importlib
from contextlib import contextmanager

# NOC modules
from noc.config import config


class ImportRouter(object):
    """
    Module importer that maps module prefixes to loader classes
    """

    def __init__(self, mappings):
        self.mappings = mappings

    def find_module(self, fullname, path=None):
        for prefix in self.mappings:
            if fullname.startswith(prefix):
                return self.mappings[prefix](path[0])
        return None


class NOCLoader(object):
    """
    Abstract class for prefixed loader
    """

    PREFIX = None
    INIT_SOURCE = ""
    packages = set()

    def __init__(self, path_entry):
        self.path_entry = path_entry
        self.packages.add(self.PREFIX)

    def get_source(self, fullname):
        raise NotImplementedError()

    def get_code(self, fullname):
        source = self.get_source(fullname)
        return compile(source, self._get_filename(fullname), "exec", dont_inherit=True)

    def get_data(self, path):
        raise NotImplementedError()

    def _get_filename(self, fullname):
        name = os.path.join(self.path_entry, fullname.replace(".", os.sep))
        if fullname in self.packages:
            return name + os.sep + "__init__.py"
        else:
            return name + ".py"

    def is_package(self, fullname):
        return fullname in self.packages

    def load_module(self, fullname):
        source = self.get_source(fullname)
        if source is None:
            return None

        mod = sys.modules.get(fullname)
        if mod is None:
            spec = importlib.util.spec_from_loader(fullname, loader=None)
            mod = sys.modules.setdefault(fullname, importlib.util.module_from_spec(spec))
        # Set a few properties required by PEP 302
        mod.__file__ = self._get_filename(fullname)
        mod.__name__ = fullname
        mod.__path__ = self.path_entry
        mod.__loader__ = self
        # PEP-366 specifies that package"s set __package__ to
        # their name, and modules have it set to their parent
        # package (if any).
        if self.is_package(fullname):
            mod.__package__ = fullname
            # Set __path__ for packages
            # so we can find the sub-modules.
            # Strip __init__.py
            mod.__path__ = [mod.__file__[:-12]]
        else:
            mod.__package__ = ".".join(fullname.split(".")[:-1])

        if isinstance(source, str):
            # Convert to UTF-8 to prevent
            # SyntaxError: encoding declaration in Unicode string
            source = source.encode()
        exec(source, mod.__dict__)
        return mod


class NOCPyruleLoader(NOCLoader):
    PREFIX = "noc.pyrules"
    COLLECTION_NAME = "pyrules"
    collection = None

    def _get_collection(self):
        if not self.collection:
            from noc.core.mongo.connection import get_db

            self.collection = get_db()[self.COLLECTION_NAME]
        return self.collection

    def get_source(self, fullname):
        key = fullname[len(self.PREFIX) + 1 :]
        if not key:
            return self.INIT_SOURCE  # Importing noc.pyrules
        try:
            coll = self._get_collection()
            # Try to load module
            d = coll.find_one({"name": key}, {"_id": 0, "source": 1})
            if d:
                return d.get("source", "")  # Found
            # Not found, try to resolve as package name
            d = coll.find_one({"name": {"$regex": r"^{}\.".format(key.replace(".", "\\."))}})
            if d:
                self.packages.add(fullname)
                return self.INIT_SOURCE
            # Invalid modules
            return None
        except Exception as e:
            raise ImportError(str(e))


class NOCCustomLoader(NOCLoader):
    PREFIX = "noc.custom"

    def get_source(self, fullname):
        key = fullname[len(self.PREFIX) + 1 :]
        if not key:
            return self.INIT_SOURCE  # Importing noc.custom
        path = os.path.join(config.path.custom_path, key.replace(".", os.sep))
        f_path = path + ".py"
        # File exists
        if os.path.exists(f_path):
            with open(f_path) as f:
                return f.read()
        # Not found, resolve as package name
        if os.path.exists(path):
            self.packages.add(fullname)
            return self.INIT_SOURCE
        raise ModuleNotFoundError(f"No module named '{fullname}'")


def _get_loader():
    # Pyrules
    loader_map = {NOCPyruleLoader.PREFIX: NOCPyruleLoader}
    # Custom
    if config.path.custom_path and os.path.exists(config.path.custom_path):
        loader_map[NOCCustomLoader.PREFIX] = NOCCustomLoader
    parts = __file__.split(os.sep)
    root = os.path.join(*parts[:-3])
    if not parts[0]:
        root = os.sep + root
    root = os.path.abspath(root)
    return ImportRouter(loader_map)


@contextmanager
def prefer_site_packages():
    """
    Temporary remove script directory from import path to avoid naming clashes.
    Usage

    ```
    with prefer_site_packages():
        import dns
    ```
    """
    prev = sys.path
    sys.path = [x for x in sys.path if x]
    yield
    sys.path = prev


# Install loader
sys.meta_path += [_get_loader()]
