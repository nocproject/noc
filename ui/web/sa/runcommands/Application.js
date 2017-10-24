//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.runcommands.Application');
Ext.define('NOC.sa.runcommands.Application', {
    extend: 'NOC.core.Application',
    xtype: 'layout-card',
    layout: 'card',
    alias: 'widget.runcommands',
    viewModel: 'runcommands',
    controller: 'runcommands',

    requires: [
        'Ext.layout.container.Card',
        'Ext.form.field.ComboBox',
        'NOC.sa.runcommands.ViewModel',
        'NOC.sa.runcommands.Controller',
        'NOC.core.filter.Filter'
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
            id: 'run-command-select',
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
                            reference: 'sa-run-commands-selection-grid',
                            // stateId: 'sa-run-commands-selection-grid',
                            // stateful: true,
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
                                mode: 'SIMPLE',
                                // pruneRemoved: false,
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
                                        text: __('Select All'),
                                        glyph: NOC.glyph.plus_circle,
                                        tooltip: __('Select all devices on screen'),
                                        style: {
                                            pointerEvents: 'all'
                                        },
                                        handler: 'onSelectionSelectAll'
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
                                        text: __('Select Checked'),
                                        glyph: NOC.glyph.arrow_right,
                                        tooltip: __('Move all selected devices to the right'),
                                        style: {
                                            pointerEvents: 'all'
                                        },
                                        bind: {
                                            disabled: '{!selectionGridHasSel}'
                                        },
                                        handler: 'onSelectionAddChecked'
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
                            reference: 'sa-run-commands-selected-grid-1',
                            // stateId: 'sa-run-commands-selected-grid-1',
                            // stateful: true,
                            region: 'east',
                            width: '50%',
                            resizable: true,
                            pageSize: 0,
                            border: false,
                            scrollable: true,
                            emptyText: __('nothing checked'),
                            split: {
                                xtype: 'splitter',
                                width: 1
                            },
                            bind: {
                                store: '{selectedStore}',
                                selection: '{selectedRow}'
                            },
                            selModel: 'checkboxmodel',
                            listeners: {
                                itemdblclick: 'onSelectedDblClick',
                                afterrender: 'setRowClass'
                            },
                            dockedItems: [{
                                tbar: {
                                    items: [{
                                        text: __('Remove Checked'),
                                        glyph: NOC.glyph.arrow_left,
                                        tooltip: __('Remove selected devices from right panel'),
                                        style: {
                                            pointerEvents: 'all'
                                        },
                                        bind: {
                                            disabled: '{!selectedGridHasSel}',
                                            style: {
                                                cursor: '{cursorIcon}'
                                            }
                                        },
                                        handler: 'onSelectedRemoveChecked'
                                    }, {
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
                                        xtype: 'box',
                                        bind: {
                                            html: __('Total : {total.selected}')
                                        }
                                    }]
                                }
                            }]
                        }
                    ]
                }, {
                    xtype: 'NOC.Filter',
                    reference: 'filter-panel',
                    region: 'west',
                    width: 300,
                    collapsed: true,
                    border: false,
                    animCollapse: false,
                    collapseMode: 'mini',
                    hideCollapseTool: true,
                    split: {
                        xtype: 'splitter',
                        width: 1
                    },
                    listAlign: 'left',
                    resizable: true,
                    selectionStore: 'runcommands.selectionStore'
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
                            text: __('Do Checked'),
                            tooltip: __('Go to next step'),
                            style: {
                                pointerEvents: 'all'
                            },
                            glyph: NOC.glyph.play,
                            bind: {
                                disabled: '{!hasRecords}'
                            },
                            handler: 'toNext'
                        }
                    ]
                }
            }]
        },
        {
            id: 'run-command-config',
            activeItem: 1,
            items: [
                {
                    xtype: 'grid',
                    reference: 'sa-run-commands-selected-grid-2',
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
                            xtype: 'combo',
                            reference: 'sa-run-commands-mode',
                            fieldLabel: __('Mode'),
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
                        }, {
                            xtype: 'form',
                            reference: 'sa-run-commands-command-form',
                            width: '100%',
                            border: false,
                            defaults: {
                                margin: 10,
                                padding: 20,
                                width: '80%'
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
            id: 'run-command-progress',
            activeItem: 2,
            items: [
                {
                    xtype: 'grid',
                    reference: 'sa-run-commands-selected-grid-3',
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
                    region: 'east',
                    width: '50%',
                    items: {
                        xtype: 'textarea',
                        layout: 'fit',
                        width: '100%',
                        height: 700,
                        scrollable: true,
                        padding: 4,
                        fieldStyle: {
                            'fontFamily': 'courier new',
                            'fontSize': '12px'
                        },
                        bind: {
                            value: '{resultOutput}'
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
            id: 'run-command-report',
            activeItem: 3,
            xtype: 'panel',
            reference: 'sa-run-commands-report-panel',
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
                    }
                ]
            }]
        }
    ]
});
