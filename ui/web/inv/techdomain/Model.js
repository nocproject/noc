//---------------------------------------------------------------------
// inv.techdomain Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.techdomain.Model");

Ext.define("NOC.inv.techdomain.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/techdomain/",

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
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "kind",
            type: "string"
        },
        {
            name: "discriminators",
            type: "auto"
        },
        {
            name: "max_endpoints",
            type: "int"
        },
        {
            name: "full_mesh",
            type: "boolean"
        },
        {
            name: "require_unique",
            type: "boolean"
        },
        {
            name: "controller_handler",
            type: "string"
        },
        {
            name: "bi_id",
            type: "int",
            persist: false
        }
    ]
});