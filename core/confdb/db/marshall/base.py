# ----------------------------------------------------------------------
# BaseMarshaller
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class BaseMarshaller(object):
    name = None

    @classmethod
    def marshall(cls, node):
        """
        Serialize Node
        :param node: Node instance
        :return: Raw data
        """
        raise NotImplementedError()

    @classmethod
    def unmarshall(cls, data):
        """
        Deserialize raw data to Node
        :param data: Raw data
        :return: Node
        """
        raise NotImplementedError()
