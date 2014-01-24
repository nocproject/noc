//---------------------------------------------------------------------
// inv.inv application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.Application");

Ext.define("NOC.inv.inv.Application", {
    extend: "NOC.core.Application",
    layout: "border",
    requires: [
        "NOC.inv.inv.NavModel"
    ],
    initComponent: function() {
        var me = this;
        // Navigation tree
        me.defaultRoot = {
            text: ".",
            children: []
        };

        me.store = Ext.create("Ext.data.TreeStore", {
            model: "NOC.inv.inv.NavModel",
            proxy: {
                type: "ajax",
                reader: "json",
                url: "/inv/inv/node/"
            },
            lazyFill: true
        });

        me.navReloadButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.refresh,
            tooltip: "Reload",
            scope: me,
            handler: me.onReloadNav
        });

        me.addButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.plus,
            tooltip: "Add group",
            scope: me,
            handler: me.onAddGroup
        });

        me.removeButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.minus,
            tooltip: "Remove group",
            scope: me,
            handler: me.onRemoveGroup
        });

        me.navTree = Ext.create("Ext.tree.Panel", {
            store: me.store,
            autoScroll: true,
            rootVisible: false,
            useArrows: true,
            region: "west",
            split: true,
            loadMask: true,
            width: 300,
            displayField: "name",
            allowDeselect: true,
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.navReloadButton,
                    "-",
                    me.addButton,
                    me.removeButton
                ]
            }],
            listeners: {
                scope: me,
                select: me.onSelectNav
            },
            viewConfig: {
                plugins: [
                    {
                        ptype: "treeviewdragdrop"
                    }
                ]
            }
        });
        me.navTree.getView().on("drop", me.onNavDrop, me);
        //

        me.tabPanel = Ext.create("Ext.tab.Panel", {
            region: "center",
            layout: "fit",
            border: false,
            autoScroll: true,
            defaults: {
                autoScroll: true
            },
            items: [
            ]
        });
        //
        Ext.apply(me, {
            items: [
                me.navTree,
                me.tabPanel
            ]
        });
        me.callParent();
        // Process commands
        if(me.noc.cmd) {
            switch(me.noc.cmd.cmd) {
                case "history":
                    me.restoreHistory(me.noc.cmd.args);
                    return;
                    break;
            }
        }
    },
    //
    onReloadNav: function() {
        var me = this;
        me.store.reload({node: me.store.getRootNode()});
    },
    //
    runPlugin: function(objectId, pData) {
        var me = this,
            plugin = Ext.create(pData.xtype, {app: me});
        me.tabPanel.add(plugin);
        Ext.Ajax.request({
            url: "/inv/inv/" + objectId + "/plugin/" + pData.name + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                plugin.preview(data);
            },
            failure: function() {
                NOC.error("Failed to get data for plugin " + pData.name);
            }
        });
    },
    //
    onSelectNav: function(panel, record, index, eOpts) {
        var me = this,
            objectId = record.get("id"),
            plugins = record.get("plugins");
        me.addButton.setDisabled(!record.get("can_add"));
        me.tabPanel.removeAll();
        Ext.each(plugins, function(p) {
            me.runPlugin(objectId, p);
        });
        me.setHistoryHash(objectId);
    },
    // Expand nav tree to object
    showObject: function(objectId) {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/inv/" + objectId + "/path/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText),
                    path = [,me.navTree.getRootNode().get("id")];
                path = path.concat(data.map(function(v) {return v.id}));
                me.navTree.selectPath(
                    path.join("/"), "id", "/",
                    function(success, lastNode) {
                        if(!success) {
                            NOC.error("Failed to find node");
                        }
                    }, me
                );
            },
            failure: function(response) {
                NOC.error("Failed to get path");
            }
        })
    },
    //
    onAddGroup: function() {
        var me = this,
            sm = me.navTree.getSelectionModel(),
            sel = sm.getSelection(),
            container = null;
        if(sel.length > 0) {
            container = sel[0];
        }
        Ext.create("NOC.inv.inv.AddGroupForm", {
            app: me,
            groupContainer: container
        });
    },
    //
    onNavDrop: function(node, data, overModel, dropPosition, eOpts) {
        var me = this,
            objects = data.records.map(function(r) {return r.get("id")});
        Ext.Ajax.request({
            url: "/inv/inv/insert/",
            method: "POST",
            jsonData: {
                objects: objects,
                container: overModel.get("id"),
                position: dropPosition
            },
            scope: me,
            success: function() {
            },
            failure: function() {
                NOC.error("Failed to move");
            }
        });
    },
    //
    onRemoveGroup: function() {
        var me = this,
            sm = me.navTree.getSelectionModel(),
            sel = sm.getSelection(),
            container = null;
        if(sel.length > 0) {
            container = sel[0];
        }
        if(container) {
            Ext.Msg.show({
                title: "Remove group '" + container.get("name") + "'?",
                msg: "Would you like to remove group. All nested groups will be removed. All nested objects will be moved to Lost&Found folder",
                buttons: Ext.Msg.YESNO,
                glyph: NOC.glyph.question_sign,
                fn: function(rec) {
                    if(rec === "yes") {
                        Ext.Ajax.request({
                            url: "/inv/inv/remove_group/",
                            method: "DELETE",
                            jsonData: {
                                container: container.get("id")
                            },
                            scope: me,
                            success: function() {
                                me.store.reload({node: me.store.getRootNode()});
                            },
                            failure: function() {
                                NOC.error("Failed to delete group");
                            }
                        });
                    }
                }
            });
        }
    },
    //
    restoreHistory: function(args) {
        var me = this,
            objectId = args[0];
        me.showObject(args[0]);
    }
});
