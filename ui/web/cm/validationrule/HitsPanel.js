//---------------------------------------------------------------------
// sa.managed_object DiscoveryPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationrule.HitsPanel");

Ext.define("NOC.cm.validationrule.HitsPanel", {
    extend: "Ext.panel.Panel",
    app: null,
    layout: "fit",
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.closeButton = Ext.create("Ext.button.Button", {
            text: __("Close"),
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose
        });

        me.store = Ext.create("Ext.data.Store", {
            fields: [
                {
                    name: "managed_object_id",
                    type: "string"
                },
                {
                    name: "managed_object",
                    type: "string"
                },
                {
                    name: "address",
                    type: "string"
                },
                {
                    name: "platform",
                    type: "string"
                },
                {
                    name: "hits",
                    type: "integer"
                }
            ]
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            stateful: true,
            stateId: "cm.validationrule-hits",
            columns: [
                {
                    text: __("Hits"),
                    dataIndex: "hits",
                    width: 50,
                    align: "right",
                    sortable: false,
                    renderer: function(v) {
                        if(v) {
                            return "<span class='x-display-tag'>" + v + "</span>";
                        } else {
                            return ""
                        }
                    }
                },
                {
                    text: __("Object"),
                    dataIndex: "managed_object",
                    width: 120
                },
                {
                    text: __("Address"),
                    dataIndex: "address",
                    width: 70
                },
                {
                    text: __("Platform"),
                    dataIndex: "platform",
                    width: 100
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.closeButton
                    ]
                }
            ]
        });

        Ext.apply(me, {
            items: [me.grid]
        });
        me.callParent();
    },
    //
    preview: function(record) {
        var me = this;
        me.currentRecord = record;
        me.setTitle(record.get("name") + " hits");
        Ext.Ajax.request({
            url: "/cm/validationrule/" + record.get("id") + "/hits/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.store.loadData(data);
            },
            failure: function() {
                NOC.error(__("Failed to load data"));
            }
        });
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    }
});
