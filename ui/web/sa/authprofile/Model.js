//---------------------------------------------------------------------
// sa.authprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.authprofile.Model");

Ext.define("NOC.sa.authprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/authprofile/",

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
            name: "type",
            type: "string"
        },
        {
            name: "user",
            type: "string"
        },
        {
            name: "password",
            type: "string"
        },
        {
            name: "super_password",
            type: "string"
        },
        {
            name: "snmp_ro",
            type: "string"
        },
        {
            name: "snmp_rw",
            type: "string"
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
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
        }
    ]
});
