//---------------------------------------------------------------------
// gis.srs application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.srs.Application");

Ext.define("NOC.gis.srs.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.gis.srs.Model"],
    model: "NOC.gis.srs.Model",
    search: true,
    columns: [
        {
            text: "Auth.",
            dataIndex: "auth_name"
        },
        {
            text: "SRID",
            dataIndex: "auth_srid"
        },
        {
            text: "Description",
            dataIndex: "proj4text",
            flex: true
        }
    ],
    fields: [
        {
            name: "srid",
            xtype: "numberfield",
            fieldLabel: "srid",
            allowBlank: false
        },
        {
            name: "auth_name",
            xtype: "textfield",
            fieldLabel: "auth name",
            allowBlank: true
        },
        {
            name: "auth_srid",
            xtype: "numberfield",
            fieldLabel: "auth srid",
            allowBlank: true
        },
        {
            name: "proj4text",
            xtype: "textfield",
            fieldLabel: "proj4text",
            allowBlank: true
        }
    ]
});
