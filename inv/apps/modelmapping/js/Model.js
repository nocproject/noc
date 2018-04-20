//---------------------------------------------------------------------
// inv.modelmapping Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.modelmapping.Model");

Ext.define("NOC.inv.modelmapping.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/modelmapping/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "vendor",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "part_no",
            type: "string"
        },
        {
            name: "to_serial",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "from_serial",
            type: "string"
        },
        {
            name: "model",
            type: "string"
        },
        {
            name: "model__label",
            type: "string",
            persist: false
        }
    ]
});
