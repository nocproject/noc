//---------------------------------------------------------------------
// pm.probe application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.probe.Application");

Ext.define("NOC.pm.probe.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.pm.pmprobe.Model"
    ],
    model: "NOC.pm.probe.Model",
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
            flex: 1
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            allowBlank: false,
            fieldLabel: "Name"
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Active"
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "Active",
            name: "is_active",
            ftype: "boolean"
        }
    ]
});
