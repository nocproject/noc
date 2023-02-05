//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.managedobject.Application');
Ext.define('NOC.sa.managedobject.Application', {
    itemId: "sa-managedobject",
    extend: 'NOC.core.Application',
    layout: 'card',
    alias: 'widget.managedobject',
    viewModel: 'managedobject',
    controller: 'managedobject',
    requires: [
        'Ext.layout.container.Card',
        'Ext.form.field.ComboBox',
        'NOC.sa.managedobject.ViewModel',
        'NOC.sa.managedobject.Controller',
        'NOC.core.filter.Filter',
        'NOC.sa.managedobject.form.View',
    ],
    stateMap: {
        w: __('Waiting'),
        r: __('Running'),
        s: __('Success'),
        f: __('Failed')
    },
    defaults: {
        xtype: 'panel',
        layout: 'border',
        border: false,
        scrollable: false
    },
    items: [
        {
            itemId: 'managedobject-select',
            activeItem: 0,
            items: [
                {   // device panel
                    xtype: 'panel',
                    layout: 'border',
                    region: 'center',
                    border: false,
                    scrollable: false,
                    items: [
                        {
                            xtype: 'grid', // selection grid
                            reference: 'saManagedobjectSelectionGrid',
                            region: 'center',
                            width: '50%',
                            resizable: true,
                            pageSize: 0,
                            border: false,
                            scrollable: true,
                            emptyText: __('Not Found'),
                            bind: {
                                store: '{selectionStore}',
                                selection: '{selectionRow}'
                            },
                            selModel: {
                                mode: 'MULTI',
                                selType: 'checkboxmodel'
                            },
                            listeners: {
                                selectionchange: 'onSelectionChange',
                                itemdblclick: 'onSelectionDblClick',
                                afterrender: 'setRowClass'
                            },
                            dockedItems: [{
                                tbar: {
                                    items: [{ // @todo: Search
                                        glyph: NOC.glyph.refresh,
                                        tooltip: __('Refresh data'),
                                        style: {
                                            pointerEvents: 'all'
                                        },
                                        handler: 'onSelectionRefresh'
                                    }, {
                                        xtype: 'combo',
                                        editable: false,
                                        minWidth: 225,
                                        emptyText: __('Group select'),
                                        store: {
                                            fields: ['cmd', 'title'],
                                            data: [
                                                {'cmd': 'SCREEN', 'title': __('All devices on screen')},
                                                {'cmd': 'FIRST_50', 'title': __('First 50')},
                                                {'cmd': 'FIRST_100', 'title': __('First 100')},
                                                {'cmd': 'N_ROWS', 'title': __('First N')},
                                                {'cmd': 'PERIOD', 'title': __('Period start,qty')}
                                            ]
                                        },
                                        queryMode: 'local',
                                        displayField: 'title',
                                        valueField: 'cmd',
                                        listeners: {
                                            select: 'onSelectionSelectAll'
                                        }
                                    }, {
                                        text: __('Unselect All'),
                                        glyph: NOC.glyph.minus_circle,
                                        tooltip: __('Unselect all devices'),
                                        style: {
                                            pointerEvents: 'all'
                                        },
                                        bind: {
                                            disabled: '{!selectionGridHasSel}'
                                        },
                                        handler: 'onSelectionUnselectAll'
                                    }, '->', {
                                        text: __('Add'),
                                        glyph: NOC.glyph.cart_plus,
                                        tooltip: __('Move all selected devices to the basket'),
                                        style: {
                                            pointerEvents: 'all'
                                        },
                                        bind: {
                                            disabled: '{!selectionGridHasSel}'
                                        },
                                        handler: 'onSelectionAddChecked'
                                    }, '|', {
                                        glyph: NOC.glyph.shopping_cart,
                                        tooltip: __('Show/Hide Basket'),
                                        style: {
                                            pointerEvents: 'all'
                                        },
                                        bind: {
                                            disabled: '{!hasRecords}',
                                            text: '{total.selected}',
                                            style: {
                                                cursor: '{cursorIcon}'
                                            }
                                        },
                                        handler: 'toggleBasket'
                                    }, '|', {
                                        xtype: 'box',
                                        bind: {
                                            html: __('Selected : {total.selection}')
                                        }
                                    }]
                                }
                            }],
                            viewConfig: {
                                enableTextSelection: true
                            }
                        }, {
                            xtype: 'grid', // selected grid
                            reference: 'saManagedobjectSelectedGrid1',
                            region: 'east',
                            width: '50%',

                            collapsed: true,
                            animCollapse: false,
                            collapseMode: 'mini',
                            hideCollapseTool: true,

                            resizable: true,
                            pageSize: 0,
                            border: false,
                            scrollable: true,
                            emptyText: __('nothing checked'),
                            split: {
                                xtype: 'splitter'
                            },
                            bind: {
                                store: '{selectedStore}',
                                selection: '{selectedRow}'
                            },
                            listeners: {
                                itemdblclick: 'onSelectedDblClick',
                                afterrender: 'setRowClass'
                            },
                            dockedItems: [{
                                tbar: {
                                    items: [{
                                        text: __('Remove All'),
                                        glyph: NOC.glyph.minus_circle,
                                        tooltip: __('Remove all devices from right panel'),
                                        style: {
                                            pointerEvents: 'all'
                                        },
                                        bind: {
                                            disabled: '{!hasRecords}',
                                            style: {
                                                cursor: '{cursorIcon}'
                                            }
                                        },
                                        handler: 'onSelectedRemoveAll'
                                    }, '->', {
                                        glyph: NOC.glyph.shopping_cart,
                                        style: {
                                            pointerEvents: 'all'
                                        },
                                        bind: {
                                            text: __('Total : {total.selected}'),
                                            tooltip: __('Hide basket'),
                                            style: {
                                                cursor: '{cursorIcon}'
                                            }
                                        },
                                        handler: 'toggleBasket'
                                    }
                                    ]
                                }
                            }]
                        }
                    ]
                },
                {
                    xtype: 'NOC.Filter',
                    reference: 'filterPanel',
                    region: 'west',
                    width: 300,
                    collapsed: true,
                    border: false,
                    animCollapse: false,
                    collapseMode: 'mini',
                    hideCollapseTool: true,
                    split: {
                        xtype: 'splitter'
                    },
                    treeAlign: 'left',
                    resizable: true,
                    selectionStore: 'managedobject.selectionStore'
                }
            ],
            dockedItems: [{
                tbar: {
                    items: [
                        {
                            text: __('Filtering List'),
                            glyph: NOC.glyph.filter,
                            tooltip: __('Show/Hide Filter'),
                            style: {
                                pointerEvents: 'all'
                            },
                            handler: 'collapseFilter'
                        }, {
                            xtype: 'splitbutton',
                            text: __('Group Operation'),
                            tooltip: __('Select Action'),
                            style: {
                                pointerEvents: 'all'
                            },
                            bind: {
                                disabled: '{!hasRecords}'
                            },
                            menu: new Ext.menu.Menu({
                                items: [
                                    {text: 'Run Commands', handler: 'toNext'},
                                    {text: 'Item 2', handler: function() {alert("Item 2 clicked");}}
                                ]
                            })
                        }, {
                            itemId: "createBtn",
                            text: __("Add"),
                            glyph: NOC.glyph.plus,
                            tooltip: __("Add new record"),
                            hasAccess: NOC.hasPermission("create"),
                            handler: "onNewRecord"
                        },
                    ]
                }
            }]
        },
        {
            itemId: 'managedobject-config',
            activeItem: 1,
            items: [
                {
                    xtype: 'grid',
                    reference: 'saManagedobjectSelectedGrid2',
                    region: 'center',
                    width: '50%',
                    border: false,
                    scrollable: true,
                    bind: '{selectedStore}',
                    listeners: {
                        afterrender: 'setRowClass'
                    }
                },
                {
                    xtype: 'panel',
                    region: 'east',
                    width: '50%',
                    border: false,
                    defaults: {
                        padding: 4,
                        width: '80%'
                    },
                    items: [
                        {
                            xtype: 'panel',
                            border: false,
                            defaults: {
                                padding: 10
                            },
                            layout: {
                                type: 'hbox',
                                align: 'middle'
                            },
                            items: [
                                {
                                    xtype: 'checkboxfield',
                                    reference: 'ignoreCliErrors',
                                    boxLabel: __('Ignore CLI errors'),
                                    checked: true
                                },
                                {
                                    xtype: 'combo',
                                    reference: 'saManagedobjectMode',
                                    fieldLabel: __('Mode'),
                                    labelWidth: 50,
                                    queryMode: 'local',
                                    displayField: 'name',
                                    valueField: 'value',
                                    editable: false,
                                    store: {
                                        data: [
                                            {value: 'commands', name: __('Run Commands')},
                                            {value: 'snippet', name: __('Run Snippet')},
                                            {value: 'action', name: __('Run Action')}
                                        ]
                                    },
                                    listeners: {
                                        change: 'onConfigModeChange',
                                        afterrender: function(field) {
                                            field.setValue('commands');
                                        }
                                    }
                                }
                            ]
                        },
                        {
                            xtype: 'form',
                            reference: 'saManagedobjectCommandForm',
                            width: '100%',
                            border: false,
                            defaults: {
                                margin: 10,
                                padding: 20,
                                width: '80%'
                            },
                            bind: {
                                disabled: '{!hasRecords}'
                            },
                            dockedItems: [{
                                xtype: 'toolbar',
                                dock: 'top',
                                ui: 'header',
                                defaults: {minWidth: '<a href="#cfg-minButtonWidth">minButtonWidth</a>'},
                                items: [
                                    {xtype: 'component', flex: 1},
                                    {
                                        xtype: 'button', text: __('Run'),
                                        glyph: NOC.glyph.play,
                                        disabled: true,
                                        formBind: true,
                                        handler: 'onRun'
                                    }
                                ]
                            }]
                        }
                    ]
                }
            ],
            dockedItems: [{
                tbar: {
                    items: [
                        {
                            glyph: NOC.glyph.arrow_left,
                            tooltip: __('Back'),
                            style: {
                                pointerEvents: 'all'
                            },
                            handler: 'toPrev'
                        }
                    ]
                }
            }]
        },
        {
            itemId: 'run-command-progress',
            activeItem: 2,
            items: [
                {
                    xtype: 'grid',
                    reference: 'saManagedobjectSelectedGrid3',
                    region: 'center',
                    width: '50%',
                    border: false,
                    scrollable: true,
                    bind: '{selectedStore}',
                    selModel: {
                        mode: 'SINGLE',
                        selType: 'checkboxmodel'
                    },
                    listeners: {
                        afterrender: 'setStatusClass',
                        select: 'onShowResult'
                    },
                    dockedItems: [{
                        xtype: 'toolbar',
                        dock: 'top',
                        items: {
                            xtype: 'segmentedbutton',
                            height: 25,
                            columns: 4,
                            frame: false,
                            allowMultiple: true,
                            items: [
                                {
                                    pressed: true,
                                    value: 'w',
                                    bind: {
                                        text: '<span>' + __('Waiting') + '&nbsp;<span class="noc-badge noc-badge-waiting">{progressState.w}</span></span>'
                                    }
                                },
                                {
                                    pressed: true,
                                    value: 'r',
                                    bind: {
                                        text: '<span>' + __('Running') + '&nbsp;<span class="noc-badge noc-badge-running">{progressState.r}</span></span>'
                                    }
                                },
                                {
                                    pressed: true,
                                    value: 'f',
                                    bind: {
                                        text: '<span>' + __('Failed') + '&nbsp;<span class="noc-badge noc-badge-failed">{progressState.f}</span></span>'
                                    }
                                },
                                {
                                    pressed: true,
                                    value: 's',
                                    bind: {
                                        text: '<span>' + __('Success') + '&nbsp;<span class="noc-badge noc-badge-success">{progressState.s}</span></span>'
                                    }
                                }
                            ],
                            listeners: {
                                toggle: 'onStatusToggle'
                            }
                        }
                    }]
                },
                {
                    xtype: 'panel',
                    region: 'east',
                    width: '50%',
                    scrollable: true,
                    padding: 4,
                    items: {
                        xtype: 'container',
                        layout: 'fit',
                        fieldStyle: {
                            'fontFamily': 'courier new',
                            'fontSize': '12px'
                        },
                        bind: {
                            html: '{resultOutput}'
                        }
                    }
                }
            ],
            dockedItems: [{
                tbar: {
                    items: [
                        {
                            glyph: NOC.glyph.arrow_left,
                            tooltip: __('Back'),
                            style: {
                                pointerEvents: 'all'
                            },
                            handler: 'toPrev',
                            bind: {
                                disabled: '{isRunning}'
                            }
                        }, {
                            glyph: NOC.glyph.print,
                            tooltip: __('Report'),
                            style: {
                                pointerEvents: 'all'
                            },
                            bind: {
                                disabled: '{isRunning}'
                            },
                            handler: 'onReportClick'
                        }
                    ]
                }
            }]
        },
        {
            itemId: 'run-command-report',
            activeItem: 3,
            xtype: 'panel',
            reference: 'saRunCommandReportPanel',
            html: '',
            scrollable: true,
            bodyPadding: 4,
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                items: [
                    {
                        glyph: NOC.glyph.arrow_left,
                        tooltip: __('Back'),
                        style: {
                            pointerEvents: 'all'
                        },
                        handler: 'toPrev'
                    },
                    {
                        glyph: NOC.glyph.download,
                        tooltip: __('Download results'),
                        style: {
                            pointerEvents: 'all'
                        },
                        handler: 'onDownload'
                    }
                ]
            }]
        },
        {
            activeItem: 4,
            itemId: 'managedobject-form',
            items: [
                {
                    xtype: 'managedobject.form',
                }
            ]
        },
    ],
    destroy: Ext.emptyFn,
});
