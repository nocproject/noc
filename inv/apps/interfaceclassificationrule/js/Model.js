//---------------------------------------------------------------------
// inv.interfaceclassificationrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceclassificationrule.Model");

Ext.define("NOC.inv.interfaceclassificationrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/interfaceclassificationrule/",

    fields: [
        {
            name: "id",
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
            name: "name",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "selector",
            type: "int"
        },
        {
            name: "selector__label",
            type: "string",
            persist: false
        },
        {
            name: "order",
            type: "int"
        },
        {
            name: "match",
            type: "auto"
        },
        {
            name: "description",
            type: "string"
        },
        // CSS
        {
            name: "row_class",
            type: "string",
            persist: false
        },
        {
            name: "match_expr",
            type: "string",
            persist: false
        }
    ]
});
