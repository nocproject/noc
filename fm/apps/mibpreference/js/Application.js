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
            dataIndex: "preference"
        },
        {
            text: "Builtin",
            dataIndex: "is_builtin",
            renderer: noc_renderBool
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
    ]
});
