//---------------------------------------------------------------------
// maintenance.maintenance application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenance.Application");

Ext.define("NOC.maintenance.maintenance.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.maintenance.maintenance.Model",
        "NOC.maintenance.maintenancetype.LookupField",
        "NOC.sa.managedobject.LookupField",
        "NOC.inv.networksegment.LookupField",
        "NOC.main.timepattern.LookupField"
    ],
    model: "NOC.maintenance.maintenance.Model",
    initComponent: function() {
        var me = this;

        me.ITEM_OBJECTS = me.registerItem(
            "NOC.maintenance.maintenance.ObjectsPanel"
        );

        me.cardButton = Ext.create("Ext.button.Button", {
            text: __("Card"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onCard
        });

        me.affectedButton = Ext.create("Ext.button.Button", {
            text: __("Affected Objects"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onObjects
        });

        Ext.apply(me, {
            columns: [
                {
                    text: __("Type"),
                    dataIndex: "type",
                    width: 150,
                    renderer: NOC.render.Lookup("type")
                },
                {
                    text: __("Start"),
                    dataIndex: "start",
                    width: 120
                },
                {
                    text: __("Stop"),
                    dataIndex: "stop",
                    width: 120
                },
                {
                    text: __("Completed"),
                    dataIndex: "is_completed",
                    width: 25,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Time Pattern"),
                    dataIndex: "time_pattern",
                    width: 150,
                    renderer: NOC.render.Lookup("time_pattern")
                },
                {
                    text: __("Subject"),
                    dataIndex: "subject",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "subject",
                    xtype: "textfield",
                    fieldLabel: __("Subject"),
                    allowBlank: false
                },
                {
                    name: "type",
                    xtype: "maintenance.maintenancetype.LookupField",
                    fieldLabel: __("Type"),
                    allowBlank: false
                },
                {
                    xtype: "container",
                    layout: "hbox",
                    items: [
                        {
                            name: "start_date",
                            xtype: "datefield",
                            // startDay: 1,
                            fieldLabel: __("Start"),
                            allowBlank: false,
                            format: "d.m.Y"
                        },
                        {
                            name: "start_time",
                            xtype: "timefield",
                            allowBlank: false,
                            labelWidth: 0,
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
                            // startDay: 1,
                            fieldLabel: __("Stop"),
                            allowBlank: false,
                            format: "d.m.Y"
                        },
                        {
                            name: "stop_time",
                            xtype: "timefield",
                            allowBlank: false,
                            labelWidth: 0,
                            width: 80,
                            format: "H:i"
                        }
                    ]
                },
                {
                    name: "is_completed",
                    xtype: "checkbox",
                    boxLabel: __("Completed")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "contacts",
                    xtype: "textarea",
                    fieldLabel: __("Contacts"),
                    allowBlank: false
                },
                {
                    name: "time_pattern",
                    xtype: "main.timepattern.LookupField",
                    fieldLabel: __("Time Pattern"),
                    allowBlank: true
                },
                {
                    name: "suppress_alarms",
                    xtype: "checkbox",
                    boxLabel: __("Suppress alarms")
                },
                {
                    name: "escalate_managed_object",
                    xtype: "sa.managedobject.LookupField",
                    fieldLabel: __("Escalate to"),
                    allowBlank: true
                },
                {
                    name: "direct_objects",
                    xtype: "gridfield",
                    fieldLabel: __("Objects"),
                    columns: [
                        {
                            text: __("Object"),
                            dataIndex: "object",
                            editor: "sa.managedobject.LookupField",
                            flex: 1,
                            renderer: NOC.render.Lookup("object")
                        }
                    ]
                },
                {
                    name: "direct_segments",
                    xtype: "gridfield",
                    fieldLabel: __("Segments"),
                    columns: [
                        {
                            text: __("Segment"),
                            dataIndex: "segment",
                            editor: "inv.networksegment.LookupField",
                            flex: 1,
                            renderer: NOC.render.Lookup("segment")
                        }
                    ]
                }
            ],
            formToolbar: [
                me.cardButton,
                me.affectedButton
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
    },

    onCard: function() {
        var me = this;
        if(me.currentRecord) {
            window.open(
                "/api/card/view/maintenance/" + me.currentRecord.get("id") + "/"
            );
        }
    },

    onObjects: function() {
        var me = this;
        me.previewItem(me.ITEM_OBJECTS, me.currentRecord);
    }
});
