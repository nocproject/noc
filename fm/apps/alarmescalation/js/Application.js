//---------------------------------------------------------------------
// fm.alarmescalation application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmescalation.Application");

Ext.define("NOC.fm.alarmescalation.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.alarmescalation.Model",
        "NOC.sa.administrativedomain.LookupField",
        "NOC.sa.managedobjectselector.LookupField",
        "NOC.fm.alarmclass.LookupField",
        "NOC.fm.ttsystem.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.notificationgroup.LookupField",
        "NOC.main.timepattern.LookupField",
    ],
    model: "NOC.fm.alarmescalation.Model",
    initComponent: function () {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: "Name",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: "Description",
                    allowBlank: true
                },
                {
                    name: "global_limit",
                    xtype: "numberfield",
                    fieldLabel: "Global limit",
                    allowBlank: true
                },
                {
                    name: "alarm_classes",
                    xtype: "gridfield",
                    fieldLabel: "Alarm Classes",
                    columns: [
                        {
                            text: "Alarm Class",
                            dataIndex: "alarm_class",
                            editor: "fm.alarmclass.LookupField",
                            renderer: NOC.render.Lookup("alarm_class"),
                            flex: 1
                        }
                    ]
                },
                {
                    name: "pre_reasons",
                    xtype: "gridfield",
                    fieldLabel: "Pre Reasons",
                    columns: [
                        {
                            text: "TT System",
                            dataIndex: "tt_system",
                            editor: "fm.ttsystem.LookupField",
                            renderer: NOC.render.Lookup("tt_system"),
                            width: 150
                        },
                        {
                            text: "Pre Reason",
                            dataIndex: "pre_reason",
                            editor: "textfield",
                            flex: 1
                        }
                    ]
                },
                {
                    name: "escalations",
                    xtype: "gridfield",
                    fieldLabel: "Escalations",
                    columns: [
                        {
                            text: "Delay",
                            dataIndex: "delay",
                            editor: "numberfield",
                            width: 75
                        },
                        {
                            text: "Adm. domain",
                            dataIndex: "administrative_domain",
                            editor: "sa.administrativedomain.LookupField",
                            width: 150,
                            renderer: NOC.render.Lookup("administrative_domain")
                        },
                        {
                            text: "Selector",
                            dataIndex: "selector",
                            editor: "sa.managedobjectselector.LookupField",
                            width: 150,
                            renderer: NOC.render.Lookup("selector")
                        },
                        {
                            text: "Time Pattern",
                            dataIndex: "time_pattern",
                            editor: "main.timepattern.LookupField",
                            renderer: NOC.render.Lookup("time_pattern")
                        },
                        {
                            text: "Notification Group",
                            dataIndex: "notification_group",
                            editor: "main.notificationgroup.LookupField",
                            width: 150,
                            renderer: NOC.render.Lookup("notification_group")
                        },
                        {
                            text: "Template",
                            dataIndex: "template",
                            editor: "main.template.LookupField",
                            flex: 1,
                            renderer: NOC.render.Lookup("template")
                        },
                        {
                            text: "TT",
                            dataIndex: "create_tt",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: "Wait TT",
                            dataIndex: "wait_tt",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        },
                        {
                            text: "Stop",
                            dataIndex: "stop_processing",
                            editor: "checkboxfield",
                            width: 50,
                            renderer: NOC.render.Bool
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
