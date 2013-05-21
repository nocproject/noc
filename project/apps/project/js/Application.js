//---------------------------------------------------------------------
// project.project application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.project.project.Application");

Ext.define("NOC.project.project.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.project.project.Model"
    ],
    model: "NOC.project.project.Model",
    search: true,
    columns: [
        {
            text: "Code",
            dataIndex: "code",
            width: 150
        },
        {
            text: "Name",
            dataIndex: "name",
            width: 300
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        }
    ],
    fields: [
        {
            name: "code",
            xtype: "textfield",
            fieldLabel: "Code",
            allowBlank: false
        },
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
        }
    ]
});
