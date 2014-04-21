//---------------------------------------------------------------------
// ip.ippool Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.terminationgroup.IPPoolModel");

Ext.define("NOC.sa.terminationgroup.IPPoolModel", {
    extend: "Ext.data.Model",
    rest_url: "/sa/terminationgroup/{{parent}}/ippool/",
    parentField: "termination_group_id",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "vrf",
            type: "int"
        },
        {
            name: "vrf__label",
            type: "string",
            persist: false
        },
        {
            name: "afi",
            type: "string"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "from_address",
            type: "string"
        },
        {
            name: "to_address",
            type: "string"
        }
    ]
});
