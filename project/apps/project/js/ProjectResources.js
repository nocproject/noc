//---------------------------------------------------------------------
// VC Interfaces
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.project.project.ProjectResources");

Ext.define("NOC.project.project.ProjectResources", {
    extend: "Ext.panel.Panel",
    app: null,
    vc: null,
    interfaces: [],
    layout: "fit",
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.closeButton = Ext.create("Ext.button.Button", {
            text: "Close",
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose
        });

        Ext.apply(me, {
            items: [
                {
                    xtype: "panel",
                    padding: 4,
                    layout: "fit",
                    html: ""
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.closeButton,
                        me.refreshButton
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
    preview: function(record) {
        var me = this;
        Ext.Ajax.request({
            url: "/project/project/" + record.get("id") + "/resources/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.items.items[0].update(me.app.templates.AllocatedResources(data));
            },
            failure: function() {
                NOC.error("Failed to get resources");
            }
        });
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    }
});
