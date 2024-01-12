//---------------------------------------------------------------------
// main.style application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.style.Application");

Ext.define("NOC.main.style.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.style.Model",
        "Ext.ux.form.ColorField"
    ],
    model: "NOC.main.style.Model",
    rowClassField: "row_class",
    columns: [
        {
            text: __("Name"),
            dataIndex: "name"
        },
        {
            text: __("Active"),
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: __("Description"),
            dataIndex: "description",
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
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: __("Is Active"),
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
            allowBlank: true
        },
        {
            name: "font_color",
            xtype: "colorfield",
            uiStyle: "medium",
            fieldLabel: __("Font Color"),
            allowBlank: false
        },
        {
            name: "background_color",
            xtype: "colorfield",
            uiStyle: "medium",
            fieldLabel: __("Background Color"),
            allowBlank: false
        },
        {
            name: "bold",
            xtype: "checkboxfield",
            boxLabel: __("Bold"),
            allowBlank: false
        },
        {
            name: "italic",
            xtype: "checkboxfield",
            boxLabel: __("Italic"),
            allowBlank: false
        },
        {
            name: "underlined",
            xtype: "checkboxfield",
            boxLabel: __("Underlined"),
            allowBlank: false
        }
    ],
    filters: [
        {
            title: __("By Active"),
            name: "is_active",
            ftype: "boolean"
        }
    ]
});
