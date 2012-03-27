//---------------------------------------------------------------------
// main.pyrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pyrule.Application");

Ext.define("NOC.main.pyrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.pyrule.Model",
        "NOC.main.ref.interface.LookupField"
    ],
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
            text: "Builtin",
            renderer: NOC.render.Bool,
            width: 50
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
            xtype: "main.ref.interface.LookupField",
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
            height: 200,
            fieldStyle: {
                fontFamily: "Courier"
            }
        },
        {
            name: "is_builtin",
            xtype: "checkboxfield",
            boxLabel: "Is Builtin"
        }
    ],
    filters: [
        {
            title: "By Is Builtin",
            name: "is_builtin",
            ftype: "boolean"
        }
    ]
});
