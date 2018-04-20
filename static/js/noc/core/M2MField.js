//---------------------------------------------------------------------
// NOC.core.M2MField -
// Lookup Many-To-Many form field
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.M2MField");

Ext.define("NOC.core.M2MField", {
    extend: "Ext.form.FieldContainer",
    mixins: {
        field: 'Ext.form.field.Field'
    },

    initComponent: function() {
        var me = this,
            eclass, toolbar;

        me.store = Ext.create("Ext.data.Store", {
            fields: ["id", {name: "label", persist: false}],
            idField: "id",
            data: []
        });

        me.addButton = Ext.create("Ext.button.Button", {
            text: "Add",
            glyph: NOC.glyph.plus,
            scope: me,
            handler: me.onAddRecord
        });

        me.deleteButton = Ext.create("Ext.button.Button", {
            text: "Delete",
            glyph: NOC.glyph.minus,
            disabled: true,
            scope: me,
            handler: me.onDeleteRecord
        });

        toolbar = [me.addButton, me.deleteButton];
        eclass = me.$className.replace("M2MField", "LookupField");
        Ext.require(eclass);
        me.grid = Ext.create("Ext.grid.Panel", {
            layout: "fit",
            store: me.store,
            header: false,
            columns: [{
                name: "id",
                flex: 1,
                renderer: function(value, meta, record) {
                    return record.get("label");
                },
                editor: eclass.substr(4)  // Strip NOC.
            }],
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
            records.push(r.get("id"));
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
        }
    },
    //
    onCellEdit: function(editor, e) {
        var me = this,
            ge = e.grid.columns[e.colIdx].getEditor();
        if(ge.rawValue) {
            e.record.set("id", ge.getValue());
            e.record.set("label", ge.getRawValue());
        } else {
            me.store.remove(e.record);
        }
    }
});
