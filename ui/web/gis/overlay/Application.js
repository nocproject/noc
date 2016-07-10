//---------------------------------------------------------------------
// gis.overlay application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.overlay.Application");

Ext.define("NOC.gis.overlay.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.gis.overlay.Model"],
    model: "NOC.gis.overlay.Model",
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Gate Id",
            dataIndex: "gate_id"
        },
        {
            text: "Active",
            dataIndex: "is_active"
        },
        {
            text: "Plugin",
            dataIndex: "plugin"
        },
        {
            text: "Permission",
            dataIndex: "permission_name"
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
            name: "gate_id",
            xtype: "textfield",
            fieldLabel: "Gate Id",
            allowBlank: false,
            regex: /^[a-zA-Z0-9_\-]+$/
        },
        {
            name: "Active",
            xtype: "checkboxfield",
            boxLabel: "is_active"
        },
        {
            name: "Plugin",
            xtype: "textfield",
            fieldLabel: "plugin",
            allowBlank: false
        },
        {
            name: "Permission",
            xtype: "textfield",
            fieldLabel: "permission_name",
            allowBlank: false
        }
    ]
});
