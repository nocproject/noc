# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# BaseCollator class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six
from typing import Dict, Optional

# NOC modules
from noc.inv.models.interface import Interface


class BaseCollator(object):
    def __init__(self):
        pass

    def collate(self, physical_path, interfaces):
        # type: (six.string_types, Dict[six.string_types, Interface]) -> Optional[six.string_types]
        raise NotImplementedError
