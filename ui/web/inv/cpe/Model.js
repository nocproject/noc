//---------------------------------------------------------------------
// inv.cpe Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.cpe.Model");

Ext.define("NOC.inv.cpe.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/cpe/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "controller",
            type: "int"
        },
        {
            name: "controller__label",
            type: "string",
            persist: false
        },
        {
            name: "global_id",
            type: "string"
        },
        {
            name: "local_id",
            type: "string"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "profile",
            type: "string"
        },
        {
            name: "state",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "caps",
            type: "auto"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        }
    ]
});