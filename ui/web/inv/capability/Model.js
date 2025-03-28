//---------------------------------------------------------------------
// inv.capability Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.capability.Model");

Ext.define("NOC.inv.capability.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/capability/",

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
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "card_template",
            type: "string"
        },
        {
            name: "agent_collector",
            type: "string"
        },
        {
            name: "agent_param",
            type: "string"
        },
        {
            name: "values",
            type: "auto"
        },
        {
            name: "enable_horizontal_transit",
            type: "boolean"
        },
        {
            name: "multi",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "allow_manual",
            type: "boolean",
            defaultValue: false
        }
    ]
});
