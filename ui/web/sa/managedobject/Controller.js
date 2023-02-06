//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.managedobject.Controller');
Ext.define('NOC.sa.managedobject.Controller', {
    extend: 'Ext.app.ViewController',
    requires: [
        "Ext.ux.grid.column.GlyphAction",
    ],
    alias: 'controller.managedobject',

    init: function(app) {
        var selectionGrid = app.lookupReference('saManagedobjectSelectionGrid');
        var selectedGrid1 = app.lookupReference('saManagedobjectSelectedGrid1');
        var selectedGrid2 = app.lookupReference('saManagedobjectSelectedGrid2');
        var selectedGrid3 = app.lookupReference('saManagedobjectSelectedGrid3');
        var defaultCols = [
            {
                xtype: 'glyphactioncolumn',
                width: 25,
                items: [{
                    glyph: NOC.glyph.edit,
                    handler: 'onEdit'
                }]
            }, {
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
            }, {
                text: __("S"),
                dataIndex: "oper_state",
                sortable: false,
                width: 30,
                renderer: function(value, metaData) {
                    var color = "grey";
                    metaData.tdAttr = "data-qtip='<table style=\"font-size: 11px;\">" +
                        "<tr><td style=\"padding-right: 10px;\"><div class=\"noc-object-oper-state\" style=\"background-color: grey;\"></div></td><td>" + __("Unmanaged or ping is disabled") + "</td></tr>" +
                        "<tr><td><div class=\"noc-object-oper-state\" style=\"background-color: red;\"></div></td><td>" + __("Ping fail") + "</td></tr>" +
                        "<tr><td><div class=\"noc-object-oper-state\" style=\"background-color: yellow;\"></div></td><td>" + __("Device has alarm") + "</td></tr>" +
                        "<tr><td><div class=\"noc-object-oper-state\" style=\"background-color: green;\"></div></td><td>" + __("Device is normal") + "</td></tr>" +
                        "</table>'";
                    if(value === "failed") {
                        color = "red";
                    } else if(value === "degraded") {
                        color = "yellow";
                    } else if(value === "full") {
                        color = "green";
                    }
                    return "<div class='noc-object-oper-state' style='background-color: " + color + "'></div>";
                }
            }, {
                text: __('Managed'),
                dataIndex: 'is_managed',
                width: 30,
                renderer: NOC.render.Bool
            }, {
                text: __('Obj. Profile'),
                dataIndex: 'object_profile',
                flex: 1
            }, {
                text: __('Adm. Domain'),
                dataIndex: 'administrative_domain',
                flex: 1
            }, {
                text: __('Auth Profile'),
                dataIndex: 'auth_profile',
                flex: 1
            }, {
                text: __('VRF'),
                dataIndex: 'vrf',
                flex: 1
            }, {
                text: __('Pool'),
                dataIndex: 'pool',
                flex: 1
            }, {
                text: __('Description'),
                dataIndex: 'description',
                flex: 1
            }, {
                text: __('Interfaces'),
                dataIndex: 'interface_count',
                width: 50,
                sortable: false,
                align: "right",
                renderer: this.renderClickableCell
            }, {
                text: __('Links'),
                dataIndex: 'link_count',
                width: 50,
                sortable: false,
                align: "right",
                cls: "noc-clickable-cell",
                renderer: this.renderClickableCell
            }, {
                text: __('Labels'),
                dataIndex: 'labels',
                renderer: NOC.render.LabelField,
                align: "right",
                width: 100
            }, {
                xtype: 'glyphactioncolumn',
                width: 25,
                items: [{
                    glyph: NOC.glyph.cart_plus,
                    handler: 'onAddObject'
                }]
            }
        ];
        var action = this.getView().noc.cmd;
        if(action && action.args && action.args.length >= 1) {
            this.editManagedObject(undefined, action.args[0], action.args[1]);
        }
        app.setActiveItem(0);
        // page 1 init selection grid
        Ext.Array.each(defaultCols, function(col, index) {
            selectionGrid.headerCt.insert(index + 1, col);
        });
        selectionGrid.getView().refresh();
        // page 1 init selected grid
        Ext.Array.each([{
            xtype: 'glyphactioncolumn',
            width: 25,
            items: [{
                glyph: NOC.glyph.minus_circle,
                handler: 'onRemoveObject'
            }]
        }].concat(defaultCols), function(col, index) {
            selectedGrid1.headerCt.insert(index + 1, col);
        });
        selectedGrid1.getView().refresh();
        // page 2 init selected grid
        Ext.Array.each(defaultCols.concat([{
            xtype: 'glyphactioncolumn',
            width: 25,
            items: [{
                glyph: NOC.glyph.minus_circle,
                handler: 'onRemoveObject'
            }]
        }]), function(col, index) {
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

        app.lookupReference('filterPanel').appId = 'sa.managedobject';
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
        this.lookupReference('filterPanel').toggleCollapse();
    },
    //
    toggleBasket: function() {
        this.lookupReference('saManagedobjectSelectedGrid1').toggleCollapse();
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
        this.lookupReference('saManagedobjectSelectionGrid').getStore().reload();
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
    onSelectionSelectAll: function(combo, record) {
        var selectionGrid, renderPlugin, rows;

        switch(record.get('cmd')) {
            case 'SCREEN': {
                selectionGrid = this.lookupReference('saManagedobjectSelectionGrid');
                renderPlugin = selectionGrid.findPlugin('bufferedrenderer');
                selectionGrid.getSelectionModel().selectRange(0, renderPlugin.getLastVisibleRowIndex());
                this.lookupReference('saManagedobjectSelectedGrid1').getStore().loadData(
                    this.lookupReference('saManagedobjectSelectionGrid').getSelection()
                );
                return;
            }
            case 'N_ROWS': {
                Ext.Msg.prompt(__('Select rows'), __('Please enter number:'), function(btn, text) {
                    if(btn === 'ok') {
                        this.getNRows('0', text);
                    }
                }, this);
                break;
            }
            case 'PERIOD': {
                Ext.Msg.prompt(__('Select period'), __('Please enter period (start,qty), first pos is 0:'), function(btn, text) {
                    if(btn === 'ok') {
                        this.getNRows(text.split(',')[0], text.split(',')[1]);
                    }
                }, this);
                break;
            }
            default: {
                this.getNRows('0', record.get('cmd').slice(6));
            }
        }
        combo.setValue(null);
    },
    //
    onSelectionUnselectAll: function() {
        this.lookupReference('saManagedobjectSelectionGrid').getSelectionModel().deselectAll();
    },
    //
    onSelectionAddChecked: function() {
        this.lookupReference('saManagedobjectSelectedGrid1').getStore().add(
            this.lookupReference('saManagedobjectSelectionGrid').getSelection()
        );
        this.getViewModel().set('total.selected', this.getStore('selectedStore').getCount());
    },
    //
    onSelectedRemoveChecked: function() {
        var selectedGrid = this.lookupReference('saManagedobjectSelectedGrid1');

        selectedGrid.getStore().remove(
            selectedGrid.getSelectionModel().getSelection()
        );
    },
    //
    onSelectedRemoveAll: function() {
        this.lookupReference('saManagedobjectSelectedGrid1').getStore().removeAll();
    },
    //
    onSelectedDblClick: function(grid, record, item, rowIndex) {
        this.lookupReference('saManagedobjectSelectedGrid1').getStore().removeAt(rowIndex);
    },
    //
    onConfigModeChange: function(field, mode) {
        var commandForm = this.lookupReference('saManagedobjectCommandForm');

        commandForm.removeAll();
        switch(mode) {
            case 'action': {
                commandForm.add({
                    xclass: 'NOC.sa.action.LookupField',
                    reference: 'sa-managedobject-action-field',
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
                    reference: 'sa-managedobject-snippet-field',
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
                    reference: 'saManagedobjectCommandField',
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
        var mode = this.lookupReference('saManagedobjectMode').getValue();
        var makeRequest = function(mode) {
            var objects = [];
            var config = me.lookupReference('saManagedobjectCommandForm').getValues();
            var ignore_cli_errors = JSON.stringify(me.lookupReference('ignoreCliErrors').getValue());

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
                                    include_commands: true,
                                    ignore_cli_errors: ignore_cli_errors
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
        this.lookupReference('saManagedobjectSelectedGrid3').getSelectionModel().deselectAll();
        this.getViewModel().set('resultOutput', '');

        switch(mode) {
            case 'commands': {
                this.sendCommands('commands', {
                    'script': 'commands',
                    'args': {
                        'commands': this.lookupReference('saManagedobjectCommandForm').getValues().cmd.split('\n'),
                        'include_commands': 'true',
                        'ignore_cli_errors': JSON.stringify(this.lookupReference('ignoreCliErrors').getValue())
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
        this.lookupReference('saRunCommandReportPanel').setHtml(this.buildReport());
        this.toNext();
    },
    //
    onShowResult: function(grid, record) {
        var acc = [];

        if(record.get('result')) {
            this.makeReportRow(record, acc);
        }
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
    toMain: function() {
        this.navigate(0, true);
    },
    //
    // Private function
    //
    navigate: function(inc, absolute) {
        var l = this.getView().getLayout();
        var i = l.activeItem.activeItem;
        var activeItem = parseInt(i, 10);
        var activate = activeItem + inc;

        if(absolute) {
            activate = inc;
        }
        l.setActiveItem(activate);
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
                    var commandForm = me.lookupReference('saManagedobjectCommandForm');

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
        xhr.setRequestHeader('Content-Type', 'application/json');
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

        this.getStore('selectedStore').each(function(record) {
            if(record.get('result')) {
                this.makeReportRow(record, r);
            }
        }, this);
        return r.join('\n');
    },
    //
    makeReportRow: function(record, ac) {
        var result = record.get('result');
        var text = '<b>#</b> ' + result + '<br/>';

        if(Ext.isFunction(result.map)) {
            text = result.map(function(e) {
                return '<b>#</b> ' + e;
            }).join('<br/>');
        }
        ac.push('<div class=\'noc-mrt-section\'>' + record.get('name') + '(' + record.get('address') + ')</div>');
        ac.push('<div class=\'noc-mrt-result\'>' + text + '</div>');
    },
    //
    getNRows: function(m, n) {
        var params, me = this,
            selectionGrid = this.lookupReference('saManagedobjectSelectionGrid'),
            limit = Number.parseInt(n),
            start = Number.parseInt(m);
        if(Number.isInteger(limit) && Number.isInteger(start)) {
            params = Ext.Object.merge(
                {},
                Ext.clone(this.lookupReference('saManagedobjectSelectionGrid').getStore().filterParams),
                {
                    __limit: limit,
                    __start: start
                }
            );

            selectionGrid.mask(__('Loading'));
            Ext.Ajax.request({
                url: this.lookupReference('saManagedobjectSelectionGrid').getStore().rest_url,
                method: 'POST',
                jsonData: params,
                scope: me,
                success: function(response) {
                    var params = Ext.decode(response.request.requestOptions.data);
                    selectionGrid.unmask();
                    selectionGrid.getSelectionModel().selectRange(params.__start, params.__start + params.__limit - 1);
                    me.lookupReference('saManagedobjectSelectedGrid1').getStore()
                        .insert(0, Ext.decode(response.responseText));
                },
                failure: function() {
                    selectionGrid.unmask();
                    NOC.error(__("Failed to get data"));
                }
            });

        }
    },
    //
    onDownload: function() {
        var text = $($.parseHTML(this.lookupReference('saRunCommandReportPanel').html)).text(),
            blob = new Blob([text], {type: "text/plain;charset=utf-8"});
        saveAs(blob, 'result.txt');
    },
    onEdit: function(gridView, rowIndex, colIndex, item, e, record) {
        this.editManagedObject(gridView.up('[itemId=sa-managedobject]'), record.id);
    },
    //
    onNewRecord: function() {
        var view = this.getView();
        view.down('[itemId=managedobject-form-panel]').getController().onNewRecord();
        view.getLayout().setActiveItem('managedobject-form');
    },
    editManagedObject: function(gridView, id, suffix) {
        var url = '/sa/managedobject/' + id + '/',
            view = this.getView();

        if(gridView) {
            gridView.mask(__("Loading ..."));
        }
        Ext.Ajax.request({
            url: url,
            method: 'GET',
            scope: this,
            success: function(response) {
                if(response.status === 200) {
                    var field,
                        formPanel,
                        form,
                        r = {},
                        data = Ext.decode(response.responseText),
                        record = Ext.create("NOC.sa.managedobject.Model", data);

                    if(!gridView) { // restore by url
                        gridView = this.getView();
                    }
                    record.set('id', id);
                    formPanel = gridView.down('[itemId=managedobject-form-panel]');
                    formView = formPanel.up();
                    formPanel.recordId = id;
                    formPanel.currentRecord = record;
                    form = formPanel.getForm();
                    Ext.iterate(data, function(v) {
                        if(v.indexOf("__") !== -1) {
                            return
                        }
                        field = form.findField(v);
                        if(!field) {
                            return;
                        }
                        // hack to get instance of .TreeCombo class
                        if(Ext.String.endsWith(field.xtype, '.TreeCombo')) {
                            field[0].restoreById(data[v]);
                            return;
                        }
                        if(Ext.isFunction(field.cleanValue)) {
                            r[v] = field.cleanValue(
                                field.store.getModel().create({[v]: data[v], [v + "__label"]: data[v + "__label"]}),
                                field.store.rest_url
                            )
                            return;
                        }
                        if(!Ext.isEmpty(data[v])) {
                            r[v] = data[v];
                        }
                    });
                    // 
                    form.reset();
                    form.setValues(r);
                    this.loadInlineStore(formPanel, data.id);
                    view.setHistoryHash(data.id);
                    view.getLayout().setActiveItem('managedobject-form').down().setActiveItem('managedobject-form-panel');
                    if(suffix) {
                        formView.getController().itemPreview('sa-' + suffix);
                    }
                    this.setFormTitle(formView.changeTitle, data.id);
                    this.showMapHandler(record);
                }
                if(gridView) {
                    gridView.unmask();
                }
                this.buttonState();
            },
            failure: function() {
                if(gridView) {
                    gridView.unmask();
                }
                NOC.error(__("Failed get MO detail"));
            }
        });
    },
    // Set edit form title
    setFormTitle: function(tpl, itemId) {
        var t = "<b>" + Ext.String.format(tpl, this.view.appTitle) + "</b>",
            formTitle = this.view.down('[itemId=formTitle]');
        if(itemId !== "NEW" && itemId !== "CLONE") {
            itemId = "<b>ID:</b>" + itemId;
        } else {
            itemId = "<b>" + itemId + "</b>";
        }
        t += "<span style='float:right'>" + itemId + "</span>";
        formTitle.update(t);
    },
    resetInlineStore: function(formPanel, defaults) {
        Ext.each(formPanel.query("[itemId$=-inline]"),
            function(gridField) {
                var store = gridField.getStore(),
                    value = [];
                if(!store) {
                    store = new Ext.create("NOC.core.InlineModelStore", {
                        model: gridField.model
                    });
                    gridField.setStore(store);
                }
                if(store.hasOwnProperty("rootProperty") && this.hasOwnProperty(store.rootProperty)) {
                    value = this[store.rootProperty];
                }
                store.loadData(value);
            }, defaults || {});
    },
    loadInlineStore(formPanel, id) {
        Ext.each(formPanel.query("[itemId$=-inline]"),
            function(gridField) {
                var store = new Ext.create("NOC.core.InlineModelStore", {
                    model: gridField.model
                });
                gridField.setStore(store);
                store.setParent(id);
                store.load();
            }, this);
    },
    buttonState: function() {
        var view = this.getView(),
            cloneBtn = view.down('[itemId=cloneBtn]'),
            saveBtn = view.down('[itemId=saveBtn]'),
            deleteBtn = view.down('[itemId=deleteBtn]'),
            createBtn = view.down('[itemId=createBtn]');

        saveBtn.setDisabled(!view.hasPermission("update"));
        saveBtn.formBind = view.hasPermission("update");
        cloneBtn.setDisabled(!view.hasPermission("create"));
        deleteBtn.setDisabled(!view.hasPermission("delete"));
        createBtn.setDisabled(!view.hasPermission("create"));
    },
    showMapHandler: function(record) {
        Ext.Ajax.request({
            url: "/sa/managedobject/" + record.get("id") + "/map_lookup/",
            method: "GET",
            scope: this,
            success: function(response) {
                var me = this,
                    defaultHandler, menu,
                    showMapBtn = this.getView().down('[itemId=showMapBtn]'),
                    data = Ext.decode(response.responseText);

                defaultHandler = data.filter(function(el) {
                    return el.is_default
                })[0];
                showMapBtn.setHandler(function() {
                    NOC.launch("inv.map", "history", {
                        args: defaultHandler.args
                    });
                }, me);
                showMapBtn.setMenu(
                    data.filter(function(el) {
                        return !el.is_default
                    }).map(function(el) {
                        return {
                            text: el.label,
                            handler: function() {
                                NOC.launch("inv.map", "history", {
                                    args: el.args
                                })
                            }
                        }
                    })
                );
            },
            failure: function() {
                NOC.error(__("Show Map Button : Failed to get data"));
            }
        });
    },
    onCellClick: function(self, td, cellIndex, record) {
        this.editManagedObject(undefined, record.id, self.getGridColumns()[cellIndex].dataIndex);
    },
    renderClickableCell: function(value, metaData) {
        metaData.tdStyle = "text-decoration-line: underline;cursor: pointer;";
        return value;
    },
});
