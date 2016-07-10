//---------------------------------------------------------------------
// main.tag application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.tag.Application");

Ext.define("NOC.main.tag.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.tag.Model"
    ],
    model: "NOC.main.tag.Model",
    columns: [
        /*
        {
            text: "Name",
            dataIndex: "name"
        }*/
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "name",
            allowBlank: false
        }
    ]
});
