//---------------------------------------------------------------------
// fm.mibpreference application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.mibpreference.Application");

Ext.define("NOC.fm.mibpreference.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.fm.mibpreference.Model"],
    model: "NOC.fm.mibpreference.Model",
    search: true,
    columns: [
        {
            text: "MIB",
            dataIndex: "mib",
            width: 300
        },
        {
            text: "Pref.",
            dataIndex: "preference",
            width: 100
        },
        {
            text: "Builtin",
            dataIndex: "is_builtin",
            renderer: NOC.render.Bool,
            width: 50
        }
    ],
    fields: [
        {
            name: "mib",
            xtype: "textfield",
            fieldLabel: "MIB",
            allowBlank: false
        },
        {
            name: "preference",
            xtype: "numberfield",
            fieldLabel: "Preference",
            allowBlank: false
        },
        {
            name: "is_builtin",
            xtype: "checkboxfield",
            boxLabel: "Builtin"
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
