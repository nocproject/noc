//---------------------------------------------------------------------
// wf.solution application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.solution.Application");

Ext.define("NOC.wf.solution.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.wf.solution.Model"
    ],
    model: "NOC.wf.solution.Model",
    columns: [
        {
            text: __("Name"),
            dataIndex: "name",
            width: 200
        },
        {
            text: __("Version"),
            dataIndex: "version",
            width: 70
        },
        {
            text: __("Act"),
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: __("Workflows"),
            dataIndex: "wf_count",
            width: 70
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
            name: "version",
            xtype: "numberfield",
            fieldLabel: __("Version"),
            allowBlank: false,
            defaultValue: 1
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: __("Active")
        },
        {
            name: "description",
            xtype: "textarea",
            allowBlank: true,
            fieldLabel: __("Description")
        }
    ]
});
