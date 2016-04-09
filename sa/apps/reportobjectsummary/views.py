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
            ("tag","By Tags"),
            ("platform", "By Platform"),
            ("version", "By Version"),
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
            query = """
              SELECT t.tag, COUNT(*)
              FROM (
                SELECT unnest(tags) AS tag
                FROM sa_managedobject
                WHERE
                  tags IS NOT NULL
                  AND array_length(tags, 1) > 0
                ) t
              GROUP BY 1
              ORDER BY 2 DESC;
            """
        elif report_type=="platform":
            columns = ["Platform", "Profile"]
            query="""select sam.profile_name, sama.value,count(value)
                    from sa_managedobject sam join  sa_managedobjectattribute sama on (sam.id=sama.managed_object_id)
                    where sama.key='platform' group by 1,2 order by count(value) desc;"""

        elif report_type == "version":
            columns = ["Platform", "version"]
            query = """select sam.profile_name, sama.value,count(value)
                      from sa_managedobject sam join  sa_managedobjectattribute sama on (sam.id=sama.managed_object_id)
                    where sama.key='version' group by 1,2 order by count(value) desc;"""

        else:
            raise Exception("Invalid report type: %s"%report_type)
        for r,t in report_types:
            if r==report_type:
                title=self.title+": "+t
                break
        columns+=[TableColumn("Quantity",align="right",total="sum",format="integer")]
        return self.from_query(title=title,columns=columns,query=query,enumerate=True)
