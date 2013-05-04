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

        Ext.apply(me, {
            items: [
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
                me.paramsGrid
            ]
        });
        me.callParent();
        me.nameField = me.getComponent("name");
        me.handlerField = me.getComponent("handler");
    },
    //
    showNode: function(cell) {
        var me = this,
            data = cell.wfdata;
        me.nameField.setValue(data.name);
        me.handlerField.setValue(data.handler);
        me.paramsGrid.setSource(data.params);
    },
    //
    setHandlers: function(handlers) {
        var me = this,
            hdata = [];
        for(var v in me.editor.handlers) {
            hdata.push({id: v, label: v});
        }
        me.handlersStore.loadRawData(hdata);
    }
});
