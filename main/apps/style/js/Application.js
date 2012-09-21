//---------------------------------------------------------------------
// main.style application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.style.Application");

Ext.define("NOC.main.style.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.main.style.Model"
    ],
    model: "NOC.main.style.Model",
    rowClassField: "row_class",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Active",
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Description",
            dataIndex: "description",
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
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Is Active",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "font_color",
            xtype: "numberfield",
            fieldLabel: "Font Color",
            allowBlank: false
        },
        {
            name: "background_color",
            xtype: "numberfield",
            fieldLabel: "Background Color",
            allowBlank: false
        },
        {
            name: "bold",
            xtype: "checkboxfield",
            boxLabel: "Bold",
            allowBlank: false
        },
        {
            name: "italic",
            xtype: "checkboxfield",
            boxLabel: "Italic",
            allowBlank: false
        },
        {
            name: "underlined",
            xtype: "checkboxfield",
            boxLabel: "Underlined",
            allowBlank: false
        }
    ],
    filters: [
        {
            title: "By Active",
            name: "is_active",
            ftype: "boolean"
        }
    ]
});
