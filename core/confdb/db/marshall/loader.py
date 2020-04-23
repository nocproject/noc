# ----------------------------------------------------------------------
# Marshaller Loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseMarshaller


class MarshallerLoader(BaseLoader):
    name = "tokenizer"
    base_cls = BaseMarshaller
    base_path = ("core", "confdb", "db", "marshall")


# Create singleton object
loader = MarshallerLoader()
