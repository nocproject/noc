# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## GIS Overlay Plugins
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.interfaces import *


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
