//---------------------------------------------------------------------
// main.language application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.language.Application");

Ext.define("NOC.main.language.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.main.language.Model"],
    
    model: "NOC.main.language.Model",
    
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "Native Name",
            dataIndex: "native_name"
        },
        {
            text: "Active",
            dataIndex: "is_active"
        }
    ],
    
    fields: [
        {
            fieldLabel: "Name",
            name: "name",
            type: "textfield",
            allowBlank: false
        },

        {
            fieldLabel: "Native Name",
            name: "native_name",
            type: "textfield",
            allowBlank: false
        }
    ]
});
