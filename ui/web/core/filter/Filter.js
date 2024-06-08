//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.core.filter.Filter');
Ext.define('NOC.core.filter.Filter', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.NOC.Filter',
    controller: 'core.filter',
    viewModel: 'core.filter',
    requires: [
        'Ext.ux.form.SearchField',
        'NOC.core.ComboBox',
        'NOC.core.combotree.ComboTree',
        'NOC.core.label.LabelField',
        'NOC.core.filter.ViewModel',
        'NOC.core.filter.FilterController',
    ],
    initComponent: function() {
        this.defaults = {
            labelAlign: 'top',
            minWidth: this.minWidth - 30,
            width: '100%',
            margin: '5 10 0 18',
            uiStyle: undefined,
            listAlign: this.treeAlign
        };
        this.callParent();
    },
    scrollable: 'y',
    // minWidth: 300,
    title: __('Filter'),
    itemId: 'filterPanel',
    layout: {
        type: 'vbox',
        align: 'right'
    },
    items: [
        // {
        //     xtype: 'searchfield',
        //     isLookupField: true,
        //     itemId: '__query',  // name of http request query param
        //     fieldLabel: __('Name'),
        //     labelWidth: 50,
        //     triggers: {
        //         clear: {
        //             cls: 'x-form-clear-trigger',
        //             handler: 'cleanFilter'
        //         }
        //     },
        //     listeners: {
        //         specialkey: 'setFilter'
        //     }
        // },
        {
            xtype: "container",
            title: __("Favorites"),
            itemId: "fav_status",
            layout: {
                type: "hbox"
            },
            value: undefined,
            items: [
                {
                    xtype: "displayfield",
                    fieldLabel: __("Favorites"),
                    allowBlank: true,
                    flex: 2
                },
                {
                    xtype: "button",
                    glyph: NOC.glyph.star,
                    cls: "noc-starred",
                    toggleGroup: "favgroup",
                    handler: function() {
                        this.up().value = this.pressed ? "true" : undefined;
                        this.up().fireEvent("setFilter", this.up());
                    }
                },
                {
                    xtype: "button",
                    glyph: NOC.glyph.star,
                    cls: "noc-unstarred",
                    toggleGroup: "favgroup",
                    handler: function() {
                        this.up().value = this.pressed ? "false" : undefined;
                        this.up().fireEvent("setFilter", this.up());
                    }
                }
            ],
            listeners: {
                setFilter: 'setFilter'
            },
            setValue(value) {
                this.value = value;
                if(value === undefined) { // clean
                    Ext.Array.each(this.query('[toggleGroup=favgroup]'), function(button) {button.setPressed(false)});
                    return;
                }
                if(value === "true") {
                    this.down("[cls=noc-starred]").setPressed(true);
                }
                if(value === "false") {
                    this.down("[cls=noc-unstarred]").setPressed(true);
                }
            },
            getValue: function() {
                return this.value;
            },
        },
        {
            xtype: "core.combo",
            restUrl: "/gis/geocoder/lookup/",
            itemId: "__geoaddress", // name of request query param
            fieldLabel: __("By Geo Address:"),
            typeAheadDelay: 500,
            minChars: 4,
            pageSize: 0,
            hideTrigger: true,
            hideTriggerCreate: true,
            hideTriggerUpdate: true,
            dataFields: ["id", "label", "style", "is_loose"],
            tpl:
                '<tpl for=".">' +
                '<div class="x-boundlist-item {style}">{label}</div>' +
                "</tpl>",
            triggers: {
                clear: {
                    cls: 'x-form-clear-trigger',
                    hidden: true,
                    weight: -1,
                    handler: function(field) {
                        field.setValue(null);
                        field.fireEvent("select", field);
                    }
                },
            },
            listeners: {
                select: 'setFilter'
            },
            initField: function() {
                this.setHidden(!NOC.settings.has_geocoder);
            }
        },
        {
            xtype: "core.combo",
            restUrl: "/wf/state/lookup/",
            itemId: "state", // name of request query param
            fieldLabel: __("By State:"),
            listeners: {
                select: 'setFilter'
            },
            query: {
                "allowed_models": "sa.ManagedObject"
            },
        },
        {
            xtype: "core.combo",
            restUrl: "/sa/profile/lookup/",
            itemId: 'profile', // name of http request query param
            fieldLabel: __('By SA Profile:'),
            listeners: {
                select: 'setFilter'
            }
        },
        {
            xtype: "core.combo",
            restUrl: "/sa/managedobjectprofile/lookup/",
            itemId: 'object_profile', // name of http request query param
            fieldLabel: __('By Obj. Profile:'),
            listeners: {
                select: 'setFilter'
            }
        },
        {
            xtype: "noc.core.combotree",
            restUrl: "/sa/administrativedomain/",
            isLookupField: true,
            itemId: 'administrative_domain', // name of http request query param
            fieldLabel: __('By Adm. Domain:'),
            listeners: {
                clear: 'setFilter',
                select: 'setFilter'
            }
        },
        {
            xtype: "noc.core.combotree",
            restUrl: "/inv/networksegment/",
            isLookupField: true,
            itemId: 'segment', // name of http request query param
            fieldLabel: __('By Segment:'),
            listeners: {
                clear: 'setFilter',
                select: 'setFilter'
            }
        },
        {
            xtype: "noc.core.combotree",
            restUrl: "/inv/resourcegroup/",
            isLookupField: true,
            itemId: 'effective_service_groups', // name of http request query param
            fieldLabel: __("By Service Group"),
            listeners: {
                clear: 'setFilter',
                select: 'setFilter'
            }
        },
        {
            xtype: "core.combo",
            restUrl: "/main/pool/lookup/",
            itemId: 'pool', // name of http request query param
            fieldLabel: __('By Pool:'),
            listeners: {
                select: 'setFilter'
            }
        },
        {
            xtype: "core.combo",
            restUrl: "/inv/vendor/lookup/",
            itemId: 'vendor',  // name of http request query param
            fieldLabel: __('By Vendor:'),
            listeners: {
                select: 'setFilter'
            }
        },
        {
            xtype: "core.combo",
            restUrl: "/inv/platform/lookup/",
            itemId: 'platform',  // name of http request query param
            fieldLabel: __('By Platform:'),
            listeners: {
                select: 'setFilter'
            }
        },
        {
            xtype: "core.combo",
            restUrl: "/inv/firmware/lookup/",
            itemId: 'version',  // name of http request query param
            fieldLabel: __('By Version:'),
            listeners: {
                select: 'setFilter'
            }
        },
        {
            xtype: "labelfield",
            itemId: 'labels__labels',
            fieldLabel: __('By Labels:'),
            isLookupField: true,
            toBufferTrigger: false,
            filterProtected: false,
            query: {
                "allow_models": ["sa.ManagedObject"]
            },
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
