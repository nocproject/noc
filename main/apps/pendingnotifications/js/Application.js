//---------------------------------------------------------------------
// main.pendingnotifications application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pendingnotifications.Application");

Ext.define("NOC.main.pendingnotifications.Application", {
    extend: "NOC.core.ModelApplication",
    model: "NOC.main.pendingnotifications.Model",
    columns: [
        {
            text: "Timestamp",
            dataIndex: "timestamp",
            width: 130,
            renderer: NOC.render.DateTime
        },
        {
            text: "Method",
            dataIndex: "notification_method",
            width: 50
        },
        {
            text: "Params",
            dataIndex: "notification_params",
            width: 150
        },
        {
            text: "Subject",
            dataIndex: "subject",
            flex: 1
        },
        {
            text: "Tag",
            dataIndex: "tag",
            width: 150
        }
    ],
    fields: [
        {
            name: "timestamp",
            xtype: "datefield",
            fieldLabel: "Timestamp",
            allowBlank: false
        },
        {
            name: "notification_method",
            xtype: "textfield",
            fieldLabel: "Method",
            allowBlank: false
        },
        {
            name: "notification_params",
            xtype: "textfield",
            fieldLabel: "Params",
            allowBlank: false
        },
        {
            name: "subject",
            xtype: "textfield",
            fieldLabel: "Subject",
            allowBlank: false
        },
        {
            name: "body",
            xtype: "textarea",
            fieldLabel: "Body",
            allowBlank: false
        },
        {
            name: "link",
            xtype: "textfield",
            fieldLabel: "Link",
            allowBlank: true
        },
        {
            name: "next_try",
            xtype: "datefield",
            fieldLabel: "Next Try",
            allowBlank: true
        },
        {
            name: "actual_till",
            xtype: "datefield",
            fieldLabel: "Actual Till",
            allowBlank: true
        },
        {
            name: "tag",
            xtype: "textfield",
            fieldLabel: "Tag",
            allowBlank: true
        }
    ]
});
