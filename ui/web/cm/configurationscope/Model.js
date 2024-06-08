//---------------------------------------------------------------------
// cm.configurationscope Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.configurationscope.Model");

Ext.define("NOC.cm.configurationscope.Model", {
    extend: "Ext.data.Model",
    rest_url: "/cm/configurationscope/",

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
            name: "model_id",
            type: "string"
        },
        {
            name: "model_id__label",
            type: "string",
            persist: false
        },
        {
            name: "helper",
            type: "string"
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "helper_params",
            type: "auto"
        }
    ]
});