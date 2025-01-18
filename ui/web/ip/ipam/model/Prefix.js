//---------------------------------------------------------------------
// ip.ipam Prefix Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.model.Prefix");

Ext.define("NOC.ip.ipam.model.Prefix", {
    extend: "Ext.data.Model",
    fields: [
        {
            name: "id",
            type: "number"
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
            name: "tt",
            type: "string"
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "pools",
            type: "auto"
        },
        {
            name: "project",
            type: "string"
        },
        {
            name: "state",
            type: "string"
        },
        // {
        //     name: "direct_permissions",
        //     type: "auto"
        // },
        {
            name: "isFree",
            type: "boolean",
            persist: false
        }
    ]
});
