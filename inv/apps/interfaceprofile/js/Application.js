//---------------------------------------------------------------------
// inv.interfaceprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceprofile.Application");

Ext.define("NOC.inv.interfaceprofile.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
        "NOC.inv.interfaceprofile.Model"
    ],
    model: "NOC.inv.interfaceprofile.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Link Events",
            dataIndex: "link_events",
            renderer: function(value) {
                return {
                    "I": "Ignore",
                    "L": "Log",
                    "A": "Raise"
                }[value];
            }
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
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "link_events",
            xtype: "combobox",
            fieldLabel: "Link Events",
            allowBlank: false,
            queryMode: "local",
            displayField: "label",
            valueField: "id",
            store: {
                fields: ["id", "label"],
                data: [
                    {id: "I", label: "Ignore Link Events"},
                    {id: "L", label: "Log events, do not raise alarms"},
                    {id: "A", label: "Raise alarms"}
                ]
            }
        }
    ]
});
