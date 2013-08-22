//---------------------------------------------------------------------
// main.prefixtable Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.prefixtable.Model");

Ext.define("NOC.main.prefixtable.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/prefixtable/",

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
            name: "description",
            type: "string"
        }
    ]
});
