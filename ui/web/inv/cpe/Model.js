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
            type: "int",
            persist: false
        },
        {
            name: "controller__label",
            type: "string",
            persist: false
        },
        {
            name: "label",
            type: "string",
            persist: false
        },
        {
            name: "global_id",
            type: "string",
            persist: false
        },
        {
            name: "local_id",
            type: "string",
            persist: false
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
            name: "profile__label",
            type: "string",
            persist: false
        },
        {
            name: "state",
            type: "string"
        },
        {
            name: "oper_status",
            type: "boolean",
            persist: false
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "controllers",
            type: "auto"
        },
        {
            name: "caps",
            type: "auto"
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
            name: "bi_id",
            type: "string",
            persist: false
        }
    ]
});