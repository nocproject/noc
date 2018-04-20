# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# GIS Overlay Plugins
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## GIS Overlay Plugins
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.interfaces import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class OverlayHandler(object):
    def __init__(self, **config):
        """
        Overlay configuration will be passed
        :param config:
        :return:
        """

    def handle(self, bbox=None, **kwargs):
        """
        Re
        :param kwargs:
        :return: GeoJSON data
        """
        return []
