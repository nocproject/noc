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
        "NOC.fm.alarmclass.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.notificationgroup.LookupField",
        "NOC.fm.ttsystem.LookupField"
    ],
    model: "NOC.fm.alarmescalation.Model",
    initComponent: function() {
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
                    fieldLabel: "Name",
                    allowBlank: false
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
                            text: "Administrative Domain",
                            dataIndex: "administrative_domain",
                            editor: "sa.administrativedomain.LookupField"
                        },
                        {
                            text: "Delay",
                            dataIndex: "delay",
                            editor: "numberfield"
                        },
                        {
                            text: "Notification Group",
                            dataIndex: "notification_group",
                            editor: "main.notificationgroup.LookupField"
                        },
                        {
                            text: "TT System",
                            dataIndex: "tt_system",
                            editor: "fm.ttsystem.LookupField"
                        },
                        {
                            text: "TT Queue",
                            dataIndex: "tt_queue",
                            editor: "textfield"
                        },
                        {
                            text: "Template",
                            dataIndex: "template",
                            editor: "main.template.LookupField"
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
