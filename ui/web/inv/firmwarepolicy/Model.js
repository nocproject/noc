//---------------------------------------------------------------------
// inv.firmwarepolicy Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.firmwarepolicy.Model");

Ext.define("NOC.inv.firmwarepolicy.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/firmwarepolicy/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "status",
            type: "string"
        },
        {
            name: "object_profile",
            type: "int"
        },
        {
            name: "firmware",
            type: "string"
        },
        {
            name: "condition",
            type: "string"
        },
        {
            name: "platform",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "management",
            type: "auto"
        },
        {
            name: "firmware__label",
            type: "string",
            persist: false
        },
        {
            name: "object_profile__label",
            type: "string",
            persist: false
        }
    ]
});
