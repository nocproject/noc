//---------------------------------------------------------------------
// TestCheckForm
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.check.test.TestCheckForm");

Ext.define("NOC.pm.check.test.TestCheckForm", {
    extend: "Ext.form.Panel",
    items: [
        {
            xtype: "numberfield",
            fieldLabel: "Min",
            name: "min",
            allowBlank: false
        },
        {
            xtype: "numberfield",
            fieldLabel: "Max",
            name: "max",
            allowBlank: false
        }
    ]
});
