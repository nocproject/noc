# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Custom python module importer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
import os
import imp


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
        return compile(source, self._get_filename(fullname),
                       "exec", dont_inherit=True)

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

        if fullname in sys.modules:
            mod = sys.modules[fullname]
        else:
            mod = sys.modules.setdefault(
                fullname,
                imp.new_module(fullname)
            )

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
        else:
            mod.__package__ = ".".join(fullname.split(".")[:-1])

        if self.is_package(fullname):
            # Set __path__ for packages
            # so we can find the sub-modules.
            mod.__path__ = [self.path_entry]

        if isinstance(source, unicode):
            # Convert to UTF-8 to prevent
            # SyntaxError: encoding declaration in Unicode string
            source = source.encode("utf-8")
        exec(source, mod.__dict__)
        return mod


class NOCPyruleLoader(NOCLoader):
    PREFIX = "noc.pyrules"
    COLLECTION_NAME = "pyrules"
    collection = None

    def _get_collection(self):
        if not self.collection:
            from noc.lib.nosql import get_db
            self.collection = get_db()[self.COLLECTION_NAME]
        return self.collection

    def get_source(self, fullname):
        key = fullname[len(self.PREFIX) + 1:]
        if not key:
            return self.INIT_SOURCE  # Importing noc.pyrules
        try:
            coll = self._get_collection()
            # Try to load module
            d = coll.find_one({"name": key}, {"_id": 0, "source": 1})
            if d:
                return d.get("source", "")  # Found
            # Not found, try to resolve as package name
            d = coll.find_one({
                "name": {
                    "$regex": r"^{}\.".format(key.replace(".", "\\."))
                }
            })
            if d:
                self.packages.add(fullname)
                return self.INIT_SOURCE
            # Invalid modules
            return None
        except Exception as e:
            raise ImportError(str(e))


# Install loader
sys.meta_path += [ImportRouter({
    NOCPyruleLoader.PREFIX: NOCPyruleLoader
})]
