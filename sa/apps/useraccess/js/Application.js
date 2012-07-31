//---------------------------------------------------------------------
// sa.useraccess application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.useraccess.Application");

Ext.define("NOC.sa.useraccess.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.sa.useraccess.Model",
        "NOC.main.user.LookupField",
        "NOC.sa.managedobjectselector.LookupField"
    ],
    model: "NOC.sa.useraccess.Model",
    columns: [
        {
            text: "User",
            dataIndex: "user",
            renderer: NOC.render.Lookup("user")
        },
        {
            text: "Selector",
            dataIndex: "selector",
            renderer: NOC.render.Lookup("selector")
        }
    ],
    fields: [
        {
            name: "user",
            xtype: "main.user.LookupField",
            fieldLabel: "User",
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
            title: "By User",
            name: "user",
            ftype: "lookup",
            lookup: "main.user"
        },
        {
            title: "By Selector",
            name: "selector",
            ftype: "lookup",
            lookup: "sa.managedobjectselector"
        }
    ]
});
