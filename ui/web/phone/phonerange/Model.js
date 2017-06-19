//---------------------------------------------------------------------
// phone.phonerange Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonerange.Model");

Ext.define("NOC.phone.phonerange.Model", {
    extend: "Ext.data.Model",
    rest_url: "/phone/phonerange/",

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
            name: "profile__label",
            type: "string",
            persist: false
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "parent",
            type: "string"
        },
        {
            name: "to_number",
            type: "string"
        },
        {
            name: "project",
            type: "int"
        },
        {
            name: "project__label",
            type: "int",
            persist: false
        },
        {
            name: "from_number",
            type: "string"
        },
        {
            name: "supplier",
            type: "string"
        },
        {
            name: "supplier__label",
            type: "string",
            persist: true
        },
        {
            name: "dialplan",
            type: "string"
        },
        {
            name: "dialplan__label",
            type: "string",
            persist: false
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "total_numbers",
            type: "int",
            persist: false
        },
        {
            name: "to_allocate_numbers",
            type: "boolean"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        },
        {
            name: "administrative_domain",
            type: "string"
        },
        {
            name: "administrative_domain__label",
            type: "string",
            persist: false
        },
        {
            name: "termination_group",
            type: "string"
        },
        {
            name: "termination_group__label",
            type: "string",
            persist: false
        }
    ]
});
