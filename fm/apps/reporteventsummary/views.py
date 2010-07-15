# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event Summary Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,TableColumn
from django import forms
##
##
##
report_types=[
            ("class","By Event Class"),
            ("priority","By Event Priority"),
            ("object","By Managed Object"),
            ("profile","By Profile"),
            ]
class ReportForm(forms.Form):
    report_type=forms.ChoiceField(choices=report_types)
##
##
##
class EventSummaryReport(SimpleReport):
    title="Event Summary"
    form=ReportForm
    def get_data(self,report_type,**kwargs):
        # By Profile
        if report_type=="class":
            columns=["Event Class"]
            query="""SELECT ec.name,COUNT(*)
                    FROM fm_eventclass ec JOIN fm_event e ON (ec.id=e.event_class_id)
                    GROUP BY 1
                    ORDER BY 2 DESC"""
        elif report_type=="priority":
            columns=["Priority"]
            query="""SELECT ep.name,COUNT(*)
                    FROM fm_eventpriority ep JOIN fm_event e ON (ep.id=e.event_priority_id)
                    GROUP BY 1
                    ORDER BY 2 DESC"""
        elif report_type=="object":
            columns=["Managed Object"]
            query="""SELECT mo.name,COUNT(*)
                    FROM fm_event e JOIN sa_managedobject mo ON (e.managed_object_id=mo.id)
                    GROUP BY 1
                    ORDER BY 2 DESC"""
        elif report_type=="profile":
            columns=["Profile"]
            query="""SELECT mo.profile_name,COUNT(*)
                    FROM fm_event e JOIN sa_managedobject mo ON (e.managed_object_id=mo.id)
                    GROUP BY 1
                    ORDER BY 2 DESC"""
        else:
            raise Exception("Invalid report type: %s"%report_type)
        for r,t in report_types:
            if r==report_type:
                title=self.title+": "+t
                break
        columns+=[TableColumn("Quantity",align="right",total="sum",format="integer")]
        return self.from_query(title=title,columns=columns,query=query,enumerate=True)
