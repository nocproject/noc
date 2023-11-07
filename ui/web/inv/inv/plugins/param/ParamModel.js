//---------------------------------------------------------------------
// inv.inv ParamModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.param.ParamModel");

Ext.define("NOC.inv.inv.plugins.param.ParamModel", {
    extend: "Ext.data.Model",
    fields: [
        {
            name: "choices",
            type: "auto"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "is_readonly",
            type: "boolean"
        },
        {
            name: "param",
            type: "string"
        },
        {
            name: "param__label",
            type: "string"
        },
        {
            name: "scope",
            type: "string"
        },
        {
            name: "scope__label",
            type: "string"
        },
        {
            name: "value",
            type: "auto"
        },
        {
            name: "type",
            type: "string"
        }
    ]
});
