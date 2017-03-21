//---------------------------------------------------------------------
// sa.maintainance Objects Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintainance.maintainance.ObjectsModel");

Ext.define("NOC.maintainance.maintainance.ObjectsModel", {
    extend: "Ext.data.Model",

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
            name: "is_managed",
            type: "boolean"
        },
        {
            name: "profile",
            type: "string"
        },
        {
            name: "address",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
        }
    ]
});
