//---------------------------------------------------------------------
// pm.storage application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.storage.Application");

Ext.define("NOC.pm.storage.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.pm.pmstorage.Model",
        "NOC.pm.database.LookupField"
    ],
    model: "NOC.pm.storage.Model",
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
        },
        {
            text: "DB",
            dataIndex: "db",
            renderer: NOC.render.Lookup("db"),
            width: 150
        },
        {
            text: "Collection",
            dataIndex: "collection",
            width: 200
        },
        {
            text: "Raw Retention",
            dataIndex: "raw_retention",
            width: 100
        }
    ],
    fields: [
        {
            name: "name",
            fieldLabel: "Name",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "db",
            fieldLabel: "DB",
            xtype: "pm.database.LookupField",
            allowBlank: false
        },
        {
            name: "collection",
            fieldLabel: "Collection",
            xtype: "textfield",
            allowBlank: false
        },
        {
            name: "raw_retention",
            fieldLabel: "Raw Retention",
            xtype: "numberfield",
            allowBlank: false
        }
    ]
});
