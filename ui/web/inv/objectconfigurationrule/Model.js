//---------------------------------------------------------------------
// inv.objectconfigurationrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectconfigurationrule.Model");

Ext.define("NOC.inv.objectconfigurationrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/objectconfigurationrule/",

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
            name: "connection_rules",
            type: "auto"
        },
        {
            name: "param_rules",
            type: "auto"
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
            name: "name",
            type: "string"
        }
    ]
});
