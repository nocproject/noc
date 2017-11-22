//---------------------------------------------------------------------
// fm.alarmtrigger application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmtrigger.Application");

Ext.define("NOC.fm.alarmtrigger.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.alarmtrigger.Model",
        "NOC.main.timepattern.LookupField",
        "NOC.sa.managedobjectselector.LookupField",
        "NOC.main.notificationgroup.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.pyrule.LookupField"
    ],
    model: "NOC.fm.alarmtrigger.Model",
    columns: [
        {
            text: __("Name"),
            dataIndex: "name"
        },
        {
            text: __("Enabled"),
            dataIndex: "is_enabled",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: __("Alarm Class RE"),
            dataIndex: "alarm_class_re"
        },
        {
            text: __("Condition"),
            dataIndex: "condition"
        },
        {
            text: __("Time Pattern"),
            dataIndex: "time_pattern",
            renderer: NOC.render.Lookup("time_pattern")
        },
        {
            text: __("Selector"),
            dataIndex: "selector",
            renderer: NOC.render.Lookup("selector")
        },
        {
            text: __("Notification Group"),
            dataIndex: "notification_group",
            renderer: NOC.render.Lookup("notification_group")
        },
        {
            text: __("Template"),
            dataIndex: "template",
            renderer: NOC.render.Lookup("template")
        },
        {
            text: __("PyRule"),
            dataIndex: "pyrule",
            renderer: NOC.render.Lookup("pyrule")
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("Name"),
            allowBlank: false
        },
        {
            name: "is_enabled",
            xtype: "checkboxfield",
            boxLabel: __("Is Enabled"),
            allowBlank: false
        },
        {
            name: "alarm_class_re",
            xtype: "textfield",
            fieldLabel: __("Alarm class RE"),
            allowBlank: false
        },
        {
            name: "condition",
            xtype: "textfield",
            fieldLabel: __("Condition"),
            allowBlank: false
        },
        {
            name: "time_pattern",
            xtype: "main.timepattern.LookupField",
            fieldLabel: __("Time Pattern"),
            allowBlank: true
        },
        {
            name: "selector",
            xtype: "sa.managedobjectselector.LookupField",
            fieldLabel: __("Managed Object Selector"),
            allowBlank: true
        },
        {
            name: "notification_group",
            xtype: "main.notificationgroup.LookupField",
            fieldLabel: __("Notification Group"),
            allowBlank: true
        },
        {
            name: "template",
            xtype: "main.template.LookupField",
            fieldLabel: __("Template"),
            allowBlank: true
        },
        {
            name: "pyrule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: __("pyRule"),
            allowBlank: true
        }
    ],
    filters: [
        {
            title: __("By Enabled"),
            name: "is_enabled",
            ftype: "boolean"
        }
    ]
});
