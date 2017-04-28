console.debug('Defining NOC.core.Filter');
Ext.define('NOC.core.Filter', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.NOC.Filter',

    requires: [
        'Ext.ux.form.SearchField',
        'NOC.main.ref.profile.LookupField',
        'NOC.main.pool.LookupField',
        'NOC.sa.administrativedomain.TreeCombo',
        'NOC.inv.networksegment.TreeCombo',
        'NOC.sa.managedobjectprofile.LookupField',
        'NOC.sa.managedobjectselector.LookupField',
        'NOC.sa.commandsnippet.LookupField',
        'NOC.sa.actioncommands.LookupField'
    ],

    config: {
        filterObject: {}
    },
    scrollable: 'y',
    minWidth: 300,

    initComponent: function() {
        this.capabilityModel = Ext.create('Ext.data.TreeModel', {
            fields: [
                {
                    name: 'text',
                    type: 'string'
                },
                {
                    name: 'type',
                    type: 'string'
                },
                {
                    name: 'capType',
                    type: 'string',
                    persist: false
                },
                {
                    name: 'id',
                    type: 'string'
                },
                {
                    name: 'condition',
                    type: 'string'
                },
                {
                    name: 'value',
                    defaultValue: false,
                    type: 'string'
                },
                {
                    name: 'checked',
                    defaultValue: false,
                    type: 'boolean'
                }
            ]
        });

        this.viewModel = Ext.create('Ext.app.ViewModel', {
            stores: {
                capabilityStore: {
                    model: this.capabilityModel,
                    xclass: 'Ext.data.TreeStore',
                    autoLoad: true,
                    proxy: {
                        type: 'ajax',
                        url: '/inv/capability/tree',
                        reader: 'json'
                    },
                    sorters: [
                        {
                            property: 'leaf',
                            direction: 'ASC'
                        }, {
                            property: 'text',
                            direction: 'ASC'
                        }
                    ],
                    listeners: {
                        scope: this,
                        load: this.restoreFilter,
                        update: this.changeCaps
                    }
                }
            },
            formulas: {
                currentCap: {
                    bind: {
                        bindTo: '{capabilitiesTree.selection}',
                        deep: true
                    },
                    get: function(capability) {
                        return capability;
                    },
                    set: function(capability) {
                        if(!capability.isModel) {
                            capability = this.get('capabilityStore').getNodeById(capability);
                        }
                        this.set('currentCap', capability);
                    }
                },
                selectedCap: function(get) {
                    var selection = get('capabilitiesTree.selection');

                    Ext.ComponentQuery.query('[itemId=capCondition]')[0].setHidden(true);
                    Ext.ComponentQuery.query('[itemId=capValue]')[0].setHidden(true);
                    Ext.ComponentQuery.query('[itemId=capValueBool]')[0].setHidden(true);
                    Ext.ComponentQuery.query('[itemId=capChecked]')[0].setHidden(true);
                    Ext.ComponentQuery.query('[itemId=capType]')[0].setHidden(true);

                    if(selection && selection.get('leaf')) {
                        var path = selection.getPath('text');
                        var capTypeValue = Ext.ComponentQuery.query('[itemId=capType]')[0].getValue();

                        Ext.ComponentQuery.query('[itemId=capChecked]')[0].setHidden(false);
                        Ext.ComponentQuery.query('[itemId=capType]')[0].setHidden(false);
                        path = path.replace(/^\/Root/, '');

                        if(capTypeValue === 'include') {
                            if('bool' === selection.get('type')) {
                                Ext.ComponentQuery.query('[itemId=capValueBool]')[0].setHidden(false);
                            } else if('int' === selection.get('type')) {
                                Ext.ComponentQuery.query('[itemId=capCondition]')[0].setHidden(false);
                                Ext.ComponentQuery.query('[itemId=capValue]')[0].setHidden(false);
                            } else if('str' === selection.get('type')) {
                                Ext.ComponentQuery.query('[itemId=capValue]')[0].setHidden(false);
                            }
                        }
                        return __('Selected') + ' (' + selection.get('type') + '): ' + path;
                    } else {
                        return __('No leaf selected');
                    }
                },
                capTypeRadioValue: {
                    bind: '{currentCap.capType}',
                    get: function(value) {
                        return {
                            capType: value
                        };
                    },
                    set: function(value) {
                        this.set('currentCap.capType', value.capType);
                    }
                }
            }
        });

        Ext.apply(this, {
            title: __('Filter'),
            itemId: 'filterPanel',
            region: 'east',
            width: 300,
            collapsed: true,
            border: true,
            animCollapse: false,
            collapseMode: 'mini',
            hideCollapseTool: true,
            split: true,
            resizable: true,
            layout: {
                type: 'vbox',
                align: 'right'
            },
            defaults: {
                labelAlign: 'top',
                minWidth: 270,
                width: '100%',
                margin: '5 10 0 18'
            },
            items: [
                {
                    xtype: 'searchfield',
                    isLookupField: true,
                    itemId: '__query',  // name of http request query param
                    fieldLabel: __('Name'),
                    labelWidth: 50,
                    triggers: {
                        clear: {
                            cls: 'x-form-clear-trigger',
                            scope: this,
                            handler: this.cleanFilter
                        }
                    },
                    listeners: {
                        scope: this,
                        specialkey: this.setFilter
                    }
                },
                {
                    xtype: 'main.ref.profile.LookupField',
                    itemId: 'profile_name', // name of http request query param
                    fieldLabel: __('By SA Profile:'),
                    uiStyle: undefined,
                    listeners: {
                        scope: this,
                        change: this.setFilter
                    }
                },
                {
                    xtype: 'sa.managedobjectprofile.LookupField',
                    itemId: 'object_profile', // name of http request query param
                    fieldLabel: __('By Obj. Profile:'),
                    uiStyle: undefined,
                    listeners: {
                        scope: this,
                        change: this.setFilter
                    }
                },
                {
                    xtype: 'sa.administrativedomain.TreeCombo',
                    isLookupField: true,
                    itemId: 'administrative_domain', // name of http request query param
                    fieldLabel: __('By Adm. Domain:'),
                    listeners: {
                        scope: this,
                        clear: this.setFilter,
                        select: this.setFilter
                    }
                },
                {
                    xtype: 'inv.networksegment.TreeCombo',
                    isLookupField: true,
                    itemId: 'segment', // name of http request query param
                    fieldLabel: __('By Segment:'),
                    listeners: {
                        scope: this,
                        clear: this.setFilter,
                        select: this.setFilter
                    }
                },
                {
                    xtype: 'sa.managedobjectselector.LookupField',
                    itemId: 'selector', // name of http request query param
                    fieldLabel: __('By Selector:'),
                    listeners: {
                        scope: this,
                        change: this.setFilter
                    }
                },
                {
                    xtype: 'main.pool.LookupField',
                    itemId: 'pool', // name of http request query param
                    fieldLabel: __('By Pool:'),
                    listeners: {
                        scope: this,
                        change: this.setFilter
                    }
                },
                // {
                //     xtype: '',
                //     itemId: 'tag', // name of http request query param
                //     fieldLabel: __('By Tag:'),
                //     listeners: {
                //         scope: this,
                //         change: this.setFilter
                //     }
                // },
                {
                    xtype: 'textarea',
                    itemId: 'addresses',
                    fieldLabel: __('By IP list (max. 500):'),
                    listeners: {
                        scope: this,
                        change: this.setFilter
                    },
                    bind: {
                        value: '{ips}'
                    }
                },
                {
                    xtype: 'box',
                    html: __('Capability') + ':'
                },
                {
                    xtype: 'panel',
                    isLookupField: true,
                    itemId: 'caps',
                    fieldLabel: __('Capability'),
                    width: '100%',
                    height: 280,
                    layout: 'border',
                    viewModel: this.viewModel,
                    items: [
                        {
                            region: 'west',
                            width: 140,
                            split: true,
                            layout: {
                                type: 'vbox',
                                align: 'stretch'
                            },
                            border: false,
                            scrollable: 'y',
                            items: {
                                xtype: 'treelist',
                                reference: 'capabilitiesTree',
                                bind: {
                                    store: '{capabilityStore}'
                                }
                            }
                        },
                        {
                            region: 'center',
                            bodyPadding: 10,
                            reference: 'capabilityValues',
                            scrollable: 'y',
                            defaults: {
                                width: '100%',
                                labelAlign: 'top',
                                hidden: false
                            },
                            items: [
                                {
                                    xtype: 'box',
                                    hidden: false,
                                    bind: {
                                        html: '{selectedCap}'
                                    }
                                },
                                {
                                    xtype: 'radiogroup',
                                    itemId: 'capType',
                                    fieldLabel: __('Value'),
                                    bind: {
                                        value: '{capTypeRadioValue}'
                                    },
                                    vertical: true,
                                    columns: 1,
                                    defaults: {
                                        xtype: 'radio',
                                        name: 'capType'
                                    },

                                    items: [
                                        {
                                            boxLabel: __('Exclude'),
                                            inputValue: 'exclude'
                                        },
                                        {
                                            boxLabel: __('Include'),
                                            inputValue: 'include'
                                        }
                                    ],
                                    listeners: {
                                        scope: this,
                                        change: this.onChangeCapType
                                    }
                                },
                                {
                                    xtype: 'combo',
                                    fieldLabel: __('Condition'),
                                    itemId: 'capCondition',
                                    displayField: 'name',
                                    valueField: 'abbr',
                                    store: {
                                        fields: ['abbr', 'name'],
                                        data: [
                                            {"abbr": ">", "name": "=>"},
                                            {"abbr": "<", "name": "=<"},
                                            {"abbr": "==", "name": "=="}
                                        ]
                                    },
                                    bind: '{currentCap.condition}'
                                },
                                {
                                    xtype: 'textfield',
                                    itemId: 'capValue',
                                    fieldLabel: __('Value'),
                                    bind: '{currentCap.value}'
                                },
                                {
                                    xtype: 'checkbox',
                                    itemId: 'capValueBool',
                                    boxLabel: __('Yes/No'),
                                    bind: '{currentCap.value}'
                                },
                                {
                                    xtype: 'checkbox',
                                    itemId: 'capChecked',
                                    boxLabel: __('Checked'),
                                    bind: '{currentCap.checked}',
                                    scope: this,
                                    handler: this.onUncheckedCap
                                }
                            ]
                        }
                    ],
                    tbar: [
                        {
                            text: __('Clear'),
                            handler: this.onCapabilitiesClear,
                            scope: this
                        }, {
                            text: __('Apply'),
                            handler: this.onCapabilitiesApply,
                            scope: this
                        }
                    ]
                },
                {
                    xtype: 'button',
                    itemId: 'clean-btn',
                    minWidth: 50,
                    text: __('Clean All'),
                    handler: Ext.bind(this.cleanAllFilters, this)
                }
            ]
        });
        this.callParent();
    },

    lookupFields: function() {
        var items = [];

        Ext.Array.each(this.items.items, function(item) {
            if(item.isLookupField) {
                items.push(item);
            }
        });
        return items;
    },

    restoreFilter: function() {
        var queryStr = Ext.util.History.getToken().split('?')[1];

        if(queryStr) {
            this.filterObject = Ext.Object.fromQueryString(queryStr, true);
            Ext.Array.each(this.lookupFields(), function(item) {
                var keys = Object.keys(this.filterObject);
                var self = this;

                keys.filter(function(e) {
                    return Ext.String.startsWith(e, item.itemId, true);
                }).map(function(e) {
                    if(Ext.String.endsWith(item.xtype, 'TreeCombo', true)) {
                        item.restoreById(self.filterObject[item.itemId]);
                    } else if('caps' === item.itemId) {
                        var delimiter = self.filterObject[e].indexOf(':');
                        var condition;
                        var id, value;
                        var type = 'include';

                        if(delimiter >= 0) {
                            id = self.filterObject[e].substring(0, delimiter);
                            value = self.filterObject[e].substring(delimiter + 1);

                            if(value[0] === '~') {
                                condition = '<';
                                value = value.substring(1);
                            } else if(value[value.length - 1] === '~') {
                                condition = '>';
                                value = value.substring(0, value.length - 1);
                            } else {
                                condition = '==';
                            }
                        } else if(self.filterObject[e][0] === '!') {
                            id = self.filterObject[e].substring(1);
                            type = 'exclude';
                        } else {
                            id = self.filterObject[e];
                            type = undefined;
                        }

                        var exist = self.viewModel.get('capabilityStore').getNodeById(id);

                        if(exist) {
                            exist.set('capType', type);
                            exist.set('condition', condition);
                            exist.set('value', value);
                            exist.set('checked', true);
                        }
                    } else {
                        item.setValue(self.filterObject[item.itemId]);
                    }
                });
            }, this);
            this.selectionStore.setFilterParams(this.filterObject);
            this.expand();
        }
        this.selectionStore.load();
    },

    setFilter: function(field, event) {
        var value = field.getValue();

        if(field.itemId && 'addresses' === field.itemId) {
            value = value.split('\n')
                .filter(function(ip) {
                    return ip.length > 0;
                })
                .map(function(ip) {
                    return ip.trim();
                });

            if(value.length > 500) {
                NOC.msg.failed(__('Too many IP, max 500'));
                return;
            }
        }

        if(Ext.String.endsWith(field.xtype, 'TreeCombo', true)) {
            if(Ext.isFunction(event.get)) { // event -> data
                value = event.get('id');
            }
        }

        if('Ext.event.Event' === Ext.getClassName(event)) {
            if(Ext.EventObject.ENTER === event.getKey()) {
                this.reloadData(field.itemId, value);
            }
            return;
        }

        this.reloadData(field.itemId, value);
    },

    cleanAllFilters: function() {
        Ext.History.add(this.appId);
        this.filterObject = {};
        Ext.Array.each(this.lookupFields(), function(item) {
            if(Ext.String.endsWith(item.xtype, 'TreeCombo', true)) {
                item.reset();
            } else if('caps' === item.itemId) {
                // skip
            } else {
                item.setValue('');
            }
        });
        this.viewModel.set('ips', '');
        this.onCapabilitiesClear();
        this.reload();
    },

    cleanFilter: function(field) {
        var fieldName = field;

        if(Ext.isObject(field) && 'itemId' in field) {
            field.setValue('');
            fieldName = field.itemId;
        }
        this.reloadData(fieldName, '');
    },

    reloadData: function(name, value) {
        if((typeof value === 'string' && value.length > 0)
            || (typeof value === 'number')
            || (value !== null && typeof value === 'object')) {
            if(value === this.filterObject[name]) return;
            this.filterObject[name] = value;
        } else {
            if(this.filterObject.hasOwnProperty(name)) {
                delete this.filterObject[name];
            } else return;
        }

        var queryObject = Ext.clone(this.filterObject);
        if(queryObject.hasOwnProperty('addresses')) {
            delete queryObject['addresses'];
        }

        var token = '', query = Ext.Object.toQueryString(queryObject, true);

        if(query.length > 0) {
            token = '?' + query;
        }

        Ext.History.add(this.appId + token, true);
        this.reload();
    },

    reload: function() {
        this.selectionStore.setFilterParams(this.filterObject);
        this.selectionStore.load();
    },

    updateCapsFromUrl: function(params) {
        var queryObject = this.filterObject;
        var token = '';
        var keys = Object.keys(queryObject);

        keys.map(function(element) {
            if(Ext.String.startsWith(element, 'caps')) {
                delete this.filterObject[element];
            }
        }, this);

        var query = Ext.Object.toQueryString(
            Ext.Object.merge(queryObject, params),
            true);

        if(query.length > 0) {
            token = '?' + query;
        }

        Ext.History.add(this.appId + token, true);
        this.reload();
    },

    onCapabilitiesApply: function() {
        var index = 0;
        var params = {};

        this.viewModel.get('capabilityStore').root.cascadeBy(function(element) {
            if(element.get('leaf') && element.get('checked')) {
                var type = element.get('type');
                var condition = element.get('condition');
                var value;

                if(element.get('capType') === 'include') {
                    if('str' === type) {
                        value = element.get('id') + ':' + element.get('value');
                    } else if('int' === type) {
                        if('<' === condition) {
                            value = element.get('id') + ':~' + element.get('value');
                        } else if('>' === condition) {
                            value = element.get('id') + ':' + element.get('value') + '~';
                        } else {
                            value = element.get('id') + ':' + element.get('value');
                        }
                    } else if('bool' === type) {
                        // value = element.get('id') + (element.get('value') ? ':' + element.get('value') : '');
                        value = element.get('id') + ':' + (element.get('value') === true ? 'true' : 'false');
                    }
                } else if(element.get('capType') === 'exclude') {
                    value = '!' + element.get('id')
                } else {
                    value = element.get('id');
                }
                params['caps' + index] = value;
                index++;
            }
        }, this);
        this.updateCapsFromUrl(params);
    },

    onCapabilitiesClear: function() {
        this.viewModel.get('capabilityStore').root.cascadeBy(function(element) {
            if(element.get('leaf')) {
                element.set('checked', false, {silent: true});
            }
        });
        Ext.ComponentQuery.query('[itemId=capChecked]')[0].setValue(false);
        this.updateCapsFromUrl({});
    },

    changeCaps: function(self, record, operation, modifiedFieldNames) {
        if(modifiedFieldNames.indexOf('checked') !== -1) {
            // if(!record.get('checked')) {
            //     record.set('capType', null);
            // }
        } else if(modifiedFieldNames.indexOf('capType') !== -1) {
            record.set('checked', true);
        }
    },

    onUncheckedCap: function(self, value) {
        if(!value) {
            this.hideAllCaps();
            Ext.ComponentQuery.query('[itemId=capType]')[0].reset();
        }
    },

    viewCapValue: function(type, value) {
        if('bool' === type) {
            Ext.ComponentQuery.query('[itemId=capValueBool]')[0].setHidden(value);
        } else if('int' === type) {
            Ext.ComponentQuery.query('[itemId=capCondition]')[0].setHidden(value);
            Ext.ComponentQuery.query('[itemId=capValue]')[0].setHidden(value);
        } else if('str' === type) {
            Ext.ComponentQuery.query('[itemId=capValue]')[0].setHidden(value);
        }
    },

    hideAllCaps: function() {
        Ext.ComponentQuery.query('[itemId=capCondition]')[0].setHidden(true);
        Ext.ComponentQuery.query('[itemId=capValue]')[0].setHidden(true);
        Ext.ComponentQuery.query('[itemId=capValueBool]')[0].setHidden(true);
    },

    onChangeCapType: function(self, newVal, oldVal) {
        if(newVal.capType === 'include') {
            this.viewCapValue(this.getViewModel().get('currentCap').get('type'), false);
        }
    }
});