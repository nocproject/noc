//---------------------------------------------------------------------
// MongoDBCheckForm
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.check.mongodb.MongoDBCheckForm");

Ext.define("NOC.pm.check.mongodb.MongoDBCheckForm", {
    extend: "Ext.form.Panel",
    items: [
        {
            name: "host",
            fieldLabel: "Host",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "port",
            fieldLabel: "Port",
            xtype: "numberfield",
            allowBlank: false,
            defaultValue: 21017
        },
        {
            name: "db",
            fieldLabel: "Database",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "user",
            fieldLabel: "User",
            xtype: "textfield",
            allowBlank: true
        },
        {
            name: "password",
            fieldLabel: "Password",
            xtype: "textfield",
            allowBlank: true
        }
    ]
});
