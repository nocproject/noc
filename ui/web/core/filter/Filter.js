//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.core.filter.Filter');
Ext.define('NOC.core.filter.Filter', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.NOC.Filter',

    requires: [
        'Ext.ux.form.SearchField',
        'NOC.sa.profile.LookupField',
        'NOC.main.pool.LookupField',
        'NOC.sa.vendor.LookupField',
        'NOC.sa.platform.LookupField',
        'NOC.sa.administrativedomain.TreeCombo',
        'NOC.inv.networksegment.TreeCombo',
        'NOC.inv.firmware.LookupField',
        'NOC.inv.platform.LookupField',
        'NOC.inv.vendor.LookupField',
        'NOC.sa.managedobjectprofile.LookupField',
        'NOC.sa.managedobjectselector.LookupField',
        'NOC.sa.commandsnippet.LookupField',
        'NOC.sa.actioncommands.LookupField',
        'NOC.core.filter.ViewModel',
        'NOC.core.filter.FilterController'
    ],
    controller: 'core.filter',
    viewModel: 'core.filter',
    scrollable: 'y',
    minWidth: 300,
    title: __('Filter'),
    itemId: 'filterPanel',
    layout: {
        type: 'vbox',
        align: 'right'
    },
    defaults: {
        labelAlign: 'top',
        minWidth: 270,
        width: '100%',
        margin: '5 10 0 18',
        uiStyle: undefined
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
                    handler: 'cleanFilter'
                }
            },
            listeners: {
                specialkey: 'setFilter'
            }
        },
        {
            xtype: 'sa.profile.LookupField',
            itemId: 'profile_name', // name of http request query param
            fieldLabel: __('By SA Profile:'),
            listeners: {
                change: 'setFilter'
            }
        },
        {
            xtype: 'sa.managedobjectprofile.LookupField',
            itemId: 'object_profile', // name of http request query param
            fieldLabel: __('By Obj. Profile:'),
            listeners: {
                change: 'setFilter'
            }
        },
        {
            xtype: 'sa.administrativedomain.TreeCombo',
            isLookupField: true,
            itemId: 'administrative_domain', // name of http request query param
            fieldLabel: __('By Adm. Domain:'),
            listeners: {
                clear: 'setFilter',
                select: 'setFilter'
            }
        },
        {
            xtype: 'inv.networksegment.TreeCombo',
            isLookupField: true,
            itemId: 'segment', // name of http request query param
            fieldLabel: __('By Segment:'),
            listeners: {
                clear: 'setFilter',
                select: 'setFilter'
            }
        },
        {
            xtype: 'sa.managedobjectselector.LookupField',
            itemId: 'selector', // name of http request query param
            fieldLabel: __('By Selector:'),
            listeners: {
                change: 'setFilter'
            }
        },
        {
            xtype: 'main.pool.LookupField',
            itemId: 'pool', // name of http request query param
            fieldLabel: __('By Pool:'),
            listeners: {
                change: 'setFilter'
            }
        },
        {
            xtype: 'inv.vendor.LookupField',
            itemId: 'vendor',  // name of http request query param
            fieldLabel: __('By Vendor:'),
            listeners: {
                change: 'setFilter'
            }
        },
        {
            xtype: 'inv.platform.LookupField',
            itemId: 'platform',  // name of http request query param
            fieldLabel: __('By Platform:'),
            listeners: {
                change: 'setFilter'
            }
        },
        {
            xtype: 'inv.firmware.LookupField',
            itemId: 'version',  // name of http request query param
            fieldLabel: __('By Version:'),
            listeners: {
                change: 'setFilter'
            }
        },
        {
            xtype: 'textarea',
            itemId: 'addresses',
            fieldLabel: __('By IP list (max. 2000):'),
            listeners: {
                change: 'setFilter'
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
                        labelAlign: 'top'
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
                            fieldLabel: __('Value'),
                            xtype: 'fieldcontainer',
                            layout: 'vbox',
                            defaultType: 'checkbox',
                            bind: {
                                visible: '{isLeaf}'
                            },
                            defaults: {
                                margin: '0 0 0 10'
                            },

                            items: [{
                                boxLabel: __('Exclude'),
                                itemId: 'exclude',
                                bind: '{capabilitiesTree.selection.typeExclude}'
                            }, {
                                boxLabel: __('Include'),
                                itemId: 'include',
                                bind: '{capabilitiesTree.selection.typeInclude}'
                            }]
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
                                    {'abbr': '>', 'name': '=>'},
                                    {'abbr': '<', 'name': '=<'},
                                    {'abbr': '==', 'name': '=='}
                                ]
                            },
                            bind: {
                                value: '{capabilitiesTree.selection.condition}',
                                visible: '{isTypeIncludeCondition}'
                            }
                        },
                        {
                            xtype: 'textfield',
                            itemId: 'capValue',
                            fieldLabel: __('Value'),
                            bind: {
                                value: '{capabilitiesTree.selection.value}',
                                visible: '{isTypeInclude}'
                            }
                        },
                        {
                            xtype: 'checkbox',
                            itemId: 'capValueBool',
                            boxLabel: __('Yes/No'),
                            bind: {
                                value: '{capabilitiesTree.selection.value}',
                                visible: '{isTypeIncludeBool}'
                            }
                        },
                        {
                            xtype: 'checkbox',
                            itemId: 'capChecked',
                            boxLabel: __('Checked'),
                            bind: {
                                value: '{capabilitiesTree.selection.checked}',
                                visible: '{isLeaf}'
                            }
                        }
                    ]
                }
            ],
            tbar: [
                {
                    text: __('Clear'),
                    handler: 'onCapabilitiesClear'
                }, {
                    text: __('Apply'),
                    handler: 'onCapabilitiesApply'
                }
            ]
        },
        {
            xtype: 'button',
            itemId: 'clean-btn',
            minWidth: 50,
            text: __('Clean All'),
            handler: 'cleanAllFilters'
        }
    ]
});
