//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.Grid");

Ext.define("NOC.fm.alarm.view.grids.Grid", {
    extend: "Ext.grid.Panel",
    controller: "fm.alarm.GridController",
    requires: [
        "NOC.fm.alarm.view.grids.GridController",
        "NOC.fm.alarm.view.grids.GridViewTable"
    ],
    columns: [
        {
            text: __("ID"),
            dataIndex: "id",
            width: 150,
            hidden: true
        },
        {
            xtype: "glyphactioncolumn",
            width: 20 * 2,
            sortable: false,
            items: [
                {
                    glyph: NOC.glyph.globe,
                    tooltip: __("Show map"),
                    handler: "onShowMap"
                },
                {
                    glyph: NOC.glyph.eye,
                    tooltip: __("Show object"),
                    handler: "onShowObject"
                }
            ]
        },
        {
            text: __("Status"),
            dataIndex: "status",
            width: 60,
            renderer: function(v, _, record) {
                var STATUS_MAP = {
                        A: "Active",
                        C: "Archived"
                    },
                    value = NOC.render.Choices(STATUS_MAP)(v);
                if(record.get("isInMaintenance")) value = '<span title="' + __('Under maintaintance') + '">' +
                    '<i class="fa fa-wrench" aria-hidden="true"></i>&nbsp;' + value + '</span>';
                return value;
            },
            hidden: true
        },
        {
            text: __("Time/Duration"),
            dataIndex: "timestamp",
            width: 120,
            renderer: function(v, _, record) {
                return NOC.render.DateTime(record.get("timestamp")) +
                    "<br/>" +
                    NOC.render.Duration(record.get("duration"));
            }
        },
        {
            text: __("Start"),
            dataIndex: "timestamp",
            width: 120,
            hidden: true,
            renderer: NOC.render.DateTime
        },
        {
            text: __("Stop"),
            dataIndex: "clear_timestamp",
            width: 120,
            hidden: true,
            renderer: function(v) {
                if(v === null) {
                    return "-"
                } else {
                    return NOC.render.DateTime(v)
                }
            }
        },
        {
            text: __("Duration"),
            dataIndex: "duration",
            width: 120,
            hidden: true,
            renderer: NOC.render.Duration
        },
        {
            text: __("Object/Segment"),
            dataIndex: "managed_object",
            width: 250,
            renderer: function(v, _, record) {
                return record.get("managed_object__label") + "<br/>" + record.get("segment__label");
            }
        },
        {
            text: __("Location"),
            dataIndex: "location",
            width: 250,
            renderer: function(v, _, record) {
                return record.get("location_1") + "<br/>" + record.get("location_2");
            }
        },
        {
            text: __("Address/Platform"),
            dataIndex: "address",
            width: 120,
            renderer: function(v, _, record) {
                return record.get("address") +
                    "<br/>" +
                    (record.get("platform") || "");
            }
        },
        {
            text: __("Severity"),
            dataIndex: "severity",
            width: 70,
            renderer: function(v, _, record) {
                return record.get("severity__label") +
                    "<br/>" +
                    record.get("severity");
            }
        },
        {
            xtype: "actioncolumn",
            text: __("Ack"),
            width: 35,
            items: [{
                tooltip: __("Alarm Acknowledged"),
                handler: function(view, rowIndex, colIndex, item, e, record) {
                    var isAck = !!record.get("ack_user");
                    // ToDo double code #acknowledge
                    Ext.MessageBox.confirm(
                        __("Acknowledge"),
                        isAck ? __("Set alarm as unacknowledged") : __("Set alarm as acknowledged"),
                        function(btn) {
                            var msg = __("Failed to set acknowledgedun/acknowledged"),
                                url = "/fm/alarm/" + record.id + (isAck ? "/unacknowledge/" : "/acknowledge/");
                            if(btn === "yes") {
                                Ext.Ajax.request({
                                    url: url,
                                    method: "POST",
                                    scope: this,
                                    success: function(response) {
                                        var data = Ext.decode(response.responseText);
                                        if(!data.status) {
                                            Ext.MessageBox.show({
                                                title: "Error",
                                                message: data.hasOwnProperty("message") ? data.message : msg,
                                                buttons: Ext.Msg.OK,
                                                icon: Ext.Msg.ERROR
                                            });
                                        }
                                        view.up("[itemId=fm-alarm]").getController().reloadActiveGrid();
                                    },
                                    failure: function() {
                                        NOC.error(msg);
                                    }
                                })
                            }
                        },
                        this
                    );
                },
                getClass: function(v, _, record) {
                    return "x-fa fa-" + (record.get("ack_user") ? "toggle-on" : "toggle-off");
                },
                isDisabled: function(view, rowIndex, colIndex, item, record) {
                    var isActive = record.get("status") === "A" || false;
                    return !(view.up("[itemId=fm-alarm]").permissions["acknowledge"] && isActive);
                }
            }]
        },
        {
            text: __("Acknowledged"),
            dataIndex: "ack_user",
            renderer: function(v, _, record) {
                return record.get("ack_user")
                    ? record.get("ack_user")
                    + "<br/>"
                    + NOC.render.DateTime(record.get("ack_ts"))
                    : "-";
            }
        },
        {
            text: __("Subject/Class"),
            dataIndex: "subject",
            flex: 1,
            sortable: false,
            renderer: function(v, _, record) {
                return record.get("subject") +
                    "<br/>" +
                    record.get("alarm_class__label");
            }
        },
        {
            text: __("Summary/TT"),
            dataIndex: "summary",
            width: 150,
            sortable: false,
            renderer: function(v, _, record) {
                var r = [], summary = record.get("summary"),
                    tt = record.get("escalation_tt") || false,
                    ee = record.get("escalation_error") || false,
                    filter = this.getViewModel().get("displayFilter.hasProfiles");
                if(!Ext.Object.isEmpty(filter)
                    && filter.array && filter.array.length > 0
                    && (record.get("total_services") || record.get("total_subscribers"))) {
                    var data = Ext.Array.map(record.get("total_subscribers").concat(record.get("total_services")), function(item) {
                        return {
                            id: item.profile,
                            label: item.profile__label,
                            icon: item.glyph,
                            summary: item.summary,
                            display_order: item.display_order
                        }
                    });
                    summary = this.up("[reference=fm-alarm-list]").getController().generateSummaryHtml(data, filter);
                }
                r.push(summary);
                if(tt) {
                    r.push('<a href="/api/card/view/tt/' + tt + '/" target="_blank">' + tt + '</a>');
                } else {
                    if(ee) {
                        r.push('<i class="fa fa-exclamation-triangle"></i> Error')
                    }
                }
                return r.join("<br>");
            }
        },
        {
            text: __("Objects"),
            dataIndex: "total_objects",
            width: 30,
            align: "right",
            sortable: false
        },
        {
            text: __("Events"),
            dataIndex: "events",
            width: 30,
            align: "right",
            sortable: false
        }
    ],
    viewConfig: {
        xclass: "NOC.fm.alarm.view.grids.GridViewTable"
    }
});