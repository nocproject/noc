//---------------------------------------------------------------------
// pm.database application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.database.Application");

Ext.define("NOC.pm.database.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.database.Model"
    ],
    model: "NOC.pm.database.Model",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Database",
            dataIndex: "database"
        },
        {
            text: "Host",
            dataIndex: "host"
        },
        {
            text: "Port",
            dataIndex: "port"
        },
        {
            text: "User",
            dataIndex: "user"
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
            name: "database",
            xtype: "textfield",
            fieldLabel: "Database",
            allowBlank: false
        },
        {
            name: "host",
            xtype: "textfield",
            fieldLabel: "Host",
            allowBlank: false,
            defaultValue: "127.0.0.1"
        },
        {
            name: "port",
            xtype: "numberfield",
            fieldLabel: "Port",
            allowBlank: false,
            defaultValue: 27017
        },
        {
            name: "user",
            xtype: "textfield",
            fieldLabel: "User",
            allowBlank: true
        },
        {
            name: "password",
            xtype: "textfield",
            fieldLabel: "Password",
            allowBlank: true
        }
    ]
});
