//---------------------------------------------------------------------
// main.customfieldenumgroup application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.customfieldenumgroup.Application");

Ext.define("NOC.main.customfieldenumgroup.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.main.customfieldenumgroup.Model"
    ],
    model: "NOC.main.customfieldenumgroup.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
        },
        {
            text: "Act",
            dataIndex: "is_active",
            width: 30,
            renderer: NOC.render.Bool
        },
        {
            name: "Description",
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
        }
    ],
    filters: [{
        title: "Is Active?",
        name: "is_active",
        ftype: "boolean"
    }],
    inlines: [{
        title: "Values",
        model: "NOC.main.customfieldenumgroup.ValuesModel",
        columns: [
            {
                text: "Act",
                dataIndex: "is_active",
                renderer: NOC.render.Bool,
                width: 30,
                editor: "checkbox"
            },
            {
                text: "Key",
                dataIndex: "key",
                width: 150,
                editor: {
                    xtype: "textfield",
                    allowBlank: false
                }
            },
            {
                text: "Value",
                dataIndex: "value",
                flex: 1,
                editor: {
                    xtype: "textfield",
                    allowBlank: false
                }
            }
        ]
    }]
});
