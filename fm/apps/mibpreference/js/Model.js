//---------------------------------------------------------------------
// fm.mibpreference Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.mibpreference.Model");

Ext.define("NOC.fm.mibpreference.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/mibpreference/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "mib",
            type: "string"
        },
        {
            name: "preference",
            type: "int"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        }
    ]
});
