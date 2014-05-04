//---------------------------------------------------------------------
// inv.coverage BuildingModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.coverage.BuildingModel");

Ext.define("NOC.inv.coverage.BuildingModel", {
    extend: "Ext.data.Model",
    rest_url: "/inv/coverage/{{parent}}/buildings/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "preference",
            type: "integer"
        },
        {
            name: "building",
            type: "string"
        },
        {
            name: "building__label",
            type: "string",
            persist: false
        },
        {
            name: "entrance",
            type: "string"
        }
    ]
});
