//---------------------------------------------------------------------
// sa.activator application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.activator.Application");

Ext.define("NOC.sa.activator.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.activator.Model",
        "NOC.main.shard.LookupField",
        "NOC.main.prefixtable.LookupField"
    ],
    model: "NOC.sa.activator.Model",
    columns: [
        {
            text: "Name",
            width: 100,
            dataIndex: "name"
        },
        {
            text: "Active",
            dataIndex: "is_active",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Shard",
            dataIndex: "shard",
            width: 100,
            renderer: NOC.render.Lookup("shard")
        },
        {
            text: "Min Members",
            dataIndex: "min_members",
            width: 70,
            align: "right"
        },
        {
            text: "Min Sessions",
            dataIndex: "min_sessions",
            width: 70,
            align: "right"
        },
        {
            text: "Current Members",
            dataIndex: "current_members",
            width: 70,
            align: "right",
            sortable: false
        },
        {
            text: "Current Sessions",
            dataIndex: "current_sessions",
            width: 70,
            align: "right",
            sortable: false
        },
        {
            text: "Prefix",
            dataIndex: "prefix_table",
            width: 150,
            renderer: NOC.render.Lookup("prefix_table")
        },
        {
            text: "Tags",
            dataIndex: "tags",
            flex: 1,
            renderer: NOC.render.Tags
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
            name: "shard",
            xtype: "main.shard.LookupField",
            fieldLabel: "Shard",
            allowBlank: false
        },
        {
            name: "prefix_table",
            xtype: "main.prefixtable.LookupField",
            fieldLabel: "Prefix Table",
            allowBlank: false
        },
        {
            name: "auth",
            xtype: "textfield",
            fieldLabel: "Auth String",
            allowBlank: false
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Is Active",
            allowBlank: false
        },
        {
            name: "min_members",
            xtype: "numberfield",
            fieldLabel: "Min. Members",
            minValue: 0
        },
        {
            name: "min_sessions",
            xtype: "numberfield",
            fieldLabel: "Min. Sessions",
            minValue: 0
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: "Tags",
            allowBlank: true
        }
    ]
});
