//---------------------------------------------------------------------
// inv.resourcegroup Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.resourcegroup.Model");

Ext.define("NOC.inv.resourcegroup.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/resourcegroup/",

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
            name: "parent",
            type: "string"
        },
        {
            name: "parent__label",
            type: "string",
            persist: false
        },
        {
            name: "bi_id",
            type: "int",
            persist: false
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
            name: "description",
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
        }
    ]
});
