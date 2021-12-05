//---------------------------------------------------------------------
// vc.vlanfilter application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vlanfilter.Application");

Ext.define("NOC.vc.vlanfilter.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.vc.vlanfilter.Model"
    ],
    model: "NOC.vc.vlanfilter.Model",
    search: true,
    helpId: "reference-vlanfilter-filter",

    columns: [
        {
            text: __("Name"),
            dataIndex: "name"
        },
        {
            text: __("Include Expression"),
            dataIndex: "include_expression",
            flex: 1
        },
        {
            text: __("Exclude Expression"),
            dataIndex: "exclude_expression",
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
            name: "include_expression",
            xtype: "textfield",
            fieldLabel: __("Include Expression"),
            allowBlank: false
        },
        {
            name: "exclude_expression",
            xtype: "textfield",
            fieldLabel: __("Exclude Expression"),
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
            name: "exclude_expression",
            ftype: "vc"
        }
    ]
});
