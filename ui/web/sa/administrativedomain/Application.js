//---------------------------------------------------------------------
// sa.administrativedomain application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.administrativedomain.Application");

Ext.define("NOC.sa.administrativedomain.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.sa.administrativedomain.Model"],
    model: "NOC.sa.administrativedomain.Model",
    search: true,
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 150
        },
        {
            text: __("Objects"),
            dataIndex: "object_count",
            width: 50,
            align: "right",
            sortable: false
        },
        {
            text: __("Description"),
            dataIndex: "description",
            flex: true
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: __("Name"),
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: __("Description"),
            allowBlank: true
        }
    ]
});
