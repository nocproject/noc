//---------------------------------------------------------------------
// sa.mrtconfig application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.mrtconfig.Application");

Ext.define("NOC.sa.mrtconfig.Application", {
    extend: "NOC.core.ModelApplication",
    requires: ["NOC.sa.mrtconfig.Model", "NOC.main.pyrule.LookupField"],
    model: "NOC.sa.mrtconfig.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },

        {
            text: "Active",
            dataIndex: "is_active",
            renderer: noc_renderBool,
            width: 70
        },

        {
            text: "Map Script",
            dataIndex: "map_script"
        },

        {
            text: "Description",
            dataIndex: "description",
            flex: true
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
            allowBlank: false,
            regex: /^[a-zA-Z0-9_]+$/
        },
        {
            name: "reduce_pyrule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: "Reduce pyRule",
            allow_blank: false
        },
        {
            name: "map_script",
            xtype: "textfield",
            fieldLabel: "Map Script",
            allowBlank: false
        },
        {
            name: "timeout",
            xtype: "numberfield",
            fieldLabel: "Timeout",
            allowBlank: true
        }
    ]
});
