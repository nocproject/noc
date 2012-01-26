//---------------------------------------------------------------------
// sa.mrtconfig application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.mrtconfig.Application");

Ext.define("NOC.sa.mrtconfig.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.sa.mrtconfig.Model"],
    model: "NOC.sa.mrtconfig.Model",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },

        {
            text: "Active",
            dataIndex: "is_active"
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
            name: "description",
            xtype: "textfield",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Is Active"
        },
        {
            name: "permission_name",
            xtype: "textfield",
            fieldLabel: "Permission",
            allowBlank: false
        },
        {
            name: "timeout",
            xtype: "numberfield",
            fieldLabel: "Timeout",
            allowBlank: true
        },
        {
            name: "map_script",
            xtype: "textfield",
            fieldLabel: "Map Script",
            allowBlank: false
        }
    ]
});
