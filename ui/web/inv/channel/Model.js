//---------------------------------------------------------------------
// inv.channel Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.channel.Model");

Ext.define("NOC.inv.channel.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/channel/",

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
            name: "project",
            type: "int"
        },
        {
            name: "project__label",
            type: "string",
            persist: false
        },
        {
            name: "supplier",
            type: "string"
        },
        {
            name: "supplier__label",
            type: "string",
            persist: false
        },
        {
            name: "subscriber",
            type: "string"
        },
        {
            name: "subscriber__label",
            type: "string",
            persist: false
        },
        {
            name: "is_free",
            type: "boolean"
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "effective_labels",
            type: "auto",
            persist: false
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "bi_id",
            type: "int",
            persist: false
        }
    ]
});