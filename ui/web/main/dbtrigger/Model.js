//---------------------------------------------------------------------
// main.dbtrigger Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.dbtrigger.Model");

Ext.define("NOC.main.dbtrigger.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/dbtrigger/",

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
            name: "model",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "order",
            type: "int",
            defaultValue: 100
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "pre_save_rule",
            type: "int"
        },
        {
            name: "pre_save_rule__label",
            type: "string",
            persist: false
        },
        {
            name: "post_save_rule",
            type: "int"
        },
        {
            name: "post_save_rule__label",
            type: "string",
            persist: false
        },
        {
            name: "pre_delete_rule",
            type: "int"
        },
        {
            name: "pre_delete_rule__label",
            type: "string",
            persist: false
        },
        {
            name: "post_delete_rule",
            type: "int"
        },
        {
            name: "post_delete_rule__label",
            type: "string",
            persist: false
        }
    ]
});
