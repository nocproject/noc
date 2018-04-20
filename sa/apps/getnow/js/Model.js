/**
 * Created by boris on 02.09.14.
 */
//---------------------------------------------------------------------
// fm.event Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.getnow.Model");

Ext.define("NOC.sa.getnow.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/getnow/",
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
            name: "profile_name",
            type: "string"
        },
        {
            name: "last_success",
            type: "string"
        },
        {
            name: "status",
            type: "string"
        },
        {
            name: "last_update",
            type: "string"
        },
        {
            name: "in_progress",
            type: "boolean"
        }

    ]
});
