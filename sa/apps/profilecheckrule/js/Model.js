//---------------------------------------------------------------------
// sa.profilecheckrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.profilecheckrule.Model");

Ext.define("NOC.sa.profilecheckrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/profilecheckrule/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "profile",
            type: "string"
        },
        {
            name: "match_method",
            type: "string",
            defaultValue: "eq"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "value",
            type: "string"
        },
        {
            name: "param",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "preference",
            type: "int",
            defaultValue: 1000
        },
        {
            name: "action",
            type: "string",
            defaultValue: "match"
        },
        {
            name: "category",
            type: "string"
        },
        {
            name: "method",
            type: "string",
            defaultValue: "snmp_v2c_get"
        },
        {
            name: "uuid",
            type: "string"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        }
    ]
});
