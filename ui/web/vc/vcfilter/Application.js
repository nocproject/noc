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
            text: __("Name"),
            dataIndex: "name"
        },
        {
            text: __("Expression"),
            dataIndex: "expression",
            flex: 1
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
            name: "expression",
            xtype: "textfield",
            fieldLabel: __("Expression"),
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true
        }
    ],
    filters: [
        {
            title: __("By VC"),
            name: "expression",
            ftype: "vc"
        }
    ]
});
