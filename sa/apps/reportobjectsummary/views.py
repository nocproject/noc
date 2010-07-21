# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Objects Summary Report
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
            ("profile","By Profile"),
            ("domain","By Administrative Domain"),
            ("domain-profile","By Administrative Domain and Profile"),
            ("tag","By Tags")
            ]
class ReportForm(forms.Form):
    report_type=forms.ChoiceField(choices=report_types)
##
##
##
class ReportObjectsSummary(SimpleReport):
    title="Managed Objects Summary"
    form=ReportForm
    def get_data(self,report_type,**kwargs):
        # By Profile
        if report_type=="profile":
            columns=["Profile"]
            query="SELECT profile_name,COUNT(*) FROM sa_managedobject GROUP BY 1 ORDER BY 2 DESC"
        # By Administrative Domain
        elif report_type=="domain":
            columns=["Administrative Domain"]
            query="""SELECT a.name,COUNT(*)
                FROM sa_managedobject o JOIN sa_administrativedomain a ON (o.administrative_domain_id=a.id)
                GROUP BY 1
                ORDER BY 2 DESC"""
        # By Profile and Administrative Domains
        elif report_type=="domain-profile":
            columns=["Administrative Domain","Profile"]
            query="""SELECT d.name,profile_name,COUNT(*)
                    FROM sa_managedobject o JOIN sa_administrativedomain d ON (o.administrative_domain_id=d.id)
                    GROUP BY 1,2
                    """
        # By tags
        elif report_type=="tag":
            columns=["Tag"]
            query="""SELECT t.name,COUNT(*)
                FROM tagging_tag t JOIN tagging_taggeditem ti ON (t.id=ti.tag_id)
                    JOIN django_content_type c ON (ti.content_type_id=c.id)
                WHERE c.app_label='sa'
                    AND c.model='managedobject'
                GROUP BY 1
                ORDER BY 1 DESC
            """
        else:
            raise Exception("Invalid report type: %s"%report_type)
        for r,t in report_types:
            if r==report_type:
                title=self.title+": "+t
                break
        columns+=[TableColumn("Quantity",align="right",total="sum",format="integer")]
        return self.from_query(title=title,columns=columns,query=query,enumerate=True)
