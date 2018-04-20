//---------------------------------------------------------------------
// wf.solution application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.solution.Application");

Ext.define("NOC.wf.solution.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.wf.solution.Model"
    ],
    model: "NOC.wf.solution.Model",
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
        },
        {
            text: "Version",
            dataIndex: "version",
            width: 70
        },
        {
            text: "Act",
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Workflows",
            dataIndex: "wf_count",
            width: 70
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
            name: "version",
            xtype: "numberfield",
            fieldLabel: "Version",
            allowBlank: false,
            defaultValue: 1
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Active"
        },
        {
            name: "description",
            xtype: "textarea",
            allowBlank: true,
            fieldLabel: "Description"
        }
    ]
});
