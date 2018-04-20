//---------------------------------------------------------------------
// inv.networkchart application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networkchart.Application");

Ext.define("NOC.inv.networkchart.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.inv.networkchart.Model",
        "NOC.sa.managedobjectselector.LookupField"
    ],
    model: "NOC.inv.networkchart.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
        },
        {
            text: "Active",
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Selector",
            dataIndex: "selector",
            renderer: NOC.render.Lookup("selector"),
            width: 100
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
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Is Active",
            allowBlank: false
        },
        {
            name: "selector",
            xtype: "sa.managedobjectselector.LookupField",
            fieldLabel: "Selector",
            allowBlank: false
        }
    ]
});
