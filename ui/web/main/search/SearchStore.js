//---------------------------------------------------------------------
// SearchStore
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.search.SearchStore");

Ext.define("NOC.main.search.SearchStore", {
    extend: "Ext.data.Store",
    model: null,
    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "title",
            type: "string"
        },
        {
            name: "card",
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
        },
        {
            name: "info",
            type: "auto"
        }
    ],
    data: []
});