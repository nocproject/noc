//---------------------------------------------------------------------
// fm.alarmseverity application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmseverity.Application");

Ext.define("NOC.fm.alarmseverity.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.fm.alarmseverity.Model",
        "NOC.main.style.LookupField"
    ],
    model: "NOC.fm.alarmseverity.Model",
    rowClassField: "row_class",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Builtin",
            dataIndex: "is_builtin",
            renderer: NOC.render.Bool
        },
        {
            text: "Severity",
            dataIndex: "severity",
            flex: 1
        },
        {
            text: "Description",
            dataIndex: "description"
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "name",
            allowBlank: false
        },
        {
            name: "is_builtin",
            xtype: "checkboxfield",
            boxLabel: "Builtin",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "severity",
            xtype: "numberfield",
            fieldLabel: "Severity",
            allowBlank: false
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: "Style",
            allowBlank: false
        }
    ]
});
