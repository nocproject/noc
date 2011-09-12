//---------------------------------------------------------------------
// main.language Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.language.Model");

Ext.define("NOC.main.language.Model", {
    //extend: "NOC.core.Model",
    extend: "Ext.data.Model",

    fields: [
        {
            name: "id",
            type: "int"
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
    ],

    //url: "/main/language/"
    proxy: {
        type: "rest",
        url: "/main/language/",
        pageParam: "__page",
        startParam: "__start",
        limitParam: "__limit",
        sortParam: "__sort",
        extraParams: {
            "__format": "ext"
        },
        reader: {
            type: "json",
            root: "data",
            totalProperty: "total",
            successProperty: "success"
        },
        writer: {
            type: "json"
        }    
    }
});
