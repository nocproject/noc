//---------------------------------------------------------------------
// cm.configurationparam Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.configurationparam.Model");

Ext.define("NOC.cm.configurationparam.Model", {
    extend: "Ext.data.Model",
    rest_url: "/cm/configurationparam/",

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
            name: "code",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "scopes",
            type: "auto"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "schema",
            type: "auto"
        },
        {
            name: "choices",
            type: "auto"
        },
        {
            name: "choices_scope",
            type: "string"
        },
        {
            name: "choices_scope__label",
            type: "string",
            persist: false
        },
        {
            name: "threshold_type",
            type: "string"
        },
        {
            name: "metric_type",
            type: "string"
        },
        {
            name: "metric_type__label",
            type: "string",
            persist: false
        }
    ]
});