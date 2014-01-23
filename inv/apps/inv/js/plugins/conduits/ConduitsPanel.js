//---------------------------------------------------------------------
// inv.inv Conduits panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.conduits.ConduitsPanel");

Ext.define("NOC.inv.inv.plugins.conduits.ConduitsPanel", {
    extend: "Ext.panel.Panel",
    requires: [
    ],
    title: "Conduits",
    closable: false,
    layout: "fit",
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.conduitsForm = Ext.create("NOC.inv.inv.plugins.conduits.ConduitsForm", {
            app: me
        });
        Ext.apply(me, {
            items: [me.conduitsForm]
        });
        me.callParent();
    },
    //
    preview: function(data) {
        var me = this;
        me.currentId = data.id;
        me.conduitsForm.preview(data);
    },
    //
    reload: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/conduits/",
            scope: me,
            success: function(response) {
                me.preview(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        })
    }
});
