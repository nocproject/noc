//---------------------------------------------------------------------
// sa.mrtconfig application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.mrtconfig.Application");

Ext.define("NOC.sa.mrtconfig.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.mrtconfig.Model",
        "NOC.main.pyrule.LookupField",
        "NOC.sa.managedobjectselector.LookupField"
    ],
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
            renderer: NOC.render.Bool,
            width: 70
        },

        {
            text: "Permission",
            dataIndex: "permission_name",
            width: 70
        },

        {
            text: "Map Script",
            dataIndex: "map_script"
        },

        {
            text: "Reduce pyRule",
            dataIndex: "reduce_pyrule",
            width: 100,
            renderer: NOC.render.Lookup("reduce_pyrule")
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
            name: "selector",
            xtype: "sa.managedobjectselector.LookupField",
            fieldLabel: "Selector",
            allowBlank: false,
            query: {
                is_enabled: true
            }

        },
        {
            name: "reduce_pyrule",
            xtype: "main.pyrule.LookupField",
            fieldLabel: "Reduce pyRule",
            allowBlank: false,
            query: {
                interface: "IReduceTask"
            }
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
