//---------------------------------------------------------------------
// ip.addressprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.addressprofile.Model");

Ext.define("NOC.ip.addressprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/ip/addressprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "style",
            type: "int"
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
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
            name: "workflow",
            type: "string"
        },
        {
            name: "workflow__label",
            type: "string",
            persist: false
        },
        {
            name: "bi_id",
            type: "int"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
