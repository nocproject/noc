//---------------------------------------------------------------------
// pm.probe application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.probe.Application");

Ext.define("NOC.pm.probe.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.probe.Model",
        "NOC.main.user.LookupField",
        "NOC.pm.storage.LookupField"
    ],
    model: "NOC.pm.probe.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 200
        },
        {
            text: "Active",
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Instances",
            dataIndex: "n_instances",
            width: 70,
            align: "right"
        },
        {
            text: "Storage",
            dataIndex: "storage",
            width: 100,
            renderer: NOC.render.Lookup("storage")
        },
        {
            text: "Credentials",
            dataIndex: "user",
            flex: 1,
            renderer: NOC.render.Lookup("user")
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            allowBlank: false,
            fieldLabel: "Name",
            regex: /^[0-9a-zA-Z\-_\.]+$/
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Active"
        },
        {
            name: "storage",
            xtype: "pm.storage.LookupField",
            fieldLabel: "Storage"
        },
        {
            name: "user",
            xtype: "main.user.LookupField",
            fieldLabel: "Credentials",
            allowBlank: false
        },
        {
            name: "n_instances",
            xtype: "numberfield",
            fieldLabel: "Instances",
            minValue: 1
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
            title: "Active",
            name: "is_active",
            ftype: "boolean"
        }
    ]
});
