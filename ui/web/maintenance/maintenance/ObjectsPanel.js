//---------------------------------------------------------------------
// sa.managedobjectselector ObjectsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenance.ObjectsPanel");

Ext.define("NOC.maintenance.maintenance.ObjectsPanel", {
    extend: "NOC.core.ApplicationPanel",
    requires: ["NOC.maintenance.maintenance.ObjectsModel"],
    mixins: [
        "NOC.core.Export"
    ],
    app: null,
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.refreshButton = Ext.create("Ext.button.Button", {
            text: __("Refresh"),
            glyph: NOC.glyph.refresh,
            scope: me,
            handler: me.onRefresh
        });

        me.exportButton = Ext.create("Ext.button.Button", {
            tooltip: __("Export"),
            text: __("Export"),
            glyph: NOC.glyph.arrow_down,
            scope: me,
            handler: me.onExport
        });

        me.totalField = Ext.create("Ext.form.field.Display");

        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.maintenance.maintenance.ObjectsModel"
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            stateful: true,
            stateId: "sa.managedobjectselector-objects",
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Managed"),
                    dataIndex: "is_managed",
                    renderer: NOC.render.Bool,
                    width: 50
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 100
                },
                {
                    text: __("Address"),
                    dataIndex: "address",
                    width: 100
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                },
                {
                    text: __("Tags"),
                    dataIndex: "tags",
                    renderer: NOC.render.Tags,
                    width: 150
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.getCloseButton(),
                        me.refreshButton,
                        me.exportButton,
                        "->",
                        me.totalField
                    ]
                }
            ]
        });
        Ext.apply(me, {
            items: [me.grid]
        });
        me.callParent();
    },

    preview: function(record, backItem) {
        var me = this;
        me.callParent(arguments);
        Ext.Ajax.request({
            url: "/maintenance/maintenance/" + record.get("id") + "/objects/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.grid.setTitle(record.get("subject") + " " + __("objects"));
                me.store.loadData(data);
                me.totalField.setValue(__("Total: ") + data.length);
            },
            failure: function() {
                NOC.error(__("Failed to get data"));
            }
        });
    },

    onExport: function() {
        var me = this;
        me.save(me.grid, 'affected.csv');
    }
});
