//---------------------------------------------------
// Ext.ux.form.GridField
//     ExtJS4 form field
//     Embedded grid
//---------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------
Ext.define("Ext.ux.form.GridField", {
    extend: "Ext.form.FieldContainer",
    mixins: {
        field: 'Ext.form.field.Field'
    },
    alias: "widget.gridfield",
    columns: [],
    toolbar: null,

    initComponent: function() {
        var me = this,
            toolbar;

        me.fields = me.columns.map(function(v) {
            return v.dataIndex;
        });

        // Add ghost __label fields
        me.fields = me.fields.concat(me.columns.map(function(v) {
            return {
                name: v.dataIndex + "__label",
                persist: false
            }
        }));

        me.store = Ext.create("Ext.data.Store", {
            fields: me.fields,
            data: []
        });

        me.addButton = Ext.create("Ext.button.Button", {
            text: __("Add"),
            glyph: NOC.glyph.plus,
            scope: me,
            handler: me.onAddRecord
        });

        me.deleteButton = Ext.create("Ext.button.Button", {
            text: __("Delete"),
            glyph: NOC.glyph.minus,
            disabled: true,
            scope: me,
            handler: me.onDeleteRecord
        });

        me.cloneButton = Ext.create("Ext.button.Button", {
            text: __("Clone"),
            glyph: NOC.glyph.copy,
            disabled: true,
            scope: me,
            handler: me.onCloneRecord
        });

        // Build toolbar
        toolbar = [
            me.addButton,
            me.deleteButton,
            "-",
            me.cloneButton
        ];
        if(me.toolbar) {
            toolbar.push("-");
            toolbar = toolbar.concat(me.toolbar);
        }

        me.grid = Ext.create("Ext.grid.Panel", {
            layout: "fit",
            store: me.store,
            columns: me.columns,
            plugins: [
                Ext.create("Ext.grid.plugin.CellEditing", {
                    clicksToEdit: 2,
                    listeners: {
                        scope: me,
                        edit: me.onCellEdit
                    }
                })
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: toolbar
                }
            ],
            listeners: {
                scope: me,
                select: me.onSelect
            },
            viewConfig: {
                plugins: {
                    ptype: "gridviewdragdrop",
                    dragtext: __("Drag and drop to reorganize")
                }
            }
        });

        Ext.apply(me, {
            items: [
                me.grid
            ]
        });
        me.currentSelection = undefined;
        me.callParent();
    },

    getValue: function() {
        var me = this,
            records = [];
        me.store.each(function(r) {
            var d = {};
            Ext.each(me.fields, function(f) {
                d[f] = r.get(f);
            });
            records.push(d);
        });
        return records;
    },

    setValue: function(v) {
        var me = this;
        if(v === undefined || v === "") {
            v = [];
        } else {
            v = v || [];
        }
        me.store.loadData(v);
        return me.mixins.field.setValue.call(me, v);
    },
    //
    onSelect: function(grid, record, index) {
        var me = this;
        me.currentSelection = index;
        me.deleteButton.setDisabled(false);
        me.cloneButton.setDisabled(false);
    },
    //
    onAddRecord: function() {
        var me = this,
            rowEditing = me.grid.plugins[0];
        rowEditing.cancelEdit();
        me.grid.store.insert(0, {});
        rowEditing.startEdit(0, 0);
    },
    //
    onDeleteRecord: function() {
        var me = this,
            sm = me.grid.getSelectionModel(),
            rowEditing = me.grid.plugins[0];
        rowEditing.cancelEdit();
        me.grid.store.remove(sm.getSelection());
        if(me.grid.store.getCount() > 0) {
            sm.select(0);
        } else {
            me.deleteButton.setDisabled(true);
            me.cloneButton.setDisabled(true);
        }
    },
    //
    onCloneRecord: function() {
        var me = this,
            sm = me.grid.getSelectionModel(),
            sel = sm.getLastSelected(),
            rowEditing = me.grid.plugins[0],
            newRecord;
        if(!sel) {
            return;
        }
        rowEditing.cancelEdit();
        newRecord = sel.copy();
        delete newRecord.data.id;
        newRecord = me.store.createModel(newRecord.data);
        me.fireEvent("clone", newRecord);
        me.currentSelection += 1;
        me.grid.store.insert(me.currentSelection, newRecord);
        sm.select(me.currentSelection);
    },
    //
    onCellEdit: function(editor, e) {
        var me = this,
            ed = e.grid.columns[e.colIdx].getEditor();
        if(ed.rawValue) {
            e.record.set(e.field + "__label", ed.rawValue);
        }
    }
});
