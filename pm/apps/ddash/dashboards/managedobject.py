# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObject's dynamic dashboard
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.models.managedobject import ManagedObject
from base import BaseDashboard
from noc.inv.models.interface import Interface
from noc.lib.text import split_alnum


class ManagedObjectDashboard(BaseDashboard):
    name = "managedobject"

    def resolve_object(self, object):
        try:
            return ManagedObject.objects.get(id=object)
        except ManagedObject.DoesNotExist:
            raise self.NotFound()

    def render(self):
        def profile_has_metrics(profile):
            """
            Check interface profile has metrics
            """
            for m in profile.metrics:
                if m.is_active and m.metric_type.name in (
                        "Interface | Load | In",
                        "Interface | Load | Out"
                ):
                    return True
            return False

        # Basic setup
        r = {
            "title": str(self.object.name),
            "style": "dark",
            "timezone": "browser",
            "editable": False,
            "time": {
                "from": "now-6h",
                "to": "now"
            },
            "refresh": "1m",
            "rows": []
        }
        # Add object name and description
        title = [self.object.name, "(%s)" % self.object.address]
        if self.object.platform:
            title += [self.object.platform]
        title = " ".join(title)
        r["rows"] += [{
            "title": title,
            "showTitle": True,
            "collapse": True,
            "editable": False,
            "panels": []
        }]
        if self.object.description:
            r["rows"][-1]["panels"] += [{
                "editable": False,
                "mode": "markdown",
                "content": self.object.description,
                "height": "24px",
                "span": 12,
            }]
        # Get all interface profiles with configurable metrics
        all_ifaces = list(Interface.objects.filter(
            managed_object=self.object.id
        ))
        iprof = set(i.profile for i in all_ifaces)
        # @todo: Order by priority
        profiles = [p for p in iprof if profile_has_metrics(p)]
        # Create charts for configured metrics
        for profile in profiles:
            ifaces = [i for i in all_ifaces if i.profile == profile]
            r["rows"] += [{
                "title": profile.name,
                "showTitle": True,
                "collapse": False,
                "editable": False,
                "height": "250px",
                "panels": []
            }]
            for iface in sorted(ifaces, key=split_alnum):
                i_title = [iface.name]
                if i.description:
                    i_title += ["(%s)" % i.description]
                i_title = " ".join(i_title)
                r["rows"][-1]["panels"] += [{
                    "span": 6,  # 2-column
                    "lines": True,
                    "linewidth": 2,
                    "links": [],
                    "nullPointMode": "connected",
                    "percentage": False,
                    "pointradius": 5,
                    "points": False,
                    "renderer": "flot",
                    "legend": {
                        "alignAsTable": True,
                        "avg": True,
                        "current": True,
                        "max": True,
                        "min": True,
                        "show": True,
                        "total": True,
                        "values": True,
                        "sortDesc": True
                    },
                    "seriesOverrides": [
                        {
                            "alias": "Input",
                            "transform": "negative-Y"
                        }
                    ],
                    "targets": [
                        {
                            "dsType": "influxdb",
                            "alias": "Input",
                            "groupBy": [
                                {
                                    "params": ["$interval"],
                                    "type": "time"
                                },
                                {
                                    "params": ["null"],
                                    "type": "fill"
                                }
                            ],
                            "measurement": "Interface | Load | In",
                            "query": "SELECT mean(\"value\") "
                                     "FROM \"Interface | Load | In\" "
                                     "WHERE "
                                     "  \"object\" = '%s' "
                                     "  AND \"interface\" = '%s' "
                                     "  AND $timeFilter "
                                     "GROUP BY time($interval) "
                                     "fill(null)" % (
                                         self.object.name,
                                         iface.name),
                            "refId": "A",
                            "resultFormat": "time_series",
                            "select": [
                                [
                                    {
                                        "params": ["value"],
                                        "type": "field"
                                    },
                                    {
                                        "params": [],
                                        "type": "mean"
                                    }
                                ]
                            ],
                            "tags": [
                                {
                                    "key": "object",
                                    "operator": "=",
                                    "value": self.object.name
                                },
                                {
                                    "condition": "AND",
                                    "key": "interface",
                                    "operator": "=",
                                    "value": iface.name
                                }
                            ]
                        },
                        {
                            "dsType": "influxdb",
                            "alias": "Output",
                            "groupBy": [
                                {
                                    "params": ["$interval"],
                                    "type": "time"
                                },
                                {
                                    "params": ["null"],
                                    "type": "fill"
                                }
                            ],
                            "measurement": "Interface | Load | Out",
                            "query": "SELECT mean(\"value\") "
                                     "FROM \"Interface | Load | Out\" "
                                     "WHERE "
                                     "  \"object\" = '%s' "
                                     "  AND \"interface\" = '%s' "
                                     "  AND $timeFilter "
                                     "GROUP BY time($interval) "
                                     "fill(null)" % (
                                         self.object.name,
                                         iface.name),
                            "refId": "B",
                            "resultFormat": "time_series",
                            "select": [
                                [
                                    {
                                        "params": ["value"],
                                        "type": "field"
                                    },
                                    {
                                        "params": [],
                                        "type": "mean"
                                    }
                                ]
                            ],
                            "tags": [
                                {
                                    "key": "object",
                                    "operator": "=",
                                    "value": self.object.name
                                },
                                {
                                    "condition": "AND",
                                    "key": "interface",
                                    "operator": "=",
                                    "value": iface.name
                                }
                            ]
                        }
                    ],
                    "timeFrom": None,
                    "timeShift": None,
                    "title": i_title,
                    "tooltip": {
                        "shared": True,
                        "value_type": "cumulative"
                    },
                    "type": "graph",
                    "x-axis": True,
                    "y-axis": True,
                    "y_formats": [
                        "bps",
                        "short"
                    ]
                }]
        return r
