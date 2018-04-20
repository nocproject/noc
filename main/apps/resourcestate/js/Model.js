//---------------------------------------------------------------------
// main.resourcestate Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.resourcestate.Model");

Ext.define("NOC.main.resourcestate.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/resourcestate/",

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
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "is_starting",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "is_default",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "is_provisioned",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "step_to",
            type: "int"
        },
        {
            name: "step_to__label",
            type: "string",
            persist: false
        }
    ]
});
