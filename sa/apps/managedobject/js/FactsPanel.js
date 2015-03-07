//---------------------------------------------------------------------
// sa.managedobject FactsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.FactsPanel");

Ext.define("NOC.sa.managedobject.FactsPanel", {
    extend: "NOC.core.ApplicationPanel",
    requires: [
    ],

    initComponent: function() {
        var me = this;

        me.refreshButton = Ext.create("Ext.button.Button", {
            text: "Refresh",
            glyph: NOC.glyph.refresh,
            scope: me,
            handler: me.onRefresh
        });

        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.fm.alarm.Model",
            fields: ["cls", "label", "attrs"],
            data: [],
            groupField: "cls"
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            stateful: true,
            stateId: "sa.managedobject-facts",
            autoScroll: true,
            columns: [
                {
                    text: "Class",
                    dataIndex: "cls",
                    flex: 1
                },
                {
                    text: "Facts",
                    dataIndex: "label",
                    flex: 1
                }
            ],
            plugins: [
                {
                    ptype: "rowexpander",
                    rowBodyTpl: new Ext.XTemplate(
                        "<table>",
                        "<thead>",
                        '<tpl for="attrs">',
                        "<tr>",
                        "<td><b>{name}</b></td>",
                        "<td>{value}</td>",
                        "</tr>",
                        '</tpl>',
                        "</thead>",
                        "</table>"
                    )
                }
            ],
            features: [{
                ftype: "grouping",
                groupHeaderTpl: '{name}: {rows.length} Item{[values.rows.length > 1 ? "s" : ""]}',
                hideGroupedHeader: true,
                startCollapsed: true,
                id: "fcls-grouping"
            }]
        });
        Ext.apply(me, {
            items: [
                me.grid
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
    preview: function(record, backItem) {
        var me = this;
        me.callParent(arguments);
        me.setTitle(record.get("name") + " capabilities");
        Ext.Ajax.request({
            url: "/sa/managedobject/" + me.currentRecord.get("id") + "/facts/",
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
    onRefresh: function() {
        var me = this;
        me.preview(me.currentRecord);
    },
    //
    renderValue: function(v) {
        var me = this;
        return v;
    }
});
