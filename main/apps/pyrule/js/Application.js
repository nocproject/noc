//---------------------------------------------------------------------
// main.pyrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pyrule.Application");

Ext.define("NOC.main.pyrule.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.main.pyrule.Model"],
    model: "NOC.main.pyrule.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
        },

        {
            text: "Interface",
            dataIndex: "interface"
        },

        {
            dataIndex: "is_builtin",
            text: "Is Builtin",
            renderer: noc_renderBool,
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
            name: "interface",
            xtype: "textfield",
            fieldLabel: "Interface",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textareafield",
            fieldLabel: "Description",
            allowBlank: false,
            anchor: "100%"
        },
        {
            name: "text",
            xtype: "textareafield",
            fieldLabel: "Text",
            allowBlank: false,
            anchor: "100%",
            fieldStyle: {
                fontFamily: "Courier"
            }
        },
        {
            name: "is_builtin",
            xtype: "checkboxfield",
            boxLabel: "Is Builtin"
        }
    ]
});
