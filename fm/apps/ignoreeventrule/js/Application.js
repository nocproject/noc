//---------------------------------------------------------------------
// fm.ignoreeventrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.ignoreeventrule.Application");

Ext.define("NOC.fm.ignoreeventrule.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.fm.ignoreeventrules.Model"],
    model: "NOC.fm.ignoreeventrule.Model",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Active",
            dataIndex: "is_active",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Left RE",
            dataIndex: "left_re",
            flex: 1
        },
        {
            text: "Right RE",
            dataIndex: "right_re",
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
            name: "left_re",
            xtype: "textfield",
            fieldLabel: "Left RE",
            allowBlank: false
        },
        {
            name: "right_re",
            xtype: "textfield",
            fieldLabel: "Right Re",
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
            title: "By Is Active",
            name: "is_active",
            ftype: "boolean"
        }
    ]
});
