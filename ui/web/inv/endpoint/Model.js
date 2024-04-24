//---------------------------------------------------------------------
// inv.endpoint Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.endpoint.Model");

Ext.define("NOC.inv.endpoint.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/endpoint/",

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
            name: "channel",
            type: "string"
        },
        {
            name: "channel__label",
            type: "string",
            persist: false
        },
        {
            name: "tech_domain",
            type: "string"
        },
        {
            name: "tech_domain__label",
            type: "string",
            persist: false
        },
        {
            name: "model",
            type: "string"
        },
        {
            name: "resource_id",
            type: "string"
        },
        {
            name: "slot",
            type: "string"
        },
        {
            name: "discriminator",
            type: "string"
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "effective_labels",
            type: "auto",
            persist: false
        }
    ]
});