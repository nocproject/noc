//---------------------------------------------------------------------
// NOC.core.TreeField
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.core.TreeField');

Ext.define('NOC.core.TreeField', {
    extend: 'Ext.form.field.Text',

    requires: [
        'Ext.window.Window',
        'NOC.core.TreeModel',
        'NOC.core.TreePanel'
    ],

    alias: 'widget.nocTreeField',

    triggers: {
        openSelectWindow: {
            cls: 'x-form-arrow-trigger',
            handler: function() {
                this.selectWindow.showAt(this.getXY());
                this.selectWindow.setWidth(this.getWidth());
            }
        }
    },

    config: {
        fieldValue: null,
        idIsNumber: false
    },

    initComponent: function() {
        var me = this;

        this.reader = Ext.create('Ext.data.reader.Json', {
            rootProperty: 'data',
            totalProperty: 'total',
            successProperty: 'success'
        });

        this.pathStore = Ext.create('Ext.data.Store', {
            model: 'NOC.core.TreeModel',
            proxy: {
                type: 'memory',
                reader: this.reader
            }
        });

        this.proxy = Ext.create('Ext.data.proxy.Rest', {
            url: this.restUrl + '/lookup',
            pageParam: '__page',
            startParam: '__start',
            limitParam: '__limit',
            extraParams: {
                parent: '',
                __format: 'ext'
            },
            reader: this.reader
        });

        this.listStore = Ext.create('Ext.data.Store', {
            autoLoad: true,
            remoteFilter: true,
            model: 'NOC.core.TreeModel',
            pageSize: 500,
            proxy: this.proxy
        });

        this.historyStore = Ext.create('Ext.data.Store', {
            storeId: 'history',
            model: 'NOC.core.TreeModel',
            sorters: 'level',
            data: [{
                label: __('Root'),
                id: '_root_',
                level: 0
            }]
        });

        this.restoreStore = Ext.create('Ext.data.Store', {
            autoLoad: false,
            model: 'NOC.core.TreeModel',
            proxy: this.proxy
        });

        this.panel = Ext.create('NOC.core.TreePanel', {
            restUrl: this.restUrl,
            listStore: this.listStore,
            historyStore: this.historyStore,
            pathStore: this.pathStore,
            closeSelectWindow: function() {
                me.selectWindow.hide();
            },
            action: function(node) {
                me.setFieldValue(node);
                me.setValue(node.label);
                if(me.action !== undefined) {
                    me.action(node.id);
                }
                me.selectWindow.hide();
            },
            fieldValue: function(value) {
                if(value === undefined) {
                    return me.getFieldValue();
                } else {
                    me.setFieldValue(value);
                }
            }
        });

        this.selectWindow = Ext.create("Ext.window.Window", {
            header: false,
            border: false,
            resizable: false,
            scrollable: true,
            modal: true,
            alwaysOnTop: true,
            closeAction: 'hide',
            activeItem: 'filter',
            padding: 0,
            maxHeight: 600,
            items: me.panel
        });

        this.on('change', function() {
            me.fireEvent('select');
        });

        this.on('destroy', function() {
            // ToDo ext-all.js:22 Uncaught TypeError: Cannot read property 'addCls' of null, press x on tab on open window panel
            console.log('destroy TreeField');
            this.selectWindow.destroy();
        });

        this.callParent();
    },

    restoreById: function(id) {
        var me = this;
        this.restoreStore.load({
            url: this.restUrl + '/' + id + '/get_path',
            callback: function(records) {
                me.setFieldValue(records.pop());
                me.setValue(me.getFieldValue().data.label);
                if(records.length === 0) {
                    me.panel.selectListRow();
                    return;
                }
                if(records.length > 0) {
                    me.historyStore.loadData(records, true);
                    me.pathStore.loadData(records, true);
                    me.panel.byIdQuery(records[records.length - 1].id);
                }
            }
        });
    },

    reset: function() {
        this.setValue('');
        this.setFieldValue(null);
        this.pathStore.removeAll();
        this.historyStore.removeAll();
        this.historyStore.loadRawData({
            label: __('Root'),
            id: '_root_',
            level: 0
        });
        this.panel.byIdQuery('_root_');
    },

    getValue: function() {
        if(this.fieldValue != null) {
            return this.fieldValue.id;
        }
        return null;
    }
});