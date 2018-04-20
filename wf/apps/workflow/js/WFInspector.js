//---------------------------------------------------------------------
// Workflow inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.WFInspector");

Ext.define("NOC.wf.workflow.WFInspector", {
    extend: "Ext.Panel",
    width: 300,
    padding: 4,
    baseCls  : Ext.baseCSSPrefix + "toolbar",
    editor: undefined,
    currentCell: undefined,
    disabled: true,
    //
    initComponent: function() {
        var me = this;

        // Handlers field
        me.handlersStore = Ext.create("Ext.data.Store", {
            fields: ["id", "label", "icon"],
            data: []
        });

        me.paramsGrid = Ext.create("Ext.grid.property.Grid", {
            width: 288,
            title: "Params",
            source: {
            }
        });

        me.applyButton = Ext.create("Ext.button.Button", {
            text: "Apply",
            tooltip: "Apply changes",
            glyph: NOC.glyph.save,
            disabled: true,
            scope: me,
            handler: me.onApply
        });

        me.resetButton = Ext.create("Ext.button.Button", {
            text: "Reset",
            tooltip: "Reset changes",
            glyph: NOC.glyph.refresh,
            disabled: true,
            scope: me,
            handler: me.onResetChanges
        });

        Ext.apply(me, {
            items: [
                me.applyButton,
                me.resetButton,
                {
                    xtype: "textfield",
                    name: "name",
                    itemId: "name",
                    labelAlign: "top",
                    fieldLabel: "Name",
                    width: 288
                },
                {
                    xtype: "textfield",
                    name: "label",
                    itemId: "label",
                    labelAlign: "top",
                    fieldLabel: "Label",
                    width: 288
                },
                {
                    xtype: "combobox",
                    name: "handler",
                    itemId: "handler",
                    labelAlign: "top",
                    fieldLabel: "Handler",
                    forceSelection: true,
                    width: 288,
                    store: me.handlersStore,
                    queryMode: "local",
                    displayField: "label",
                    valueField: "id",
                    listeners: {
                        scope: me,
                        select: me.onChangeHandler
                    },
                    listConfig: {
                        getInnerTpl: function() {
                            var tpl = "<div>{icon} {label}</div>";
                            return tpl;
                        }
                    }
                },
                {
                    xtype: "textarea",
                    name: "description",
                    itemId: "description",
                    labelAlign: "top",
                    fieldLabel: "Description",
                    width: 288
                },
                me.paramsGrid
            ]
        });
        me.callParent();
        me.nameField = me.getComponent("name");
        me.labelField = me.getComponent("label");
        me.descriptionField = me.getComponent("description");
        me.handlerField = me.getComponent("handler");
    },
    //
    showNode: function(cell) {
        var me = this;
        if(cell) {
            var data = cell.wfdata;
            me.currentCell = cell;
            me.setDisabled(false);
            me.nameField.setValue(data.name);
            me.labelField.setValue(data.label);
            me.handlerField.setValue(data.handler);
            me.descriptionField.setValue(data.description);
            me.paramsGrid.setSource(data.params);
            me.applyButton.setDisabled(false);
            me.resetButton.setDisabled(false);
        } else {
            me.currentCell = undefined;
            me.setDisabled(true);
        }
    },
    //
    setHandlers: function(handlers) {
        var me = this,
            hdata = [];
        for(var v in me.editor.handlers) {
            hdata.push({
                id: v,
                label: v,
                icon: me.editor.handlers[v].conditional ? "&diams;" : "&equiv;"
            });
        }
        me.handlersStore.loadRawData(hdata);
    },
    //
    onApply: function() {
        var me = this,
            d,
            handler;
        if(!me.currentCell) {
            return;
        }
        d = me.currentCell.wfdata;
        d.name = me.nameField.getValue();
        d.label = me.labelField.getValue();
        // me.currentCell.setValue(d.name);
        me.editor.graph.model.beginUpdate();
        try {
            me.editor.graph.model.setValue(me.currentCell, d.label);
        } finally {
            me.editor.graph.model.endUpdate();
        }
        handler = me.handlerField.getValue();
        d.description = me.descriptionField.getValue();
        d.handler = handler;
        d.changed = true;
        d.params = me.paramsGrid.getSource();
        d.conditional = me.editor.handlers[handler].conditional;
        me.editor.changeShape(me.currentCell);
        me.editor.registerChange(me.currentCell);
    },
    //
    onChangeHandler: function(combo, records, opts) {
        var me = this,
            handler = records[0].get("id"),
            d = me.currentCell.wfdata,
            cp = me.paramsGrid.getSource(),
            np = {};
        if(d.handler == handler) {
            return;
        }
        // Handler has been changed, replace params
        var hp = me.editor.handlers[handler].params;
        for(var i in hp) {
            var p = hp[i];
            if(cp && cp[p]) {
                np[p] = cp[p];
            } else {
                np[p] = "";
            }
        }
        me.paramsGrid.setSource(np);
        // Change between conditional and unconditional nodes
    },
    //
    onResetChanges: function() {
        var me = this;
        me.showNode(me.currentCell);
    }
});
