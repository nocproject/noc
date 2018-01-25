//---------------------------------------------------------------------
// Network Map Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.log('Defining NOC.inv.map.Maintenance');

Ext.define('NOC.inv.map.Maintenance', {
    extend: 'NOC.core.Application',
    layout: 'fit',
    defaultListenerScope: true,

    requires: [
        'Ext.grid.Panel',
        'Ext.ux.form.SearchField',

        "NOC.maintenance.maintenance.Model",
        "NOC.maintenance.maintenancetype.LookupField",
        "NOC.sa.managedobject.LookupField",
        "NOC.inv.networksegment.LookupField"
    ],

    model: 'NOC.maintenance.maintenance.Model',

    initComponent: function() {
        var me = this;

        me.rest_url = Ext.create(me.model).rest_url;
        me.store = Ext.create('Ext.data.Store', {
            model: me.model,
            data: []
        });
        me.modeLabel = me.noc.args[1].length > 1 ? me.noc.args[0].mode + 's' : me.noc.args[0].mode;
        me.dockMaintenance = Ext.create('Ext.form.Panel', {
            dock: 'top',
            bodyPadding: 10,
            items: [
                {
                    xtype: 'container',
                    scrollable: 'vertical',
                    style: {
                        'font-size': '15px',
                        'padding-bottom': '10'
                    },
                    tpl: [
                        '<div style="padding-bottom: 5px">' + __("Add") + '&nbsp;<b>{mode}:</b><br/>' + '</div>',
                        '<tpl for="elements">',
                        '<div style="padding-left: 20px">{object__label}</div>',
                        '</tpl>',
                        '<div style="padding-top: 5px">' + __("to maintenance") + '</div>'
                    ],
                    data: {mode: me.modeLabel, elements: me.noc.args[1]}
                },
                {
                    xtype: 'searchfield',
                    itemId: 'filterField',
                    fieldLabel: __('Filter'),
                    labelWidth: 50,
                    width: '100%',
                    triggers: {
                        clear: {
                            cls: 'x-form-clear-trigger',
                            scope: me,
                            handler: 'cleanFilter'
                        }
                    },
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
        me.gridMaintenance = Ext.create('Ext.grid.Panel', {
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
                rowdblclick: me.addToMaintenance
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
            handler: me.addToMaintenance,
            text: __('Add ') + me.modeLabel
        }];
        Ext.apply(me, {
            buttonAlign: 'center',
            dockedItems: me.dockMaintenance,
            items: me.gridMaintenance,
            buttons: me.buttons
        });
        me.loadData();
        this.callParent(arguments);
    },

    addToMaintenance: function() {
        var me = this,
            selected = me.gridMaintenance.getSelection();

        if(selected.length === 0) {
            NOC.error(__('Your must select maintenance!'));
            return;
        }
        if('Object' === me.noc.args[0].mode) {
            selected[0].data.direct_objects = selected[0].data.direct_objects.concat(me.noc.args[1]);
        } else if('Segment' === me.noc.args[0].mode) {
            selected[0].data.direct_segments = selected[0].data.direct_segments.concat(me.noc.args[1]);
        } else {
            NOC.error(__('Unknows mode :') + me.noc.args[0].mode);
            return;
        }

        selected[0].data.direct_objects = selected[0].data.direct_objects.map(function(o) {
            return {object: o.object};
        });

        selected[0].data.affected_objects = selected[0].data.affected_objects.map(function(o) {
            return {object: o.object};
        });
        Ext.Ajax.request({
            url: me.rest_url + selected[0].data.id + "/",
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
            filterValue = me.dockMaintenance.down('#filterField') ? me.dockMaintenance.down('#filterField').getValue() : '',
            isCompletedValue = me.dockMaintenance.down('#isCompleted') ? me.dockMaintenance.down('#isCompleted').getValue() : true;

        var params = {};
        if(filterValue.length > 0) {
            params = Ext.apply(params, {__query: filterValue});
        }
        if(isCompletedValue) {
            params = Ext.apply(params, {is_completed: 1})
        }

        Ext.Ajax.request({
            url: me.rest_url,
            method: "GET",
            params: params,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                me.store.loadData(data);
                me.dockMaintenance.down('#status').update({count: data.length});
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

    cleanFilter: function(field) {
        var me = this;
        field.setValue('');
        me.loadData();
    }
});