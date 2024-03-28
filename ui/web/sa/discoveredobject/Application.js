//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.Application");

Ext.define("NOC.sa.discoveredobject.Application", {
    extend: "NOC.core.Application",
    layout: "card",
    reference: "sa-discoveredobject",
    controller: "sa.discoveredobject",
    appId: "sa.discoveredobject",
    viewModel: {
        type: "sa.discoveredobject"
    },
    requires: [
        "Ext.layout.container.Card",
        "NOC.sa.discoveredobject.ApplicationController",
        "NOC.sa.discoveredobject.ApplicationModel",
        "NOC.sa.discoveredobject.view.Container",
    ],
    items: [
        {
            itemId: "sa-discoveredobject-list",
            xtype: "sa.discoveredobject.container",
        },
    ],
    listeners: {
        afterrender: "onAfterRender",
    },
});