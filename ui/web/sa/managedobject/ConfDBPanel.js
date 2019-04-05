//---------------------------------------------------------------------
// sa.managedobject ConfDBPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.ConfDBPanel");

Ext.define("NOC.sa.managedobject.ConfDBPanel", {
    extend: "NOC.core.ApplicationPanel",
    app: null,
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.currentObject = null;
        me.defaultRoot = {
            text: __("."),
            expanded: true,
            children: []
        };

        me.store = Ext.create("Ext.data.TreeStore", {
            root: me.defaultRoot
        });
        me.confDBPanel = Ext.create("Ext.tree.Panel", {
            store: me.store,
            rootVisible: false,
            useArrows: true
        });
        me.refreshButton = Ext.create("Ext.button.Button", {
            text: __("Refresh"),
            glyph: NOC.glyph.refresh,
            scope: me,
            handler: me.onRefresh
        });
        Ext.apply(me, {
            items: [
                me.confDBPanel
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.getCloseButton(),
                        me.refreshButton
                    ]
                }
            ]
        });
        me.callParent();
    },
    //
    setConfDB: function(data) {
        var me = this,
            result = {
                text: ".",
                expanded: true,
                children: []
            },
            applyNode = function(node, conf) {
                Ext.each(conf, function (item) {
                    var r = {
                        text: item.node
                    };
                    if (item.children) {
                        r.children = [];
                        applyNode(r, item.children);
                        r.expanded = r.children.length < 100
                    } else {
                        r.leaf = true
                    }
                    node.children.push(r)
                })
            };
        console.log("->", data);
        applyNode(result, data);
        console.log("<-", result);
        me.store.setRootNode(result)
    },
    //
    preview: function(record, backItem) {
        var me = this;
        me.callParent(arguments);
        me.setTitle(record.get("name") + " ConfDB");
        me.confDBPanel.mask();
        Ext.Ajax.request({
            url: "/sa/managedobject/" + record.get("id") + "/confdb/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.setConfDB(data);
                me.confDBPanel.unmask()
            },
            failure: function() {
                NOC.error(__("Failed to load data"));
                me.confDBPanel.unmask()
            }
        });
    },
    //
    onRefresh: function() {
        var me = this;
        me.preview(me.currentRecord);
    },
    //
    onRefresh: function() {
        var me = this;
        me.preview(me.currentRecord);
    }
});
