//---------------------------------------------------------------------
// sa.collector application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.collector.Application");

Ext.define("NOC.sa.collector.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.collector.Model"
    ],
    model: "NOC.sa.collector.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 100
        },
        {
            text: "Active",
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
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
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Is Active",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        }
    ]
});
