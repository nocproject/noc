//---------------------------------------------------------------------
// inv.modelmapping application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.modelmapping.Application");

Ext.define("NOC.inv.modelmapping.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.modelmapping.Model",
        "NOC.inv.objectmodel.LookupField"
    ],
    model: "NOC.inv.modelmapping.Model",
    columns: [
        {
            text: "Vendor",
            dataIndex: "vendor",
            width: 100
        },
        {
            text: "Part No",
            dataIndex: "part_no",
            width: 75
        },
        {
            text: "From serial",
            dataIndex: "from_serial",
            width: 75
        },
        {
            text: "To serial",
            dataIndex: "to_serial",
            width: 75
        },
        {
            text: "Model",
            dataIndex: "model",
            renderer: NOC.render.Lookup("model"),
            width: 200
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
            name: "vendor",
            xtype: "textfield",
            fieldLabel: "Vendor",
            allowBlank: false
        },
        {
            name: "part_no",
            xtype: "textfield",
            fieldLabel: "Part No",
            allowBlank: true
        },
        {
            name: "from_serial",
            xtype: "textfield",
            fieldLabel: "From Serial",
            allowBlank: true
        },
        {
            name: "to_serial",
            xtype: "textfield",
            fieldLabel: "To Serial",
            allowBlank: true
        },
        {
            name: "model",
            xtype: "inv.objectmodel.LookupField",
            fieldLabel: "Model",
            allowBlank: false
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Active"
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        }
    ]
});
