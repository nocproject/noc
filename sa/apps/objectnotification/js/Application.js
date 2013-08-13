//---------------------------------------------------------------------
// sa.objectnotification application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.objectnotification.Application");

Ext.define("NOC.sa.objectnotification.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.sa.objectnotification.Model",
        "NOC.sa.managedobjectselector.LookupField",
        "NOC.main.notificationgroup.LookupField"
    ],
    model: "NOC.sa.objectnotification.Model",
    columns: [
        {
            text: "Selector",
            dataIndex: "selector",
            renderer: NOC.render.Lookup("selector"),
            width: 200
        },
        {
            text: "Notification",
            dataIndex: "notification_group",
            renderer: NOC.render.Lookup("notification_group"),
            width: 200
        },
        {
            text: "Config Changed",
            dataIndex: "config_changed",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Alarm Risen",
            dataIndex: "alarm_risen",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Alarm Cleared",
            dataIndex: "alarm_cleared",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Alarm Commented",
            dataIndex: "alarm_commented",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "New",
            dataIndex: "new",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Deleted",
            dataIndex: "deleted",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Version Changed",
            dataIndex: "version_changed",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Script Failed",
            dataIndex: "script_failed",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Config Policy Violation",
            dataIndex: "config_policy_violation",
            width: 50,
            renderer: NOC.render.Bool
        }
    ],
    fields: [
        {
            name: "selector",
            xtype: "sa.managedobjectselector.LookupField",
            fieldLabel: "Selector",
            allowBlank: false
        },
        {
            name: "notification_group",
            xtype: "main.notificationgroup.LookupField",
            fieldLabel: "Notification Group",
            allowBlank: false
        },
        {
            name: "config_changed",
            xtype: "checkboxfield",
            boxLabel: "Config changed"
        },
        {
            name: "alarm_risen",
            xtype: "checkboxfield",
            boxLabel: "Alarm risen"
        },
        {
            name: "alarm_cleared",
            xtype: "checkboxfield",
            boxLabel: "Alarm cleared"
        },
        {
            name: "alarm_commented",
            xtype: "checkboxfield",
            boxLabel: "Alarm commented"
        },
        {
            name: "new",
            xtype: "checkboxfield",
            boxLabel: "New"
        },
        {
            name: "deleted",
            xtype: "checkboxfield",
            boxLabel: "Deleted"
        },
        {
            name: "version_changed",
            xtype: "checkboxfield",
            boxLabel: "Version changed"
        },
        {
            name: "interface_changed",
            xtype: "checkboxfield",
            boxLabel: "Interface changed"
        },
        {
            name: "script_failed",
            xtype: "checkboxfield",
            boxLabel: "Script failed"
        },
        {
            name: "config_policy_violation",
            xtype: "checkboxfield",
            boxLabel: "Config policy violation"
        }
    ]
});
