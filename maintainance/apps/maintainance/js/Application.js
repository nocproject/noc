//---------------------------------------------------------------------
// maintainance.maintainance application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintainance.maintainance.Application");

Ext.define("NOC.maintainance.maintainance.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.maintainance.maintainance.Model",
        "NOC.maintainance.maintainancetype.LookupField",
        "NOC.sa.managedobject.LookupField"
    ],
    model: "NOC.maintainance.maintainance.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Type",
                    dataIndex: "type",
                    width: 150,
                    renderer: NOC.render.Lookup("type")
                },
                {
                    text: "Start",
                    dataIndex: "start",
                    width: 120
                },
                {
                    text: "Stop",
                    dataIndex: "stop",
                    width: 120
                },
                {
                    text: "Completed",
                    dataIndex: "is_completed",
                    width: 25,
                    renderer: NOC.render.Bool
                },
                {
                    text: "Subject",
                    dataIndex: "subject",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "subject",
                    xtype: "textfield",
                    fieldLabel: "Subject",
                    allowBlank: false
                },
                {
                    name: "type",
                    xtype: "maintainance.maintainancetype.LookupField",
                    fieldLabel: "Type",
                    allowBlank: false
                },
                {
                    xtype: "container",
                    layout: "hbox",
                    items: [
                        {
                            name: "start_date",
                            xtype: "datefield",
                            fieldLabel: "Start",
                            allowBlank: false,
                            uiStyle: "small",
                            width: 200,
                            format: "d.m.Y"
                        },
                        {
                            name: "start_time",
                            xtype: "timefield",
                            allowBlank: false,
                            labelWidth: 0,
                            uiStyle: "small",
                            width: 80,
                            format: "H:i"
                        }
                    ]
                },
                {
                    xtype: "container",
                    layout: "hbox",
                    items: [
                        {
                            name: "stop_date",
                            xtype: "datefield",
                            fieldLabel: "Stop",
                            allowBlank: false,
                            uiStyle: "small",
                            width: 200,
                            format: "d.m.Y"
                        },
                        {
                            name: "stop_time",
                            xtype: "timefield",
                            allowBlank: false,
                            labelWidth: 0,
                            uiStyle: "small",
                            width: 80,
                            format: "H:i"
                        }
                    ]
                },
                {
                    name: "is_completed",
                    xtype: "checkbox",
                    boxLabel: "Completed"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "contacts",
                    xtype: "textarea",
                    fieldLabel: "Contacts",
                    allowBlank: false
                },
                {
                    name: "suppress_alarms",
                    xtype: "checkbox",
                    boxLabel: "Suppress alarms"
                },
                {
                    name: "direct_objects",
                    xtype: "gridfield",
                    fieldLabel: "Objects",
                    columns: [
                        {
                            text: "Object",
                            dataIndex: "object",
                            editor: "sa.managedobject.LookupField",
                            flex: 1,
                            renderer: NOC.render.Lookup("object")
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },

    editRecord: function(record) {
        var me = this,
            start = Ext.Date.parse(record.get("start"), "Y-m-d H:i:s"),
            stop = Ext.Date.parse(record.get("stop"), "Y-m-d H:i:s");
        record.set("start_date", start);
        record.set("start_time", start);
        record.set("stop_date", stop);
        record.set("stop_time", stop);
        me.callParent([record]);
    },

    cleanData: function(v) {
        var me = this;
        me.callParent([v]);
        v.start = me.mergeDate(v.start_date, v.start_time);
        delete v.start_date;
        delete v.start_time;
        v.stop = me.mergeDate(v.stop_date, v.stop_time);
        delete v.stop_date;
        delete v.stop_time;
    },

    mergeDate: function(d, t) {
        var year = d.getFullYear(),
            month = d.getMonth(),
            day = d.getDate(),
            hour = t.getHours(),
            min = t.getMinutes(),
            sec = t.getSeconds(),
            q = function(v) {
                if(v < 10) {
                    return "0" + v;
                } else {
                    return "" + v;
                }
            };
        return "" + year + "-" + q(month + 1) + "-" + q(day) + "T" +
                q(hour) + ":" + q(min) + ":" + q(sec);
    }
});
