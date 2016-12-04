//---------------------------------------------------------------------
// NOC.core.SAApplication
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.core.SAApplication');

Ext.define('NOC.core.SAApplication', {
    extend: 'NOC.core.Application',
    layout: 'card',

    requires: [
        'NOC.core.SAApplicationModel'
    ],
    stateMap: {
        w: __('Waiting'),
        r: __('Running'),
        s: __('Success'),
        f: __('Failed')
    },

    stateCls: {
        w: 'noc-status-waiting',
        r: 'noc-status-running',
        s: 'noc-status-success',
        f: 'noc-status-failed'
    },

    initComponent: function() {
        var me = this,
            bs = 40;

        me.viewModel = Ext.create('Ext.app.ViewModel', {
            data: {
                total: {
                    selection: 0,
                    selected: 0
                },
                progressState: {
                    w: 0,
                    r: 0,
                    s: 0,
                    f: 0
                }
            },
            stores: {
                selected: {
                    model: 'NOC.core.SAApplicationModel',
                    listeners: {
                        scope: me,
                        datachanged: me.onStoreSizeChange
                    }
                }
            },
            formulas: {
                hasRecords: function(get) {
                    return get('total.selected') > 0;
                }
            }
        });
        me.cols = [
            {
                text: __('Name'),
                dataIndex: 'name',
                width: 200
            },
            {
                text: __('Address'),
                dataIndex: 'address',
                width: 100
            },
            {
                text: __('Profile'),
                dataIndex: 'profile_name',
                width: 100
            },
            {
                text: __('Platform'),
                dataIndex: 'platform',
                flex: 1
            }
        ];
        me.selectedStore = me.viewModel.get('selected');
        me.selectionStore = Ext.create('NOC.core.ModelStore', {
            model: 'NOC.core.SAApplicationModel',
            autoLoad: true,
            pageSize: bs,
            leadingBufferZone: bs * 5,
            numFromEdge: Math.ceil(bs / 2),
            trailingBufferZone: bs * 5,
            purgePageCount: 10
        });
        me.filterPanel = Ext.create('Ext.panel.Panel', {
            title: 'filters',
            region: 'west',
            width: 300,
            html: 'filter fields',
            collapsed: true,
            border: true,
            animCollapse: false,
            collapseMode: 'mini',
            hideCollapseTool: true,
            split: true,
            resizable: true
        });
        me.ITEM_SELECT = me.registerItem(
            me.createSelectPanel()
        );
        me.ITEM_CONFIG = me.registerItem(
            me.createConfigPanel()
        );
        me.ITEM_PROGRESS = me.registerItem(
            me.createProgressPanel()
        );
        me.ITEM_REPORT = me.registerItem(
            me.createReportPanel()
        );
        Ext.apply(me, {
            items: me.getRegisteredItems(),
            activeItem: me.ITEM_SELECT
        });
        me.callParent();
    },
    //
    createSelectPanel: function() {
        var me = this,
            selectionGrid, selectedGrid, selectionGridStateId, selectedGridStateId,
            selectionGridHasSelection, selectedGridHasSelection, selectedGridHasRecords,
            appName = me.appId.replace('.', '_');

        selectionGridStateId = Ext.String.format('{0}-select-grid', appName || 'name');
        selectedGridStateId = Ext.String.format('{0}-selected-grid', appName || 'name');
        selectionGridHasSelection = '{!' + selectionGridStateId + '.selection}';
        selectedGridHasSelection = '{!' + selectedGridStateId + '.selection}';
        selectedGridHasRecords = '{!hasRecords}';

        selectionGrid = Ext.create("Ext.grid.Panel", {
            reference: selectionGridStateId,
            store: me.selectionStore,
            pageSize: 0,
            border: false,
            scrollable: true,
            stateful: true,
            stateId: selectionGridStateId,
            selModel: {
                mode: 'SIMPLE',
                pruneRemoved: false,
                selType: 'checkboxmodel'
            },
            region: 'center',
            width: "50%",
            columns: me.cols.concat({
                xtype: "glyphactioncolumn",
                width: 25,
                items: [
                    {
                        glyph: NOC.glyph.arrow_right,
                        scope: me,
                        handler: me.onAddObject
                    }
                ]
            }),
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        // @todo: Search
                        {
                            glyph: NOC.glyph.refresh
                        },
                        {
                            text: __("Select Checked"),
                            glyph: NOC.glyph.plus_circle,
                            bind: {
                                disabled: selectionGridHasSelection
                            },
                            handler: function() {
                                selectedGrid.getStore().loadData(
                                    selectionGrid.getSelectionModel().getSelection()
                                );
                            }
                        },
                        {
                            text: __("Select All"),
                            glyph: NOC.glyph.plus_circle,
                            handler: function() {
                                var renderPlugin = selectionGrid.findPlugin('bufferedrenderer');
                                selectionGrid.getSelectionModel().selectRange(0, renderPlugin.getLastVisibleRowIndex());
                            }
                        },
                        {
                            text: __("Unselect All"),
                            glyph: NOC.glyph.minus_circle,
                            bind: {
                                disabled: selectionGridHasSelection
                            },
                            handler: function() {
                                selectionGrid.getSelectionModel().deselectAll();
                            }
                        },
                        "->",
                        {
                            xtype: 'box',
                            bind: {
                                html: __('Selected : {total.selection}')
                            }
                        }
                    ]
                }
            ],
            listeners: {
                selectionchange: function(element, selected) {
                    me.viewModel.set('total.selection', selected.length);
                },
                itemdblclick: function(grid, record, item, rowIndex) {
                    me.onAddObject(grid, rowIndex);
                }
            },
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me, 'row_class', true)
            }
        });

        selectedGrid = Ext.create("Ext.grid.Panel", {
            reference: selectedGridStateId,
            bind: '{selected}',
            border: false,
            scrollable: true,
            pageSize: 0,
            stateful: true,
            stateId: selectedGridStateId,
            selModel: "checkboxmodel",
            region: 'east',
            width: "50%",
            columns: [
                {
                    xtype: "glyphactioncolumn",
                    width: 25,
                    items: [
                        {
                            glyph: NOC.glyph.arrow_left,
                            scope: me,
                            handler: me.onRemoveObject
                        }
                    ]
                }].concat(me.cols),
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: __("Remove Checked"),
                            glyph: NOC.glyph.minus_circle,
                            bind: {
                                disabled: selectedGridHasSelection
                            },
                            handler: function() {
                                selectedGrid.getStore().remove(
                                    selectedGrid.getSelectionModel().getSelection()
                                );
                            }
                        },
                        {
                            text: __("Remove All"),
                            glyph: NOC.glyph.minus_circle,
                            bind: {
                                disabled: selectedGridHasRecords
                            },
                            handler: function() {
                                selectedGrid.getStore().removeAll();
                            }
                        },
                        "->",
                        {
                            xtype: 'box',
                            bind: {
                                html: __('Total : {total.selected}')
                                // html: __('Total : {selected.data.length}')
                            }
                        }
                    ]
                }
            ],
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me, 'row_class', true)
            }
        });

        me.selectContinueButton = Ext.create("Ext.button.Button", {
            text: __("Continue"),
            glyph: NOC.glyph.play,
            bind: {
                disabled: selectedGridHasRecords
            },
            handler: function() {
                me.showItem(me.ITEM_CONFIG);
            }
        });

        return Ext.create("Ext.panel.Panel", {
            layout: 'border',
            scrollable: false,
            items: [
                selectionGrid,
                selectedGrid,
                me.filterPanel
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.selectContinueButton,
                        '->',
                        {
                            xtype: 'button',
                            text: '<i class="fa fa-filter" aria-hidden="true"></i>',
                            scope: me,
                            handler: function() {
                                me.filterPanel.toggleCollapse();
                            }
                        }
                    ]
                }
            ]
        });
    },
    //
    createConfigPanel: function() {
        var me = this,
            selectedGrid,
            appName = me.appId.replace('.', '_');

        selectedGrid = Ext.create("Ext.grid.Panel", {
            bind: '{selected}',
            border: false,
            scrollable: true,
            stateful: true,
            stateId: appName + "-selected-grid",
            region: 'west',
            width: "50%",
            columns: me.cols,
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me, 'row_class', true)
            }
        });

        me.runButton = Ext.create("Ext.button.Button", {
            text: __("Run"),
            glyph: NOC.glyph.play,
            disabled: true,
            scope: me,
            handler: me.onRun
        });

        return Ext.create("Ext.panel.Panel", {
            layout: "border",
            activeItem: 1,
            items: [
                selectedGrid,
                {
                    region: 'east',
                    width: "50%",
                    border: false,
                    items: me.getConfigPanel()
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            glyph: NOC.glyph.arrow_left,
                            scope: me,
                            tooltip: __("Back"),
                            handler: function() {
                                me.showItem(me.ITEM_SELECT);
                            }
                        },
                        "-",
                        me.runButton
                    ]
                }
            ]
        });
    },
    //
    createProgressPanel: function() {
        var me = this,
            selectedGrid,
            appName = me.appId.replace('.', '_');

        me.progressState = {
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
                toggle: {
                    scope: me,
                    fn: function(value) {
                        this.selectedStore.filterBy(function(record) {
                            return value.getValue().indexOf(record.get('status')) !== -1;
                        });
                    }
                }
            }
        };

        selectedGrid = Ext.create("Ext.grid.Panel", {
            bind: '{selected}',
            border: false,
            scrollable: true,
            stateful: true,
            region: 'west',
            width: "50%",
            stateId: appName + "-selected-grid",
            selModel: {
                mode: 'SINGLE',
                selType: 'checkboxmodel'
            },
            columns: me.cols.concat({
                text: __("Status"),
                dataIndex: "status",
                width: 70,
                renderer: NOC.render.Choices({
                    w: __("Waiting"),
                    r: __("Running"),
                    f: __("Failed"),
                    s: __("Success")
                })
            }),
            listeners: {
                scope: me,
                select: me.onShowResult
            },
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: me.progressState
            }],
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me, 'status', true)
            }
        });

        me.resultPanel = me.getResultPanel();

        me.progressBackButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.arrow_left,
            tooltip: __("Back"),
            disabled: true,
            scope: me,
            handler: function() {
                me.showItem(me.ITEM_CONFIG);
            }
        });

        me.progressReportButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.print,
            tooltip: __("Report"),
            disabled: true,
            handler: function() {
                var r = me.showItem(me.ITEM_REPORT);
                r.setHtml(
                    me.buildReport()
                );
            }
        });

        return Ext.create("Ext.panel.Panel", {
            layout: "border",
            items: [
                selectedGrid,
                {
                    region: 'east',
                    width: "50%",
                    items: me.resultPanel
                }
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.progressBackButton,
                        me.progressReportButton
                    ]
                }
            ]
        });
    },
    //
    createReportPanel: function() {
        var me = this;
        return Ext.create("Ext.panel.Panel", {
            html: "",
            scrollable: true,
            bodyPadding: 4,
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    {
                        glyph: NOC.glyph.arrow_left,
                        tooltip: __("Back"),
                        scope: me,
                        handler: function() {
                            me.showItem(me.ITEM_PROGRESS);
                        }
                    }
                ]
            }]
        });
    },
    // Return Grid's row classes
    getRowClass: function(record, index, params, store, fieldName) {
        var value = record.get(fieldName);
        if(value) {
            switch(fieldName) {
                case 'status':
                    var className = this.stateCls[value];
                    if(className) {
                        return className;
                    }
                    break;
                case 'row_class':
                    return value;
                    break;
            }
        }
        return '';
    },
    //
    onAddObject: function(grid, rowIndex) {
        var selectedRecord = grid.store.getAt(rowIndex);

        grid.getSelectionModel().select(
            grid.getSelectionModel()
                .getSelection()
                .concat(selectedRecord)
        );
        this.selectedStore.add(selectedRecord);
        // this.viewModel.notify();
    },
    //
    onRemoveObject: function(grid, rowIndex, colIndex) {
        grid.store.removeAt(rowIndex);
    },

    stateInc: function(state, step) {
        console.log(state + '=' + this.viewModel.get(state) + ', step =' + step);
        this.viewModel.set(state, this.viewModel.get(state) + step)
    },

    onRun: function() {
        var me = this,
            xhr, cfg,
            params = [],
            offset = 0,
            rxChunk = /^(\d+)\|/;
        // Get params and check errors
        cfg = me.getArgs();
        me.viewModel.set('progressState.r', 0);
        me.viewModel.set('progressState.w', 0);
        me.viewModel.set('progressState.f', 0);
        me.viewModel.set('progressState.s', 0);
        me.selectedStore.each(function(record) {
            var v = {};
            // Copy config
            Ext.Object.each(cfg, function(key, value) {
                if(key !== "id") {
                    v[key] = value;
                }
            });
            v.id = record.get("id");
            record.set('status', 'w');
            params.push(v);
        });
        //
        me.progressReportButton.setDisabled(true);
        me.progressBackButton.setDisabled(true);
        me.showItem(me.ITEM_PROGRESS);
        me.viewModel.set('progressState.w', me.selectedStore.count());
        // Start streaming request
        xhr = new XMLHttpRequest();
        xhr.open(
            "POST",
            "/api/mrt/",
            true
        );
        xhr.setRequestHeader("Content-Type", "text/json");
        xhr.onprogress = function() {
            // Parse incoming chunks
            var ft = xhr.responseText.substr(offset),
                match, l, lh, chunk, record;

            while(ft) {
                match = ft.match(rxChunk);
                if(!match) {
                    break;
                }
                lh = match[0].length;
                l = parseInt(match[1]);
                chunk = JSON.parse(ft.substr(lh, l));
                offset += lh + l;
                ft = ft.substr(lh + l);
                // Process chunk
                record = me.selectedStore.getById(chunk.id);
                if(chunk.error && 'f' != record.get('status')) {
                    record.set({
                        status: 'f',
                        result: chunk.error
                    });
                    me.stateInc('progressState.r', -1);
                    me.stateInc('progressState.f', 1);
                }
                if(chunk.running && 'r' != record.get('status')) {
                    record.set('status', 'r');
                    me.stateInc('progressState.w', -1);
                    me.stateInc('progressState.r', 1);
                }
                if(chunk.result && 's' != record.get('status')) {
                    record.set({
                        status: 's',
                        result: chunk.result
                    });
                    me.stateInc('progressState.r', -1);
                    me.stateInc('progressState.s', 1);
                }
                console.log(chunk);
            }
        };
        xhr.onload = function() {
            me.progressReportButton.setDisabled(false);
            me.progressBackButton.setDisabled(false);
        };
        xhr.onerror = function(e) {
            NOC.error('Error!');
            me.selectedStore.each(function(record) {
                if('r' === record.get('status')) {
                    record.set({
                        status: 'f',
                        result: 'RPC call failed: net::ERR_INCOMPLETE_CHUNKED_ENCODING'
                    });
                    me.stateInc('progressState.r', -1);
                    me.stateInc('progressState.f', 1);
                }
            });
            me.viewModel.set('progressState.r', 0);
            me.progressReportButton.setDisabled(false);
            me.progressBackButton.setDisabled(false);
        };
        xhr.send(JSON.stringify(params));
    },
    //
    onShowResult: function(grid, record) {
        var me = this;

        me.resultPanel.showResult(record.get("result"));
    },

    buildReport: function() {
        var r = [];

        this.selectedStore.each(function(record) {
            r.push("<div class='noc-mrt-section'>" + record.get("name") + "(" + record.get("address") + ")</div>");
            r.push("<div class='noc-mrt-result'>" + record.get("result") + "</div>");
        });
        return r.join("\n");
    },
    //
    onStoreSizeChange: function() {
        this.viewModel.set('total.selected', this.selectedStore.getCount());
    },

    onFilterCollapse: function() {
        console.log('xxx');
        // me.filterPanel.collapse();
    }
});
