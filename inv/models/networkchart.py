# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NetworkChart
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from noc.sa.models.managedobjectselector import ManagedObjectSelector
from networkchartstate import NetworkChartState


class NetworkChart(models.Model):
    class Meta:
        verbose_name = _("Network Chart")
        verbose_name_plural = _("Network Charts")
        db_table = "inv_networkchart"
        app_label = "inv"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=64, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    selector = models.ForeignKey(ManagedObjectSelector,
        verbose_name=_("Selector"))

    def __unicode__(self):
        return self.name

    def get_state(self, type, object):
        """
        Get current object state
        :param type:
        :param object:
        :return:
        """
        print "GET", type, object
        s = NetworkChartState.objects.filter(
            chart=self.id, type=type, object=str(object)).first()
        if s:
            return s.state
        else:
            return {}

    def update_state(self, type, object, state):
        """
        Update current object state
        :param type:
        :param object:
        :param state:
        :return:
        """
        object = str(object)
        s = NetworkChartState.objects.filter(
            chart=self.id, type=type, object=object).first()
        if s:
            cs = s.state.copy()
            cs.update(state)
            s.state = cs
            s.save()
        else:
            # Create state
            NetworkChartState(
                chart=self.id, type=type, object=object, state=state
            ).save()
