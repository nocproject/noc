# ----------------------------------------------------------------------
# ReportInterfaceMetrics datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC Modules
from .base import CHTableReportDataSource, ReportField
from noc.config import config


class ReportInterfaceMetrics(CHTableReportDataSource):
    name = "reportinterfacemetrics"
    description = "Query Metrics from Interface table"
    object_field = "managed_object"
    CHUNK_SIZE = 1500

    TABLE_NAME = "noc.interface"
    FIELDS = [
        ReportField(
            name="managed_object",
            label="Managed Object BIID",
            description="",
            unit="INT",
            metric_name="managed_object",
            group=True,
        ),
        ReportField(
            name="iface_name",
            label="Interface Name",
            description="",
            unit="STRING",
            metric_name="interface",
            group=True,
        ),
        ReportField(
            name="interface_profile",
            label="Interface Profile Name",
            description="",
            unit="STRING",
            metric_name=f"dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes', 'profile', (managed_object, interface))",
            group=True,
        ),
        ReportField(
            name="iface_description",
            label="Interface Description",
            description="",
            unit="STRING",
            metric_name=f"dictGetString('{config.clickhouse.db_dictionaries}.interfaceattributes','description' , (managed_object, interface))",
            group=True,
        ),
        ReportField(
            name="iface_speed",
            label="Interface Speed",
            description="",
            unit="BIT/S",
            metric_name=f"if(max(speed) = 0, dictGetUInt64('{config.clickhouse.db_dictionaries}.interfaceattributes', 'in_speed', (managed_object, interface)), max(speed))",
        ),
        ReportField(
            name="load_in_perc",
            label="Load In (90% percentile)",
            description="",
            unit="BIT/S",
            metric_name="round(quantile(0.90)(load_in), 0)",
        ),
        ReportField(
            name="load_in_avg",
            label="Load In (Average)",
            description="",
            unit="BIT/S",
            metric_name="round(avg(load_in), 0)",
        ),
        ReportField(
            name="load_in_p",
            label="Load In (% Bandwith)",
            description="",
            unit="BIT/S",
            metric_name=f"replaceOne(toString(round(quantile(0.90)(load_in) / if(max(speed) = 0, dictGetUInt64('{config.clickhouse.db_dictionaries}.interfaceattributes', 'in_speed', (managed_object, interface)), max(speed)), 4) * 100), '.', ',')",
        ),
        ReportField(
            name="load_out_perc",
            label="Load Out (90% percentile)",
            description="",
            unit="BIT/S",
            metric_name="round(quantile(0.90)(load_out), 0)",
        ),
        ReportField(
            name="load_out_avg",
            label="Load Out (Average)",
            description="",
            unit="BIT/S",
            metric_name="round(avg(load_out), 0)",
        ),
        ReportField(
            name="load_out_p",
            label="Load Out (% Bandwith)",
            description="",
            unit="BYTE",
            metric_name=f"replaceOne(toString(round(quantile(0.90)(load_out) / if(max(speed) = 0, dictGetUInt64('{config.clickhouse.db_dictionaries}.interfaceattributes', 'in_speed', (managed_object, interface)), max(speed)), 4) * 100), '.', ',')",
        ),
        ReportField(
            name="octets_in_sum",
            label="Traffic In (Sum by period in MB)",
            description="",
            unit="MBYTE",
            metric_name="round((sum(load_in * time_delta) / 8) / 1048576)",
        ),
        ReportField(
            name="octets_out_sum",
            label="Traffic Out (Sum by period in MB)",
            description="",
            unit="MBYTE",
            metric_name="round((sum(load_out * time_delta) / 8) / 1048576)",
        ),
        ReportField(
            name="errors_in",
            label="Errors In (packets/s)",
            description="",
            unit="PKT/S",
            metric_name="quantile(0.90)(errors_in)",
        ),
        ReportField(
            name="errors_in_sum",
            label="Errors In (Summary)",
            description="",
            unit="PKT",
            metric_name="sum(errors_in_delta)",
        ),
        ReportField(
            name="errors_out",
            label="Errors Out (packets/s)",
            description="",
            unit="PKT/S",
            metric_name="quantile(0.90)(errors_out)",
        ),
        ReportField(
            name="errors_out_sum",
            label="Errors Out (Summary)",
            description="",
            unit="PKT",
            metric_name="sum(errors_out_delta)",
        ),
        ReportField(
            name="discards_in",
            label="Discards In (packets/s)",
            description="",
            unit="PKT/S",
            metric_name="quantile(0.90)(discards_in)",
        ),
        ReportField(
            name="discards_in_sum",
            label="Discards In (Summary)",
            description="",
            unit="PKT",
            metric_name="sum(discards_in_delta)",
        ),
        ReportField(
            name="discards_out",
            label="Discards Out (packets/s)",
            description="",
            unit="PKT/S",
            metric_name="quantile(0.90)(discards_out)",
        ),
        ReportField(
            name="discards_out_sum",
            label="Discards Out (Summary)",
            description="",
            unit="PKT",
            metric_name="sum(discards_out_delta)",
        ),
        ReportField(
            name="interface_flap",
            label="Interface Flap count",
            description="",
            unit="COUNT",
            metric_name="countEqual(arrayMap((a,p) -> a + p, arrayPushFront(groupArray(status_oper), groupArray(status_oper)[1]), arrayPushBack(groupArray(status_oper), groupArray(status_oper)[-1])), 1)",
        ),
        ReportField(
            name="status_oper_last",
            label="Operational status",
            description="",
            unit="ENUM",
            metric_name="anyLast(status_oper)",
        ),
        ReportField(
            name="lastchange",
            label="Interface Last Change (days)",
            description="",
            unit="DAY",
            metric_name="anyLast(lastchange)",
        ),
    ]
    TIMEBASED = True
