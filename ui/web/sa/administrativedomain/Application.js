//---------------------------------------------------------------------
// sa.administrativedomain application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.administrativedomain.Application");

Ext.define("NOC.sa.administrativedomain.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.administrativedomain.Model",
        "NOC.sa.administrativedomain.LookupField",
        "NOC.core.TreeField",
        "NOC.main.pool.LookupField"
    ],
    model: "NOC.sa.administrativedomain.Model",
    search: true,
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 150
        },
        {
            text: __("Parent"),
            dataIndex: "parent",
            renderer: NOC.render.Lookup("parent"),
            width: 150
        },
        {
            text: __("Pool"),
            dataIndex: "default_pool",
            renderer: NOC.render.Lookup("default_pool"),
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
            name: "parent",
            xtype: "nocTreeField",
            fieldLabel: __("Parent"),
            allowBlank: true,
            emptyText: __("Select parent..."),
            restUrl: '/sa/administrativedomain'
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: __("Description"),
            allowBlank: true
        },
        {
            name: "default_pool",
            xtype: "main.pool.LookupField",
            fieldLabel: __("Pool"),
            allowBlank: true
        }
    ]
});
