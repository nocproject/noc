//---------------------------------------------------------------------
// sa.serviceprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.serviceprofile.Model");

Ext.define("NOC.sa.serviceprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/serviceprofile/",

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
            name: "description",
            type: "string"
        },
        {
            name: "card_title_template",
            type: "string"
        },
        {
            name: "glyph",
            type: "string"
        },
        {
            name: "code",
            type: "string"
        },
        {
            name: "interface_profile",
            type: "string"
        },
        {
            name: "weight",
            type: "int"
        },
        {
            name: "show_in_summary",
            type: "boolean"
        },
        {
            name: "interface_profile__label",
            type: "string",
            persist: false
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "remote_system__label",
            type: "string",
            persist: false
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "tags",
            type: "auto"
        }
    ]
});
