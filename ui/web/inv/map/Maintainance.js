//---------------------------------------------------------------------
// Network Map Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.log('Defining NOC.inv.map.Maintainance');

Ext.define('NOC.inv.map.Maintainance', {
    extend: 'NOC.core.Application',
    layout: 'fit',
    defaultListenerScope: true,

    requires: [
        'Ext.grid.Panel',
        'Ext.ux.form.SearchField',

        "NOC.maintainance.maintainance.Model",
        "NOC.maintainance.maintainancetype.LookupField",
        "NOC.sa.managedobject.LookupField",
        "NOC.inv.networksegment.LookupField"
    ],

    model: 'NOC.maintainance.maintainance.Model',

    initComponent: function() {
        var me = this;

        me.rest_url = Ext.create(me.model).rest_url;
        me.store = Ext.create('Ext.data.Store', {
            model: me.model,
            data: []
        });
        me.dockMaintainance = Ext.create('Ext.form.Panel', {
            dock: 'top',
            bodyPadding: 10,
            items: [
                {
                    xtype: 'container',
                    style: {
                        'font-size': '15px',
                        'padding-bottom': '10'
                    },
                    html: me.makeLabel(me.noc.args[0].mode, me.noc.args[1].object__label)
                },
                {
                    xtype: 'searchfield',
                    itemId: 'filterField',
                    fieldLabel: __('Filter'),
                    labelWidth: 50,
                    width: '100%',
                    listeners: {
                        specialkey: 'setFilter'
                    }
                },
                {
                    xtype: 'checkboxfield',
                    itemId: 'isCompleted',
                    boxLabel: __('Only not Completed'),
                    name: 'onlyNotCompleted',
                    checked: true,
                    listeners: {
                        change: 'loadData'
                    }
                },
                {
                    xtype: 'component',
                    itemId: 'status',
                    tpl: __('Matching row:') + ' {count}',
                    style: 'margin-right:5px'
                }
            ]
        });
        me.gridMaintainance = Ext.create('Ext.grid.Panel', {
            bodyPadding: 5,
            // width: 350,
            store: me.store,
            selModel: {
                mode: 'SINGLE',
                selType: 'checkboxmodel',
                showHeaderCheckbox: false
            },
            viewConfig: {
                emptyText: __('No matching')
            },
            listeners: {
                scope: me,
                rowdblclick: me.addToMaintainance
            },
            columns: [
                {
                    text: __('Type'),
                    dataIndex: 'type',
                    width: 150,
                    renderer: NOC.render.Lookup('type')
                },
                {
                    text: __('Start'),
                    dataIndex: 'start',
                    width: 120
                },
                {
                    text: __('Stop'),
                    dataIndex: 'stop',
                    width: 120
                },
                {
                    text: __('Subject'),
                    dataIndex: 'subject',
                    flex: 1
                }
            ]
        });
        me.buttons = [{
            scope: me,
            handler: me.addToMaintainance,
            text: __('Add ') + me.noc.args[0].mode
        }];
        Ext.apply(me, {
            buttonAlign: 'center',
            dockedItems: me.dockMaintainance,
            items: me.gridMaintainance,
            buttons: me.buttons
        });
        me.loadData();
        this.callParent(arguments);
    },

    addToMaintainance: function() {
        var me = this,
            selected = me.gridMaintainance.getSelection();

        if(selected.length === 0) {
            NOC.error(__('Your must select maintainance!'));
            return;
        }
        if('Object' === me.noc.args[0].mode) {
            selected[0].data.direct_objects.push({
                object__label: me.noc.args[1].object__label,
                object: me.noc.args[1].object
            });
        } else if('Segment' === me.noc.args[0].mode) {
            selected[0].data.direct_segments.push({
                segment__label: me.noc.args[1].object__label,
                segment: me.noc.args[1].object
            });
        } else {
            NOC.error(__('Unknows mode :') + me.noc.args[0].mode);
            return;
        }

        Ext.Ajax.request({
            url: me.rest_url + selected[0].data.id,
            method: 'PUT',
            jsonData: Ext.JSON.encode(selected[0].data),
            success: function(response) {
                NOC.msg.complete(__('Saved'));
                Ext.ComponentQuery.query('[xtype=viewport]')[0].workplacePanel.activeTab.close();
            },
            failure: function() {
                NOC.error(__('Failed to load data'));
            }
        });
    },

    loadData: function() {
        var me = this,
            filter = function(element) {
                if(this.filter.length === 0 && this.isCompleted) {
                    return !element.is_completed;
                }
                if(this.filter.length === 0 && !this.isCompleted) {
                    return true;
                }
                if(this.filter.length > 0 && this.isCompleted && element.subject.indexOf(this.filter) > -1) {
                    return !element.is_completed;
                }
                return this.filter.length > 0 && !this.isCompleted && element.subject.indexOf(this.filter) > -1;

            };
        var filterValue = me.dockMaintainance.down('#filterField') ? me.dockMaintainance.down('#filterField').getValue() : '',
            isCompletedValue = me.dockMaintainance.down('#isCompleted') ? me.dockMaintainance.down('#isCompleted').getValue() : true;
        var params = {};

        if(filterValue.length > 0) {
            params = Ext.apply(params, {query: filterValue});
        }
        if(isCompletedValue) {
            params = Ext.apply(params, {completed: 1})
        }

        Ext.Ajax.request({
            url: me.rest_url,
            method: "GET",
            // params: params,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                var filtred = data.filter(filter, {
                    filter: filterValue,
                    isCompleted: isCompletedValue
                });
                me.store.loadData(filtred);
                me.dockMaintainance.down('#status').update({count: filtred.length});
            },
            failure: function() {
                NOC.msg.failed(__("Failed to load data"))
            }
        });
    },

    setFilter: function(field, e) {
        var me = this;
        if(Ext.EventObject.ENTER === e.getKey()) {
            me.loadData();
        }
    },

    makeLabel: function(name, value) {
        return __("Add ") + "<b>" + name + "</b> '" + value + __("' to maintainance");
    }
});