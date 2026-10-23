# ----------------------------------------------------------------------
# BI Dictionary loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from noc.core.clickhouse.model import DictionaryModel


class BIDictionaryLoader(BaseLoader):
    name = "bi_dictionary"
    base_cls = DictionaryModel
    base_path = ("core", "bi", "dictionaries")
    ignored_names = {"loader"}

    def is_valid_class(self, kls, name):
        return hasattr(kls, "_meta")


# Create singleton object
loader = BIDictionaryLoader()
