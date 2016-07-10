//---------------------------------------------------------------------
// fm.oidalias Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.oidalias.Model");

Ext.define("NOC.fm.oidalias.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/oidalias/",

    fields: [
        {
            name: "id",
            type: "string"
        },

        {
            name: "to_oid",
            type: "string"
        },
        {
            name: "rewrite_oid",
            type: "string"
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
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
