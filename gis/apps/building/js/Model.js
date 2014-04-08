//---------------------------------------------------------------------
// gis.building Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.building.Model");

Ext.define("NOC.gis.building.Model", {
    extend: "Ext.data.Model",
    rest_url: "/gis/building/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "status",
            type: "string"
        },
        {
            name: "homes",
            type: "int"
        },
        {
            name: "is_administrative",
            type: "boolean"
        },
        {
            name: "end_date",
            type: "date"
        },
        {
            name: "postal_code",
            type: "string"
        },
        {
            name: "has_attic",
            type: "boolean"
        },
        {
            name: "floors",
            type: "int"
        },
        {
            name: "has_cellar",
            type: "boolean"
        },
        {
            name: "is_habitated",
            type: "boolean"
        },
        {
            name: "entrances",
            type: "auto"
        },
        {
            name: "data",
            type: "auto"
        },
        {
            name: "start_date",
            type: "date"
        },
        {
            name: "adm_division",
            type: "string"
        },
        {
            name: "adm_division__label",
            type: "string",
            persist: false
        },
        {
            name: "full_path",
            type: "string",
            persist: false
        }
    ]
});
