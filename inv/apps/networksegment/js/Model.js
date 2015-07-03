//---------------------------------------------------------------------
// inv.networksegment Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.networksegment.Model");

Ext.define("NOC.inv.networksegment.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/networksegment/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "parent",
            type: "string"
        },
        {
            name: "parent__label",
            type: "string",
            persist: false
        },
        {
            name: "settings",
            type: "auto"
        },
        {
            name: "selector",
            type: "integer"
        },
        {
            name: "selector__label",
            type: "string",
            persist: false
        },
        {
            name: "count",
            type: "integer",
            persist: false
        }
    ]
});
