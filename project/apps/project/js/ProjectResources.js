//---------------------------------------------------------------------
// VC Interfaces
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.project.project.ProjectResources");

Ext.define("NOC.project.project.ProjectResources", {
    extend: "Ext.Window",
    app: null,
    vc: null,
    interfaces: [],
    width: 600,
    height: 400,
    modal: true,
    autoShow: true,
    closable: true,
    autoScroll: "auto",
    maximizable: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            title: Ext.String.format("Allocated resources for {0}: {1}", me.project.get("code"), me.project.get("name")),
            items: [
                {
                    xtype: "panel",
                    padding: 4,
                    layout: "fit",
                    html: me.app.templates.AllocatedResources(me.data)
                }
            ]
        });
        me.callParent();
    }
});
