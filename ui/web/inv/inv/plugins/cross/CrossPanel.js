//---------------------------------------------------------------------
// inv.inv Cross Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.cross.CrossPanel");

Ext.define("NOC.inv.inv.plugins.cross.CrossPanel", {
    extend: "Ext.panel.Panel",
    title: __("Cross"),
    closable: false,
    layout: "fit",

    initComponent: function () {
        var me = this;
        me.callParent();
    },
    //
    preview: function (data) {
        var me = this;
        me.currentId = data.id;
        me.store.loadData(data.data);
    },
    //
    onReload: function () {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/cross/",
            method: "GET",
            scope: me,
            success: function (response) {
                me.preview(Ext.decode(response.responseText));
            },
            failure: function () {
                NOC.error(__("Failed to get data"));
            }
        });
    },
});
