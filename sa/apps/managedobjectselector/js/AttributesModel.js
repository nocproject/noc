//---------------------------------------------------------------------
// sa.managedobjectselector AttributesModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectselector.AttributesModel");

Ext.define("NOC.sa.managedobjectselector.AttributesModel", {
    extend: "Ext.data.Model",
    rest_url: "/sa/managedobjectselector/{{parent}}/attrs/",
    parentField: "selector_id",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "key_re",
            type: "string"
        },
        {
            name: "value_re",
            type: "string"
        }
    ]
});