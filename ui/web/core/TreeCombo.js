//---------------------------------------------------------------------
// NOC.core.TreeCombo
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.core.TreeCombo');

Ext.define('NOC.core.TreeCombo', {
    extend: 'Ext.panel.Panel',

    requires: [
        'Ext.window.Window',
        'Ext.form.field.ComboBox',
        'NOC.core.TreeModel',
        'NOC.core.TreePanel'
    ],

    alias: 'widget.nocTreeCombo',

    isLookupField: true,
    listAlign: 'right',
    listWidth: 2,

    layout: {
        type: 'hbox',
        align: 'bottom'
    },
    border: false,

    config: {
        fieldValue: null, // type model
        idIsNumber: false
    },

    rootNode: {
        label: __('Root'),
        id: '_root_',
        level: 0
    },

    initComponent: function() {
        var me = this,
            path;

        // Calculate restUrl
        path = me.$className.split(".");
        if(!me.restUrl && path[0] === 'NOC' && path[3] === 'TreeCombo') {
            me.restUrl = '/' + path[1] + '/' + path[2]
        }

        if(!me.restUrl) {
            throw "Cannot determine restUrl for " + me.$className;
        }

        this.actionAlways = this.actionAlways || true;

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
            url: this.restUrl + '/lookup/',
            pageParam: '__page',
            startParam: '__start',
            limitParam: '__limit',
            sortParam: '__sort',
            extraParams: {
                __format: 'ext'
            },
            reader: this.reader
        });

        this.comboStore = Ext.create("Ext.data.Store", {
            model: 'NOC.core.TreeModel',
            autoLoad: false,
            remoteSort: true,
            sorters: [
                {
                    property: 'name'
                }
            ],
            proxy: this.proxy
        });

        this.listStore = Ext.create('Ext.data.Store', {
            autoLoad: false,
            remoteFilter: true,
            model: 'NOC.core.TreeModel',
            pageSize: 500,
            remoteSort: true,
            sorters: [
                {
                    property: 'name'
                }
            ],
            proxy: this.proxy
        });

        this.historyStore = Ext.create('Ext.data.Store', {
            storeId: 'history',
            model: 'NOC.core.TreeModel',
            sorters: 'level',
            data: [me.rootNode]
        });

        this.restoreStore = Ext.create('Ext.data.Store', {
            autoLoad: false,
            model: 'NOC.core.TreeModel',
            proxy: this.proxy
        });

        this.autocomplete = Ext.create('Ext.form.field.ComboBox', {
            fieldLabel: this.fieldLabel,
            itemId: this.itemId,
            xtype: this.xtype,
            name: this.name,
            isLookupField: this.isLookupField,
            labelWidth: this.labelWidth,
            labelAlign: this.labelAlign || "top",
            forceSelection: false,
            typeAhead: true,
            displayField: 'label',
            valueField: 'id',
            queryMode: 'remote',
            queryParam: '__query',
            queryCaching: false,
            queryDelay: 200,
            minChars: 2,
            pageSize: 0,
            store: this.comboStore,
            hideTrigger: true,
            flex: 1,
            listConfig: {
                minWidth: 240,
                maxHeight: 450
            }
        });

        this.panel = Ext.create('NOC.core.TreePanel', {
            restUrl: this.restUrl,
            listStore: this.listStore,
            historyStore: this.historyStore,
            pathStore: this.pathStore,
            actionAlways: this.actionAlways,
            closeSelectWindow: function() {
                me.selectWindow.hide();
            },
            action: function(node, hasChild) {
                me.selectNode(node);
                if(me.action !== undefined) {
                    me.action(node.id);
                }
                if(!hasChild) {
                    me.selectWindow.hide();
                }
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
            itemId: 'selectWindow',
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

        this.items = [
            this.autocomplete,
            {
                xtype: 'button',
                style: {
                    "background-color": "#fff",
                    "border-color": "#d0d0d0",
                    "border-left": "none"
                },
                text: '<i class="fa fa-folder-open-o" style="color: #919191" aria-hidden="true"></i>',
                handler: function() {
                    var coord = me.getXY();
                    var x_coord = coord[0];

                    if(me.listAlign === 'right') x_coord -= (me.listWidth - 1) * me.getWidth();
                    me.selectWindow.showAt([x_coord, coord[1]]);
                    me.selectWindow.setWidth(me.getWidth() * me.listWidth);
                }
            }
        ];

        this.autocomplete.on('change', function(element, newValue) {
            if(newValue === null) {
                me.reset();
                me.fireEvent('clear', element);
            }
        });

        this.autocomplete.on('select', function(element, record) {
            me.restoreById(record.id);
        });

        this.autocomplete.on("specialkey", function(element, e) {
            switch(e.keyCode) {
                case e.ESC:
                    me.autocomplete.clearValue();
                    me.fireEvent('clear', element);
                    break;
            }
        });

        this.on('destroy', function() {
            // ToDo ext-all.js:22 Uncaught TypeError: Cannot read property 'addCls' of null, press x on tab on open window panel
            console.log('destroy TreeCombo');
            this.selectWindow.destroy();
        });

        this.listStore.load({
            params: {
                parent: ''
            }
        });

        this.callParent();

        this.mon(Ext.getBody(), 'click', function() {
            me.selectWindow.hide();
        }, me, {delegate: '.x-mask'});
    },

    restoreById: function(id, silent) {
        var me = this;

        if(id === '_root_') {
            me.setFieldValue(me.rootNode);
            me.autocomplete.setValue(me.rootNode.label);
            this.fireEvent('select', this.autocomplete, me.rootNode);
            return;
        }
        if(id) {
            this.restoreStore.load({
                url: this.restUrl + '/' + id + '/get_path/',
                callback: function(records) {
                    if(records) {
                        me.selectNode(records.pop(), silent);
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
                }
            });
        }
    },

    selectNode: function(node, silent) {
        this.setFieldValue(node);
        this.comboStore.load({
            params: {__query: node.data.label},
            scope: this,
            callback: function(records) {
                if(records) {
                    this.autocomplete.setValue(node.data.label);
                    if(!silent) {
                        this.fireEvent('select', this.autocomplete, node);
                    }
                }
            }
        });
    },

    getValue: function() {
        if(this.fieldValue) {
            return this.fieldValue.id;
        }
        return null;
    },

    getLookupData: function() {
        return this.getValue();
    },

    getModelData: function() {
        var obj = {};

        obj[this.name] = this.getValue();
        return obj;
    },

    getName: function() {
        return this.name;
    },

    reset: function() {
        this.autocomplete.setValue(null);
        this.setFieldValue(null);
        this.pathStore.removeAll();
        this.historyStore.removeAll();
        this.historyStore.loadRawData(this.rootNode);
        this.panel.byIdQuery('_root_');
    }
});
