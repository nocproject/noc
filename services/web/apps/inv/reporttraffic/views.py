# -*- coding: utf-8 -*-
"""
##----------------------------------------------------------------------
## fm.reporttraffic
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""

## Python modules
import datetime
from collections import defaultdict, Counter
## Django modules
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
## NOC modules
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile
from noc.core.influxdb.client import InfluxDBClient
from noc.lib.nosql import get_db
from noc.sa.models.useraccess import UserAccess
from noc.lib.app.simplereport import SimpleReport, TableColumn, PredefinedReport, SectionRow
from noc.lib.dateutils import total_seconds
from noc.lib.nosql import Q
from pymongo import ReadPreference
from noc.core.translation import ugettext as _


class ReportForm(forms.Form):
    from_date = forms.CharField(
        widget=AdminDateWidget,
        label=_("From Date"),
        required=True
    )
    to_date = forms.CharField(
        widget=AdminDateWidget,
        label=_("To Date"),
        required=True
    )
    # skip_avail = forms.BooleanField(
    #     label=_("Skip full available"),
    #     required=False
    # )

    #managed_object = forms.ModelChoiceField(
    #    label=_("Managed Object"),
    #    required=False,
    #    queryset=ManagedObject.objects.filter()
    #)
    object_profile = forms.ModelChoiceField(
        label=_("Object Profile"),
        required=False,
        queryset=ManagedObjectProfile.objects.filter()
    )   
    interface_profile = forms.ModelChoiceField(
        label=_("Interface Profile"),
        required=False,
        queryset=InterfaceProfile.objects.filter()
    )      

class ReportTraffic(SimpleReport):
    title = _("Load Interfaces")
    form = ReportForm
    predefined_reports = {
        "1d": PredefinedReport(
            _("Traffic (1 day)"), {
                "duration": 86400
            }
        ),
        "7d": PredefinedReport(
            _("Traffic (7 days)"), {
                "duration": 7 * 86400
            }
        ),
        "30d": PredefinedReport(
            _("Traffic (30 day)"), {
                "duration": 30 * 86400
            }
        )
    }
    
    def get_data(self, request, from_date=None, to_date=None, object_profile=None, interface_profile=None, managed_object=None, **kwargs):
        now = datetime.datetime.now()
        b = datetime.datetime.strptime(from_date, "%d.%m.%Y")
        td = b.strftime("%Y-%m-%d")
        if to_date:
            t1 = datetime.datetime.strptime(to_date, "%d.%m.%Y")
        else:
            t1 = now
        fd = t1.strftime("%Y-%m-%d")
        # Interval days
        a = td.split('-')
        b = fd.split('-')
        aa = datetime.date(int(a[0]),int(a[1]),int(a[2]))
        bb = datetime.date(int(b[0]),int(b[1]),int(b[2]))
        cc = bb-aa
        dd = str(cc)
        interval = (dd.split()[0])       
        # Load managed objects
        f = []
        r1 = []
        r2 = []
        r11 = []
        r12 = []
        if object_profile:
            mos = ManagedObject.objects.filter(object_profile=object_profile)
        if managed_object:
            mos = ManagedObject.objects.filter(id=managed_object.id) 
        for o in mos:
            ifaces = Interface.objects.filter(managed_object=o, type="physical")
            if interface_profile:
                ifaces = Interface.objects.filter(managed_object=o, type="physical", profile=interface_profile)
            for j in ifaces:    
                # print m.name, "," , m.platform  , ",", m.address, ",", j.name, ",",j.description
                client = InfluxDBClient()
                query1 = ["SELECT percentile(\"value\", 98) FROM \"Interface | Load | In\" WHERE \"object\" = '%s' AND \"interface\" = '%s' AND time >= '%s' AND time <= '%s';" % (
                    o.name, j.name, td , fd)]
                result1 = client.query(query1)
                r = list(result1)
                if len(r)>0:
                    r = r[0]
                    r1 = r["percentile"]
                else:
                    r1 = 0      
                query2 = ["SELECT percentile(\"value\", 98) FROM \"Interface | Load | Out\" WHERE \"object\" = '%s' AND \"interface\" = '%s' AND time >= '%s' AND time <= '%s';" % (
                    o.name, j.name, td , fd)]
                result2 = client.query(query2)
                r = list(result2)
                if len(r)>0:
                    r = r[0]
                    r2 = r["percentile"]
                else:
                    r2 = 0                          
                query11 = ["SELECT median(\"value\") FROM \"Interface | Load | In\" WHERE \"object\" = '%s' AND \"interface\" = '%s' AND time >= '%s' AND time <= '%s';" % (
                    o.name, j.name, td , fd)]
                result3 = client.query(query11)
                r = list(result3)
                if len(r)>0:
                    r = r[0]
                    r11 = r["median"]
                else:
                    r11 = 0                            
                query12 = ["SELECT median(\"value\") FROM \"Interface | Load | Out\" WHERE \"object\" = '%s' AND \"interface\" = '%s' AND time >= '%s' AND time <= '%s';" % (
                    o.name, j.name, td , fd)]
                result4 = client.query(query12)
                r = list(result4)
                if len(r)>0:
                    r = r[0]
                    r12 = r["median"]
                else:
                    r12 = 0                         
                f += [(
                    o.name,
                    o.description,
                    o.address,
                    j.name,
                    j.description,
                    int(r1),
                    int(r2),
                    int(r11),
                    int(r12),
                    interval  
                )]
        return self.from_dataset(
            title=self.title,
            columns=[
                _("Managed Object"), _("Street"), _("Address"), _("Int Name"), _("Int Descr"),
                TableColumn(_("IN bps"), align="right"),
                TableColumn(_("OUT bps"), align="right"),
                TableColumn(_("Median IN bps"), align="right"),
                TableColumn(_("Median OUT bps"), align="right"),
                TableColumn(_("Interval days"), align="right")
            ],
            data=f,
            enumerate=True
        )

