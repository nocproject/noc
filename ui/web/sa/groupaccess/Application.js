//---------------------------------------------------------------------
// sa.groupaccess application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.groupaccess.Application");

Ext.define("NOC.sa.groupaccess.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.sa.groupaccess.Model",
        "NOC.main.group.LookupField",
        "NOC.sa.managedobjectselector.LookupField"
    ],
    model: "NOC.sa.groupaccess.Model",
    columns: [
        {
            text: "Group",
            dataIndex: "group",
            renderer: NOC.render.Lookup("group")
        },
        {
            text: "Selector",
            dataIndex: "selector",
            renderer: NOC.render.Lookup("selector")
        }
    ],
    fields: [
        {
            name: "group",
            xtype: "main.group.LookupField",
            fieldLabel: "Group",
            allowBlank: false
        },
        {
            name: "selector",
            xtype: "sa.managedobjectselector.LookupField",
            fieldLabel: "Object Selector",
            allowBlank: false
        }
    ],
    filters: [
        {
            title: "By Group",
            name: "group",
            ftype: "lookup",
            lookup: "main.group"
        },
        {
            title: "By Selector",
            name: "selector",
            ftype: "lookup",
            lookup: "sa.managedobjectselector"
        }
    ]
});
