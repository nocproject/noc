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
        "NOC.main.prefixtable.LookupField",
        "NOC.core.TagsField"
    ],
    model: "NOC.sa.activator.Model",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Active",
            dataIndex: "is_active",
            renderer: NOC.render.Bool
        },
        {
            text: "Shard",
            dataIndex: "shard",
            renderer: NOC.render.Lookup("shard")
        },
        {
            text: "Prefix",
            dataIndex: "prefix_table",
            renderer: NOC.render.Lookup("prefix_table")
        },
        {
            text: "Tags",
            dataIndex: "tags",
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
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: "Tags",
            allowBlank: true
        }
    ]
});
