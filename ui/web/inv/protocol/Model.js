//---------------------------------------------------------------------
// inv.protocol Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.inv.protocol.Model");
Ext.define("NOC.inv.protocol.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/protocol/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "technology",
            type: "string"
        },
        {
            name: "technology__label",
            type: "string",
            persist: false
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "uuid",
            type: "string"
        },
        {
            name: "code",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "connection_schema",
            type: "string",
            defaultValue: "BD"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "data",
            type: "auto"
        }
    ]
});
