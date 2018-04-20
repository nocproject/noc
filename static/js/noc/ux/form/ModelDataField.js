//---------------------------------------------------
// Ext.ux.form.ModelDataField
//     ExtJS4 form field
//     Embedded grid
//---------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------
Ext.define("Ext.ux.form.ModelDataField", {
    extend: "Ext.form.FieldContainer",
    mixins: {
        field: "Ext.form.field.Field"
    },
    alias: "widget.modeldatafield",
    requires: [
        "NOC.inv.modelinterface.LookupField"
    ],

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            fields: ["interface", "key", "value"],
            data: []
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            layout: "fit",
            store: me.store,
            columns: [
                {
                    text: "Interface",
                    dataIndex: "interface",
                    editor: {
                        xtype: "inv.modelinterface.LookupField",
                        forceSelection: true,
                        valueField: "label"
                    }
                },
                {
                    text: "Key",
                    dataIndex: "key",
                    editor: "textfield"
                },
                {
                    text: "Value",
                    dataIndex: "value",
                    editor: "textfield",
                    flex: 1
                }
            ],
            plugins: [
                Ext.create("Ext.grid.plugin.CellEditing", {
                    clicksToEdit: 2
                })
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: "Add",
                            glyph: NOC.glyph.plus,
                            scope: me,
                            handler: me.onAdd
                        },
                        {
                            text: "Delete",
                            glyph: NOC.glyph.minus,
                            scope: me,
                            handler: me.onDelete
                        }
                    ]
                }
            ]
        });

        Ext.apply(me, {
            items: [
                me.grid
            ]
        });
        me.callParent();
    },

    getValue: function() {
        var me = this,
            data = {};
        me.store.each(function(r) {
            var iface = r.get("interface"),
                key = r.get("key"),
                value = r.get("value");
            if(!data[iface]) {
                data[iface] = {}
            }
            if(key) {
                data[iface][key] = value;
            }
        });
        return data;
    },

    setValue: function(v) {
        var me = this,
            records = [],
            iface, key, empty;
        for(iface in v) {
            empty = true;
            for(key in v[iface]) {
                records.push({
                    "interface": iface,
                    key: key,
                    value: v[iface][key]
                });
                empty = false;
            }
            if(empty) {
                records.push({interface: iface, key: "", value: ""});
            }
        }
        me.store.loadData(records);
        return me.mixins.field.setValue.call(me, records);
    },

    //
    onAdd: function() {
        var me = this,
            rowEditing = me.grid.plugins[0];
        rowEditing.cancelEdit();
        me.grid.store.insert(0, {});
        rowEditing.startEdit(0, 0);
    },
    //
    onDelete: function() {
        var me = this,
            sm = me.grid.getSelectionModel(),
            rowEditing = me.grid.plugins[0];
        rowEditing.cancelEdit();
        me.grid.store.remove(sm.getSelection());
        if(me.grid.store.getCount() > 0) {
            sm.select(0);
        }
    }
});
