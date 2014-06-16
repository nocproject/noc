//---------------------------------------------------------------------
// inv.interfaceprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceprofile.Application");

Ext.define("NOC.inv.interfaceprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.interfaceprofile.Model",
        "NOC.main.style.LookupField",
        "Ext.ux.form.MultiIntervalField"
    ],
    model: "NOC.inv.interfaceprofile.Model",
    search: true,
    rowClassField: "row_class",
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
        },
        {
            text: "Style",
            dataIndex: "style",
            renderer: NOC.render.Lookup("style")
        },
        {
            text: "MAC",
            dataIndex: "mac_discovery",
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
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: "Style",
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
        },
        {
            name: "check_link_interval",
            xtype: "multiintervalfield",
            fieldLabel: "check_link interval",
            allowBlank: true
        },
        {
            name: "mac_discovery",
            xtype: "checkbox",
            boxLabel: "MAC Discovery",
            allowBlank: true
        }
    ]
});
