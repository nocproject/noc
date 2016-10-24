# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dashboard storage
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, DateTimeField, ListField,
                                ReferenceField, EmbeddedDocumentField)
## NOC modules
from dashboardlayout import DashboardLayout


class Dimension(EmbeddedDocument):
    """
    Dimensions are dynamic filters on loaded data
    """
    # Field name
    field = StringField()
    # Dimension function
    type = StringField(
        choices=[
            # Field value
            ("value", "value"),
            #
            ("count", "count"),
            # Date dimensions
            # By year
            ("year", "year"),
            # By quarter
            ("quarter", "quarter"),
            # By number of month
            ("month", "month"),
            # By number of day
            ("day", "day"),
            # By number of hour
            ("hour", "hour"),
            # By year and month
            ("year_month", "year_month"),
            # By year, month and day
            ("year_month_day", "year_month_day")
        ]
    )


class Filter(EmbeddedDocument):
    """
    Filters are external SQL conditions executed on server-side
    """
    # Field name
    field = StringField()
    # Filter condition
    condition = StringField(choices=[
        ("=", "="),
        ("<", "<"),
        ("<=", "<="),
        (">", ">"),
        (">=", ">=")
    ])
    # Filter value
    # Dashboard filter can be referenced as $$<name>
    value = StringField()


class Datasource(EmbeddedDocument):
    # Alias
    name = StringField()
    # Datasource name
    datasource = StringField()
    #
    filters = ListField(EmbeddedDocumentField(Filter))
    dimensions = ListField(EmbeddedDocumentField(Dimension))
    # @todo: aggregates
    # @todo: Having

    def get_query(self):
        r = {
            "datasource": self.datasource
        }
        return r


class Widget(EmbeddedDocument):
    # Cell name, taken from layout
    cell = StringField()
    # Widget type
    type = StringField(
        choices=[
            ("pieChart", "pieChart"),
            ("barChart", "barChart"),
            ("lineChart", "lineChart")
        ]
    )
    # @todo: Settings


class Dashboard(Document):
    meta = {
        "collection": "noc.dashboards",
        "allow_inheritance": False,
        "indexes": [
            "owner", "tags"
        ]
    }

    title = StringField()
    # Username
    owner = StringField()
    #
    description = StringField()
    #
    tags = ListField(StringField())
    # Config
    layout = ReferenceField(DashboardLayout)
    datasources = ListField(EmbeddedDocumentField(Datasource))
    #
    created = DateTimeField(default=datetime.datetime.now)
    changed = DateTimeField(default=datetime.datetime.now)

    def __unicode__(self):
        return self.title

