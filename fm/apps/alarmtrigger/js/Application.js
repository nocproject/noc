//---------------------------------------------------------------------
// fm.alarmtrigger application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmtrigger.Application");

Ext.define("NOC.fm.alarmtrigger.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
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
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Enabled",
            dataIndex: "is_enabled",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Alarm Class RE",
            dataIndex: "alarm_class_re"
        },
        {
            text: "Condition",
            dataIndex: "condition"
        },
        {
            text: "Time Pattern",
            dataIndex: "time_pattern",
            renderer: NOC.render.Lookup("time_pattern")
        },
        {
            text: "Selector",
            dataIndex: "selector",
            renderer: NOC.render.Lookup("selector")
        },
        {
            text: "Notification Group",
            dataIndex: "notification_group",
            renderer: NOC.render.Lookup("notification_group")
        },
        {
            text: "Template",
            dataIndex: "template",
            renderer: NOC.render.Lookup("template")
        },
        {
            text: "PyRule",
            dataIndex: "pyrule",
            renderer: NOC.render.Lookup("pyrule")
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
            name: "is_enabled",
            xtype: "checkboxfield",
            boxLabel: "Is Enabled",
            allowBlank: false
        },
        {
            name: "alarm_class_re",
            xtype: "textfield",
            fieldLabel: "Alarm class RE",
            allowBlank: false
        },
        {
            name: "condition",
            xtype: "textfield",
            fieldLabel: "Condition",
            allowBlank: false
        },
        {
            name: "time_pattern",
            xtype: "main.timepattern.LookupField",
            fieldLabel: "Time Pattern",
            allowBlank: true
        },
        {
            name: "selector",
            xtype: "sa.managedobjectselector.LookupField",
            fieldLabel: "Managed Object Selector",
            allowBlank: true
        },
        {
            name: "notification_group",
            xtype: "main.notificationgroup.LookupField",
            fieldLabel: "Notification Group",
            allowBlank: true
        },
        {
            name: "template",
            xtype: "main.template.LookupField",
            fieldLabel: "Template",
            allowBlank: true
        },
        {
            name: "pyrule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: "pyRule",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By Enabled",
            name: "is_enabled",
            ftype: "boolean"
        }
    ]
});
