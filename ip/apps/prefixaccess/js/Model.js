//---------------------------------------------------------------------
// ip.prefixaccess Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefixaccess.Model");

Ext.define("NOC.ip.prefixaccess.Model", {
    extend: "Ext.data.Model",
    rest_url: "/ip/prefixaccess/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "user",
            type: "int"
        },
        {
            name: "user__label",
            type: "string",
            persist: false
        },
        {
            name: "vrf",
            type: "int"
        },
        {
            name: "vrf__label",
            type: "string",
            persist: false
        },
        {
            name: "afi",
            type: "string"
        },
        {
            name: "prefix",
            type: "string"
        },
        {
            name: "can_view",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "can_change",
            type: "boolean",
            defaultValue: false
        }
    ]
});
