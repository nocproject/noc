//---------------------------------------------------------------------
// MongoDB Probe Config
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.metricconfig.pm.probes.db.mongodb.MongoDBConfig");

Ext.define("NOC.metricconfig.pm.probes.db.mongodb.MongoDBConfig", {
    extend: "NOC.core.ProbeConfig",
    form: [
        {
            name: "host",
            xtype: "textfield",
            fieldLabel: "Database Host",
            allowBlank: false,
            value: "127.0.0.1"
        },
        {
            name: "port",
            xtype: "numberfield",
            fieldLabel: "Port",
            minValue: 1,
            maxValue: 65535,
            value: 27017
        },
        {
            name: "database",
            xtype: "textfield",
            fieldLabel: "DB",
            allowBlank: false,
            value: "noc"
        }
    ]
});
