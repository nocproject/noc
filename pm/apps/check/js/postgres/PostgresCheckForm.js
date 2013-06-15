//---------------------------------------------------------------------
// PostgresCheckForm
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.check.postgres.PostgresCheckForm");

Ext.define("NOC.pm.check.postgres.PostgresCheckForm", {
    extend: "Ext.form.Panel",
    items: [
        {
            name: "db",
            fieldLabel: "Database",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "host",
            fieldLabel: "Host",
            xtype: "textfield",
            allowBlank: true
        },
        {
            name: "port",
            fieldLabel: "Port",
            xtype: "numberfield",
            allowBlank: true,
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
