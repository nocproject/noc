//---------------------------------------------------------------------
// fm.oidalias application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.oidalias.Application");

Ext.define("NOC.fm.oidalias.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.fm.oidalias.Model"],
    model: "NOC.fm.oidalias.Model",
    search: true,
    columns: [
        {
            text: "Rewrite OID",
            dataIndex: "rewrite_oid",
            width: 200
        },
        {
            text: "To OID",
            dataIndex: "to_oid",
            width: 200
        },
        {
            text: "Is Builtin",
            dataIndex: "is_builtin",
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
            name: "rewrite_oid",
            xtype: "textfield",
            fieldLabel: "Rewrite OID",
            allowBlank: false,
            regex: /^[0-9]+(\.[0-9]+)+$/
        },
        {
            name: "to_oid",
            xtype: "textfield",
            fieldLabel: "To OID",
            allowBlank: true,
            regex: /^[0-9]+(\.[0-9]+)+$/
        },
        {
            name: "is_builtin",
            xtype: "checkboxfield",
            boxLabel: "Is Builtin"
        },
        {
            name: "description",
            xtype: "textfield",
            fieldLabel: "description",
            allowBlank: true
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
