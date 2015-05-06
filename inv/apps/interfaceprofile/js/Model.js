//---------------------------------------------------------------------
// inv.interfaceprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceprofile.Model");

Ext.define("NOC.inv.interfaceprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/interfaceprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "style",
            type: "int"
        },
        {
            name: "link_events",
            type: "string",
            defaultValue: "A"
        },
        {
            name: "mac_discovery",
            type: "bool",
            defaultValue: false
        },
        {
            name: "check_link_interval",
            type: "string"
        },
        // CSS
        {
            name: "row_class",
            type: "string",
            persist: false
        },
        // Foreign keys
        {
            name: "style__label",
            type: "string",
            persist: false
        }
    ]
});
