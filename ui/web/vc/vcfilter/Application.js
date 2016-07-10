//---------------------------------------------------------------------
// vc.vcfilter application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcfilter.Application");

Ext.define("NOC.vc.vcfilter.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.vc.vcfilter.Model"
    ],
    model: "NOC.vc.vcfilter.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Expression",
            dataIndex: "expression",
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
            name: "expression",
            xtype: "textfield",
            fieldLabel: "Expression",
            allowBlank: false
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
            title: "By VC",
            name: "expression",
            ftype: "vc"
        }
    ]
});
