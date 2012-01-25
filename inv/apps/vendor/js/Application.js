//---------------------------------------------------------------------
// inv.vendor application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.vendor.Application");

Ext.define("NOC.inv.vendor.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.inv.vendor.Model"],
    model: "NOC.inv.vendor.Model",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Builtin",
            dataIndex: "is_builtin"
        },
        {
            text: "Site",
            dataIndex: "site"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "name",
            allowBlank: false
        },
        {
            name: "is_builtin",
            xtype: "checkboxfield",
            boxLabel: "is_builtin"
        },
        {
            name: "site",
            xtype: "textfield",
            fieldLabel: "site",
            allowBlank: true
        }
    ]
});
