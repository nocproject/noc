//---------------------------------------------------------------------
// sa.managed_object InteractionsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.InteractionsPanel");

Ext.define("NOC.sa.managedobject.InteractionsPanel", {
    extend: "Ext.panel.Panel",
    app: null,
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

         me.refreshButton = Ext.create("Ext.button.Button", {
            text: "Refresh",
            glyph: NOC.glyph.refresh,
            scope: me,
            handler: me.onRefresh
        });

        me.store = Ext.create("Ext.data.Store", {
            fields: [
                {
                    name: "ts",
                    type: "date"
                },
                {
                    name: "op",
                    type: "integer"
                },
                {
                    name: "user",
                    type: "string"
                },
                {
                    name: "text",
                    type: "string"
                }
            ]
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            stateful: true,
            stateId: "sa.managedobject-interactions",
            columns: [
                {
                    text: "Date",
                    dataIndex: "ts",
                    width: 120,
                    renderer: NOC.render.DateTime
                },
                {
                    text: "Operation",
                    dataIndex: "op",
                    width: 100,
                    renderer: NOC.render.Choices({
                        0: "Command",
                        1: "Login",
                        2: "Logout",
                        3: "Reboot",
                        4: "Started",
                        5: "Halted",
                        6: "Config"
                    })
                },
                {
                    text: "User",
                    dataIndex: "user",
                    width: 100
                },
                {
                    text: "Text",
                    dataIndex: "text",
                    flex: 1
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.closeButton,
                        me.refreshButton,
                    ]
                }
            ],
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me)
            }
        });

        Ext.apply(me, {
            items: [
                me.grid
            ]
        });
        me.callParent();
    },
    //
    preview: function(record) {
        var me = this;
        me.currentRecord = record;
        me.setTitle(record.get("name") + " commands");
        Ext.Ajax.request({
            url: "/sa/managedobject/" + record.get("id") + "/interactions/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.store.loadData(data);
            },
            failure: function() {
                NOC.error("Failed to load data");
            }
        });
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    },
    //
    getRowClass: function(record) {
        var me = this;
        switch(record.get("op")) {
            case 0:
                return "noc-int-command";
            case 1:
                return "noc-int-login";
            case 2:
                return "noc-int-logout";
            case 3:
            case 5:
                return "noc-int-reboot";
            case 4:
                return "noc-int-started";
            case 6:
                return "noc-int-config";
        }
    },
    //
    onRefresh: function() {
        var me = this;
        me.preview(me.currentRecord);
    }
});
