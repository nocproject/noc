//---------------------------------------------------------------------
// sa.managedobjectselector ObjectsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectselector.ObjectsPanel");

Ext.define("NOC.sa.managedobjectselector.ObjectsPanel", {
    extend: "NOC.core.ApplicationPanel",
    requires: ["NOC.sa.managedobjectselector.ObjectsModel"],
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

        me.totalField = Ext.create("Ext.form.field.Display");

        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.sa.managedobjectselector.ObjectsModel"
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
                    text: __("Adm. domain"),
                    dataIndex: "administrative_domain"
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 100
                },
                {
                    text: __("Platform"),
                    dataIndex: "platform",
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
                    text: __("Labels"),
                    dataIndex: "labels",
                    renderer: NOC.render.LabelField,
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
            url: "/sa/managedobjectselector/" + record.get("id") + "/objects/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.grid.setTitle(record.get("name") + " " + __("objects"));
                me.store.loadData(data);
                me.totalField.setValue(__("Total: ") + data.length);
            },
            failure: function() {
                NOC.error(__("Failed to get data"));
            }
        });
    }
});
