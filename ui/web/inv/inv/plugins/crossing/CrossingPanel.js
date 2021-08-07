//---------------------------------------------------------------------
// inv.inv SensorPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.crossing.CrossingPanel");

Ext.define("NOC.inv.inv.plugins.crossing.CrossingPanel", {
    extend: "Ext.panel.Panel",
    title: __("Crossing"),
    closable: false,
    layout: "fit",
    requires: [
        "Ext.ux.form.GridField"
    ],
    initComponent: function() {
        var me = this;

        me.gridField = Ext.create({
            xtype: "gridfield",
            save: false,
            saveHandler: me.saveHandler,
            columns: [
                {
                    dataIndex: "name",
                    text: __("Name"),
                    width: 300
                },
                {
                    dataIndex: "object_start__label",
                    text: __("Object Start"),
                    width: 200
                },
                {
                    dataIndex: "object_start_slot",
                    text: __("Object Start Slot"),
                    width: 70
                },
                {
                    dataIndex: "object_end__label",
                    text: __("Object End"),
                    width: 200
                },
                {
                    dataIndex: "object_end_slot",
                    text: __("Object End Slot"),
                    width: 70
                },
                {
                    dataIndex: "model__label",
                    text: __("Model"),
                    width: 200
                },
                {
                    dataIndex: "length",
                    text: __("Length"),
                },
            ]
        });
        Ext.apply(me, {
            items: [
                me.gridField
            ]
        });
        me.callParent();
    },
    //
    preview: function(data) {
        var me = this;
        me.currentId = data.id;
        me.gridField.store.loadData(data)
    },
    //
    saveHandler: function() {
        var me = this;
        console.log(me);
    }
});
