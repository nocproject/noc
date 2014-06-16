//---------------------------------------------------
// Ext.ux.form.MultiIntervalField
//     ExtJS4 form field
//     Embedded grid
//---------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------
Ext.define("Ext.ux.form.MultiIntervalField", {
    extend: "Ext.form.FieldContainer",
    mixins: {
        field: 'Ext.form.field.Field'
    },
    requires: [
        "Ext.ux.grid.column.GlyphAction"
    ],
    alias: "widget.multiintervalfield",

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            fields: ["time", "interval"],
            data: []
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            layout: "fit",
            store: me.store,
            columns: [
                {
                    xtype: "glyphactioncolumn",
                    width: 36,
                    items: [
                        {
                            tooltip: "Add",
                            glyph: NOC.glyph.plus_sign,
                            color: NOC.colors.add,
                            scope: me,
                            handler: me.onAddRecord
                        },
                        {
                            tooltip: "Remove",
                            glyph: NOC.glyph.minus_sign,
                            color: NOC.colors.delete,
                            scope: me,
                            handler: me.onRemoveRecord
                        }
                    ]
                },
                {
                    text: "Time (sec)",
                    dataIndex: "time",
                    width: 150,
                    editor: "textfield",
                    renderer: function(v) {
                        if(v) {
                            return v;
                        } else {
                            return "Forever";
                        }
                    }
                },
                {
                    text: "Interval (sec)",
                    dataIndex: "interval",
                    flex: 150,
                    editor: "textfield",
                    renderer: function(v) {
                        if(!v) {
                            return "Disabled";
                        } else {
                            return v;
                        }
                    }
                }
            ],
            plugins: [
                Ext.create("Ext.grid.plugin.CellEditing", {
                    clicksToEdit: 2
                })
            ],
            viewConfig: {
                plugins: {
                    ptype: 'gridviewdragdrop',
                    dragText: 'Drag and drop to reorganize'
                }
            }
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
            v = [];
        me.store.each(function(r) {
            var time = r.get("time"),
                interval = r.get("interval");
            v.push(time ? String(time) : "");
            v.push(String(interval));
        }, this);
        return v.join(",")
    },

    setValue: function(v) {
        var me = this,
            parts = v.split(","),
            data = [];
        for(var i = 0; i < parts.length; i += 2) {
            data.push({
                time: parts[i] !== "" ? parseInt(parts[i]) : null,
                interval: parseInt(parts[i + 1])
            });
        }
        me.store.loadData(data);
        return me.mixins.field.setValue.call(me, v);
    },

    onAddRecord: function(grid, rowIndex) {
        var me = this;
        me.store.insert(rowIndex + 1, [{time: null, interval: 0}])
    },

    onRemoveRecord: function(grid, rowIndex) {
        var me = this;
        me.store.removeAt(rowIndex);
        // Add empty line
    }
});
