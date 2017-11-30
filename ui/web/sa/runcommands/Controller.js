//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.runcommands.Controller');
Ext.define('NOC.sa.runcommands.Controller', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.runcommands',

    init: function(app) {
        var selectionGrid = app.lookupReference('sa-run-commands-selection-grid');
        var selectedGrid1 = app.lookupReference('sa-run-commands-selected-grid-1');
        var selectedGrid2 = app.lookupReference('sa-run-commands-selected-grid-2');
        var selectedGrid3 = app.lookupReference('sa-run-commands-selected-grid-3');
        var defaultCols = [
            {
                text: __('Name'),
                dataIndex: 'name',
                width: 200
            }, {
                text: __('Address'),
                dataIndex: 'address',
                width: 100
            }, {
                text: __('Profile'),
                dataIndex: 'profile',
                width: 100
            }, {
                text: __('Platform'),
                dataIndex: 'platform',
                flex: 1
            }, {
                text: __('Version'),
                dataIndex: 'version',
                flex: 1
            }
        ];

        // page 1 init selection grid
        Ext.Array.each(defaultCols.concat({
            xtype: 'glyphactioncolumn',
            width: 25,
            items: [{
                glyph: NOC.glyph.arrow_right,
                handler: 'onAddObject'
            }]
        }), function(col, index) {
            selectionGrid.headerCt.insert(index + 1, col);
        });
        selectionGrid.getView().refresh();
        // page 1 init selected grid
        Ext.Array.each([{
            xtype: 'glyphactioncolumn',
            width: 25,
            items: [{
                glyph: NOC.glyph.arrow_left,
                handler: 'onRemoveObject'
            }]
        }].concat(defaultCols), function(col, index) {
            selectedGrid1.headerCt.insert(index + 1, col);
        });
        selectedGrid1.getView().refresh();
        // page 2 init selected grid
        Ext.Array.each(defaultCols, function(col, index) {
            selectedGrid2.headerCt.insert(index + 1, col);
        });
        selectedGrid2.getView().refresh();
        // page 3 init selected grid
        Ext.Array.each(defaultCols.concat({
            text: __('Status'),
            dataIndex: 'status',
            width: 70,
            renderer: NOC.render.Choices({
                w: __('Waiting'),
                r: __('Running'),
                f: __('Failed'),
                s: __('Success')
            })
        }), function(col, index) {
            selectedGrid3.headerCt.insert(index + 1, col);
        });
        selectedGrid3.getView().refresh();

        app.lookupReference('filter-panel').appId = 'sa.runcommands';
    },
    //
    onAddObject: function(grid, rowIndex) {
        var checkedRecord = grid.store.getAt(rowIndex);

        grid.getSelectionModel().select(
            grid.getSelectionModel()
            .getSelection()
            .concat(checkedRecord)
        );
        this.getStore('selectedStore').add(checkedRecord);
        // this.viewModel.notify();
    },
    //
    onRemoveObject: function(grid, rowIndex) {
        grid.store.removeAt(rowIndex);
    },
    //
    onStoreSizeChange: function() {
        this.getViewModel().set('total.selected', this.getStore('selectedStore').getCount());
    },
    //
    collapseFilter: function() {
        this.lookupReference('filter-panel').toggleCollapse();
    },
    //
    setRowClass: function(grid) {
        grid.getView().getRowClass = this.getRowClass;
    },
    //
    getRowClass: function(record) {
        var value = record.get('row_class');

        if(value) {
            return value;
        }
        return '';
    },
    //
    setStatusClass: function(grid) {
        grid.getView().getRowClass = this.getStatusClass;
    },
    //
    getStatusClass: function(record) {
        var value = record.get('status');

        if(value) {
            var stateCls = {
                w: 'noc-status-waiting',
                r: 'noc-status-running',
                s: 'noc-status-success',
                f: 'noc-status-failed'
            };
            var className = stateCls[value];

            if(className) {
                return className;
            }
        }
        return '';
    },
    //
    onSelectionRefresh: function() {
        this.lookupReference('sa-run-commands-selection-grid').getStore().reload();
    },
    //
    onSelectionChange: function(element, selected) {
        this.getViewModel().set('total.selection', selected.length);
    },
    //
    onSelectionDblClick: function(grid, record, item, rowIndex) {
        this.onAddObject(grid, rowIndex);
    },
    //
    onSelectionSelectAll: function() {
        var selectionGrid = this.lookupReference('sa-run-commands-selection-grid');
        var renderPlugin = selectionGrid.findPlugin('bufferedrenderer');

        selectionGrid.getSelectionModel().selectRange(0, renderPlugin.getLastVisibleRowIndex());
    },
    //
    onSelectionUnselectAll: function() {
        this.lookupReference('sa-run-commands-selection-grid').getSelectionModel().deselectAll();
    },
    //
    onSelectionAddChecked: function() {
        this.lookupReference('sa-run-commands-selected-grid-1').getStore().loadData(
            this.lookupReference('sa-run-commands-selection-grid').getSelection()
        );
    },
    //
    onSelectedRemoveChecked: function() {
        var selectedGrid = this.lookupReference('sa-run-commands-selected-grid-1');

        selectedGrid.getStore().remove(
            selectedGrid.getSelectionModel().getSelection()
        );
    },
    //
    onSelectedRemoveAll: function() {
        this.lookupReference('sa-run-commands-selected-grid-1').getStore().removeAll();
    },
    //
    onSelectedDblClick: function(grid, record, item, rowIndex) {
        this.lookupReference('sa-run-commands-selected-grid-1').getStore().removeAt(rowIndex);
    },
    //
    onConfigModeChange: function(field, mode) {
        var commandForm = this.lookupReference('sa-run-commands-command-form');

        commandForm.removeAll();
        switch(mode) {
            case 'action': {
                commandForm.add({
                    xclass: 'NOC.sa.action.LookupField',
                    reference: 'sa-run-commands-action-field',
                    name: 'modeId',
                    fieldLabel: __('Actions'),
                    allowBlank: false,
                    editable: false,
                    listeners: {
                        change: 'onChangeAction'
                    }
                });
                break;
            }
            case 'snippet': {
                commandForm.add({
                    xclass: 'NOC.sa.commandsnippet.LookupField',
                    reference: 'sa-run-commands-snippet-field',
                    name: 'modeId',
                    fieldLabel: __('Snippets'),
                    allowBlank: false,
                    editable: false,
                    listeners: {
                        change: 'onChangeSnippet'
                    }
                });
                break;
            }
            case 'commands': {
                commandForm.add({
                    xtype: 'textareafield',
                    reference: 'sa-run-commands-command-field',
                    name: 'cmd',
                    fieldLabel: __('Commands'),
                    labelAlign: 'top',
                    allowBlank: false,
                    height: 500,
                    scrollable: true
                });
            }
        }
    },
    //
    onChangeAction: function(field, newValue) {
        this.addFields('action', newValue);
    },
    //
    onChangeSnippet: function(field, newValue) {
        this.addFields('snippet', newValue);
    },
    //
    onRun: function() {
        var me = this;
        var mode = this.lookupReference('sa-run-commands-mode').getValue();
        var makeRequest = function(mode) {
            var objects = [];
            var config = me.lookupReference('sa-run-commands-command-form').getValues();

            me.getStore('selectedStore').each(function(record) {
                objects.push(record.get('id'));
            });

            delete config['modeId'];

            for(var key in config) {
                if(config.hasOwnProperty(key)) {
                    if(!config[key]) {
                        delete config[key];
                    }
                }
            }
            Ext.Ajax.request({
                method: 'POST',
                params: JSON.stringify({objects: objects, config: config}),
                headers: {'Content-Type': 'application/json'},
                url: Ext.String.format('/sa/runcommands/render/{0}/{1}/', mode, me.idForRender),

                success: function(response) {
                    var obj = Ext.decode(response.responseText);
                    var commands = [];

                    for(var key in obj) {
                        if(obj.hasOwnProperty(key) && obj[key]) {
                            commands.push({
                                id: key,
                                script: 'commands',
                                args: {
                                    commands: obj[key].split('\n'),
                                    include_commands: true
                                }
                            });
                        }
                    }
                    if(commands.length > 0) {
                        me.sendCommands(mode, commands);
                    } else {
                        NOC.error(__('Empty command'))
                    }
                },

                failure: function(response) {
                    NOC.error(__('server-side failure with status code ' + response.status));
                }
            });
        };

        // Reset state
        this.lookupReference('sa-run-commands-selected-grid-3').getSelectionModel().deselectAll();
        this.getViewModel().set('resultOutput', '');

        switch(mode) {
            case 'commands': {
                this.sendCommands('commands', {
                    'script': 'commands',
                    'args': {
                        'commands': this.lookupReference('sa-run-commands-command-form').getValues().cmd.split('\n'),
                        'include_commands': 'true',
                        'ignore_cli_errors': 'true'
                    }
                });
                break;
            }
            default:
                makeRequest(mode);
        }
    },
    //
    onStatusToggle: function(value) {
        this.getStore('selectedStore').filterBy(function(record) {
            return value.getValue().indexOf(record.get('status')) !== -1;
        });
    },
    //
    onReportClick: function() {
        this.lookupReference('sa-run-commands-report-panel').setHtml(this.buildReport());
        this.toNext();
    },
    //
    onShowResult: function(grid, record) {
        var acc = [];

        this.makeReportRow(record, acc);
        this.getViewModel().set('resultOutput', acc.join('\n'));
    },
    //
    toNext: function() {
        this.navigate(1);
    },
    //
    toPrev: function() {
        this.navigate(-1);
    },
    //
    // Private function
    //
    navigate: function(inc) {
        var l = this.getView().getLayout();
        var i = l.activeItem.activeItem;
        var next = parseInt(i, 10) + inc;

        l.setActiveItem(next);
    },
    //
    addFields: function(mode, newValue) {
        var me = this;

        if(newValue) {
            this.idForRender = newValue;
            Ext.Ajax.request({
                url: Ext.String.format('/sa/runcommands/form/{0}/{1}/', mode, newValue),

                success: function(response) {
                    var obj = Ext.decode(response.responseText);
                    var commandForm = me.lookupReference('sa-run-commands-command-form');

                    Ext.Array.each(commandForm.items.items.slice(), function(item) {
                        if(!item.reference) {
                            commandForm.remove(item);
                        }
                    });
                    // commandForm.removeAll();
                    commandForm.add(obj);
                },

                failure: function(response) {
                    NOC.error(__('server-side failure with status code ' + response.status));
                }
            });
        }
    },
    //
    stateInc: function(state, step) {
        this.getViewModel().set(state, this.getViewModel().get(state) + step)
    },
    //
    sendCommands: function(mode, cfg) {
        var me = this,
            xhr,
            params = [],
            offset = 0,
            rxChunk = /^(\d+)\|/,
            viewModel = this.getViewModel(),
            selectedStore = this.getStore('selectedStore');

        viewModel.set('progressState.r', 0);
        viewModel.set('progressState.w', 0);
        viewModel.set('progressState.f', 0);
        viewModel.set('progressState.s', 0);
        selectedStore.each(function(record) {
            var v = {
                id: record.get('id')
            };


            if('commands' === mode) {
                // Copy config
                Ext.Object.each(cfg, function(key, value) {
                    if(key !== 'id') {
                        v[key] = value;
                    }
                });
                params.push(v);
            } else {
                var param = cfg.filter(function(e) {
                    return e.id === v.id
                });

                if(param.length) {
                    params.push(param[0]);
                }
            }
            record.set('status', 'w');
        });
        this.toNext();
        viewModel.set('isRunning', true);
        viewModel.set('progressState.w', selectedStore.count());
        // Start streaming request
        xhr = new XMLHttpRequest();
        xhr.open(
            'POST',
            '/api/mrt/',
            true
        );
        xhr.setRequestHeader('Content-Type', 'text/json');
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
                record = selectedStore.getById(chunk.id);
                if(chunk.error && 'f' !== record.get('status')) {
                    record.set({
                        status: 'f',
                        result: chunk.error
                    });
                    me.stateInc('progressState.r', -1);
                    me.stateInc('progressState.f', 1);
                }
                if(chunk.running && 'r' !== record.get('status')) {
                    record.set('status', 'r');
                    me.stateInc('progressState.w', -1);
                    me.stateInc('progressState.r', 1);
                }
                if(chunk.result && 's' !== record.get('status')) {
                    record.set({
                        status: 's',
                        result: chunk.result
                    });
                    me.stateInc('progressState.r', -1);
                    me.stateInc('progressState.s', 1);
                }
                // console.log(chunk);
            }
        };
        xhr.onload = function() {
            viewModel.set('isRunning', false);
        };
        xhr.onerror = function(e) {
            NOC.error('Error!');
            selectedStore.each(function(record) {
                if('r' === record.get('status')) {
                    record.set({
                        status: 'f',
                        result: 'RPC call failed: net::ERR_INCOMPLETE_CHUNKED_ENCODING'
                    });
                    me.stateInc('progressState.r', -1);
                    me.stateInc('progressState.f', 1);
                }
            });
            viewModel.set('progressState.r', 0);
            viewModel.set('isRunning', false);
        };
        xhr.send(JSON.stringify(params));
    },
    //
    buildReport: function() {
        var r = [];

        this.getStore('selectedStore').each(function (record) {
            this.makeReportRow(record, r);
        }, this);
        return r.join('\n');
    },
    //
    makeReportRow: function(record, ac) {
        ac.push('<div class=\'noc-mrt-section\'>' + record.get('name') + '(' + record.get('address') + ')</div>');
        ac.push('<div class=\'noc-mrt-result\'>' + record.get('result').map(function(e){return '<b>#</b> ' + e;}).join('\n') + '</div>');
    }
});
