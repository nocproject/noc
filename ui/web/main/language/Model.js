//---------------------------------------------------------------------
// main.language Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.language.Model");

Ext.define("NOC.main.language.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/language/",

    fields: [
        {
            name: "id",
            type: "string"
        },

        {
            name: "name",
            type: "string"
        },

        {
            name: "native_name",
            type: "string"
        },
        
        {
            name: "is_active",
            type: "boolean",
            defaultValue: false
        }
    ]
});
