# ----------------------------------------------------------------------
# BaseMarshaller
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from gufo.loader import Loader

# NOC modules
from noc.config import config


class BaseMarshaller:
    name = None

    @classmethod
    def marshall(cls, node):
        """Serialize Node

        Args:
            node: Node instance

        Returns:
            Raw data
        """
        raise NotImplementedError()

    @classmethod
    def unmarshall(cls, data):
        """Deserialize raw data to Node

        Args:
            data: Raw data

        Returns:
            Node
        """
        raise NotImplementedError()


marshaller_loader = Loader[type[BaseMarshaller]](
    bases=config.iter_customized_bases("noc.core.confdb.db.marshall"),
    exclude=("base",),
)
