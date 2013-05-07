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
    //
    initComponent: function() {
        var me = this;

        // Handlers field
        me.handlersStore = Ext.create("Ext.data.Store", {
            fields: ["id", "label"],
            data: []
        });

        me.paramsGrid = Ext.create("Ext.grid.property.Grid", {
            width: 288,
            title: "Params",
            source: {
            }
        });

        me.applyButton = Ext.create("Ext.button.Button", {
            iconCls: "icon_disk",
            text: "Apply",
            tooltip: "Apply changes",
            disabled: true,
            scope: me,
            handler: me.onApply
        });

        Ext.apply(me, {
            items: [
                me.applyButton,
                {
                    xtype: "textfield",
                    name: "name",
                    itemId: "name",
                    labelAlign: "top",
                    fieldLabel: "Name",
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
                    valueField: "id"
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
        me.descriptionField = me.getComponent("description");
        me.handlerField = me.getComponent("handler");
    },
    //
    showNode: function(cell) {
        var me = this,
            data = cell.wfdata;
        me.currentCell = cell;
        me.nameField.setValue(data.name);
        me.handlerField.setValue(data.handler);
        me.descriptionField.setValue(data.description);
        me.paramsGrid.setSource(data.params);
        me.applyButton.setDisabled(false);
    },
    //
    setHandlers: function(handlers) {
        var me = this,
            hdata = [];
        for(var v in me.editor.handlers) {
            hdata.push({id: v, label: v});
        }
        me.handlersStore.loadRawData(hdata);
    },
    //
    onApply: function() {
        var me = this,
            d = me.currentCell.wfdata;
        d.name = me.nameField.getValue();
        me.currentCell.setValue(d.name);
        d.description = me.descriptionField.getValue();
        d.handler = me.handlerField.getValue();
        d.changed = true;
        d.params = me.paramsGrid.getSource();
        me.editor.registerChange(me.currentCell);
    }
});
