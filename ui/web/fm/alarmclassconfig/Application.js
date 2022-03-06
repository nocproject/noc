//---------------------------------------------------------------------
// fm.alarmclassconfig application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmclassconfig.Application");

Ext.define("NOC.fm.alarmclassconfig.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.alarmclassconfig.Model",
        "NOC.fm.alarmclass.LookupField",
        "NOC.pm.thresholdprofile.LookupField"
    ],
    model: "NOC.fm.alarmclassconfig.Model",
    columns: [

        {
            text: __("Alarm Class"),
            dataIndex: "alarm_class",
            renderer: NOC.render.Lookup("alarm_class"),
            width: 200
        },
        {
            text: __("Active"),
            dataIndex: "is_active",
            width: 100,
            renderer: NOC.render.Bool
        },
        {
            text: __("Enable Notification Delay"),
            dataIndex: "enable_notification_delay",
            width: 200,
            renderer: NOC.render.Bool
        },
        {
            text: __("Enable Control Time"),
            dataIndex: "enable_control_time",
            width: 150,
            renderer: NOC.render.Bool
        },
        {
            text: __("Enable Alarm Repeat"),
            dataIndex: "enable_alarm_repeat",
            width: 200,
            renderer: NOC.render.Bool
        },
        {
            text: __("Description"),
            dataIndex: "description",
            width: 300
        }
    ],
    fields: [
        {
            name: "alarm_class",
            xtype: "fm.alarmclass.LookupField",
            fieldLabel: __("Alarm Class"),
            allowBlank: false,
            uiStyle: "large"
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: __("Active"),
            allowBlank: true
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true,
            uiStyle: "large"
        },
        {
            xtype: "fieldset",
            title: __("Notification Delay"),
            layout: "vbox",
            defaults: {
                labelAlign: "top",
                padding: 4
            },
            items: [
                {
                    name: "enable_notification_delay",
                    xtype: "checkboxfield",
                    boxLabel: __("Notification Delay")
                },
                {
                    name: "notification_delay",
                    xtype: "numberfield",
                    fieldLabel: __("Notification Delay (s)"),
                    allowBlank: true,
                    minValue: 0,
                    uiStyle: "medium"
                }
            ]
        },
        {
            xtype: "fieldset",
            title: __("Control Time"),
            layout: "vbox",
            defaults: {
                labelAlign: "top",
                padding: 4
            },
            items: [
                {
                    name: "enable_control_time",
                    xtype: "checkboxfield",
                    boxLabel: __("Control Time")
                },
                {
                    name: "control_time0",
                    xtype: "numberfield",
                    fieldLabel: __("Control time (no reopens)"),
                    allowBlank: true,
                    minValue: 0,
                    uiStyle: "medium"
                },
                {
                    name: "control_time1",
                    xtype: "numberfield",
                    fieldLabel: __("Control time (1 reopen)"),
                    allowBlank: true,
                    minValue: 0,
                    uiStyle: "medium"
                },
                {
                    name: "control_timeN",
                    xtype: "numberfield",
                    fieldLabel: __("Control time (multiple reopens)"),
                    allowBlank: true,
                    minValue: 0,
                    uiStyle: "medium"
                }
            ]
        },
        {
            xtype: "fieldset",
            title: __("Alarm Repeat"),
            layout: "vbox",
            defaults: {
                labelAlign: "top",
                padding: 4
            },
            items: [
                {
                    name: "enable_alarm_repeat",
                    xtype: "checkboxfield",
                    boxLabel: __("Alarm Repeat")
                },
                {
                    name: "thresholdprofile",
                    xtype: "pm.thresholdprofile.LookupField",
                    fieldLabel: __("Threshold profile"),
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    name: "close_threshold_profile",
                    xtype: "checkboxfield",
                    boxLabel: __("Close Alarm Repeat by Threshold Profile")
                }
            ]
        }
    ]
});
