//---------------------------------------------------------------------
// main.systemnotification application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.systemnotification.Application");

Ext.define("NOC.main.systemnotification.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.systemnotification.Model",
        "NOC.main.notificationgroup.LookupField"
    ],
    model: "NOC.main.systemnotification.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            flex: 1
        },
        {
            text: "Notification Group",
            dataIndex: "notification_group__label",
            flex: 1
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "Name",
            width: 400,
            allowBlank: false
        },
        {
            name: "notification_group",
            xtype: "main.notificationgroup.LookupField",
            fieldLabel: "Notification Group",
            width: 400,
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By Notify Group",
            name: "notification_group",
            ftype: "lookup",
            lookup: "main.notificationgroup"
        }
    ]
});
