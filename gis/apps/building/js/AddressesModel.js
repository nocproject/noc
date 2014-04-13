//---------------------------------------------------------------------
// gis.building Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.building.AddressesModel");

Ext.define("NOC.gis.building.AddressesModel", {
    extend: "Ext.data.Model",
    rest_url: "/gis/building/{{parent}}/addresses/",
    parentField: "building",

    fields: [
        {
            name: "street",
            type: "string"
        },
        {
            name: "street__label",
            type: "string",
            persist: false
        },
        {
            name: "id",
            type: "string"
        },
        {
            name: "num",
            type: "string"
        },
        {
            name: "num2",
            type: "string"
        },
        {
            name: "num_letter",
            type: "string"
        },
        {
            name: "build",
            type: "string"
        },
        {
            name: "build_letter",
            type: "string"
        },
        {
            name: "struct",
            type: "string"
        },
        {
            name: "struct2",
            type: "string"
        },
        {
            name: "struct_letter",
            type: "string"
        },
        {
            name: "estate",
            type: "string"
        },
        {
            name: "estate2",
            type: "string"
        },
        {
            name: "estate_letter",
            type: "string"
        },
        {
            name: "text_address",
            type: "string",
            persist: false
        },
        {
            name: "is_primary",
            type: "boolean"
        }
    ]
});
