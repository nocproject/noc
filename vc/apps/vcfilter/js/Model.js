//---------------------------------------------------------------------
// vc.vcfilter Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcfilter.Model");

Ext.define("NOC.vc.vcfilter.Model", {
    extend: "Ext.data.Model",
    rest_url: "/vc/vcfilter/",

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
            name: "expression",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
