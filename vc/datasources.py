# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VC module datasources
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.datasource import DataSource
from noc.vc.models import VCDomain, VC


class VCDS(DataSource):
    _name = "vc.VCDS"

    def __init__(self, managed_object, l1, l2=0):
        self._vc = None
        self._vc_domain = self.find_vc_domain(managed_object)
        if self._vc_domain:
            r = list(VC.objects.filter(
                vc_domain=self._vc_domain, l1=l1, l2=l2))
            if r:
                self._vc = r[0]

    def find_vc_domain(self, managed_object):
        """
        Find VCDomain belonging to managed objects
        @todo: Speed optimization
        :param managed_object:
        :return:
        """
        return managed_object.vc_domain

    @property
    def vc_domain(self):
        if self._vc_domain:
            return self._vc_domain.name
        else:
            return None

    @property
    def name(self):
        if self._vc:
            return self._vc.name
        else:
            return None

    @property
    def description(self):
        if self._vc:
            return self._vc.description
        else:
            return None
