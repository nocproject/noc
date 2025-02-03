//---------------------------------------------------------------------
// sa.serviceinstance Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.serviceinstance.Model");

Ext.define("NOC.sa.serviceinstance.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/serviceinstance/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "label",
            type: "string"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "fqdn",
            type: "string"
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "service",
            type: "string"
        },
        {
            name: "service_label",
            type: "string",
            persist: false
        },
        {
            name: "managed_object",
            type: "string"
        },
        {
            name: "managed_object__label",
            type: "string",
            persist: false
        },
        {
            name: "addresses",
            type: "auto"
        },
        {
            name: "macs",
            type: "auto"
        }
    ]
});
