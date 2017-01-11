//---------------------------------------------------------------------
// NOC.core.ModelApplication
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ModelApplication");

Ext.define("NOC.core.ModelApplication", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.core.ModelStore",
        "NOC.core.InlineModelStore"
    ],
    mixins: [
        "NOC.core.Export"
    ],

    layout: "card",
    search: false,
    filters: null,
    gridToolbar: [],  // Additional grid toolbar buttons
    formToolbar: [],  // Additional form toolbar buttons
    currentRecord: null,
    appTitle: null,
    createTitle: __("Create") + " {0}",
    cloneTitle: __("Clone") + " {0}",
    changeTitle: __("Change") + " {0}",
    groupChangeTitle: __("Change") + " {0} {1}",
    rowClassField: undefined,
    actions: undefined,
    previewIcon: "icon_magnifier",
    preview: null,
    treeFilter: null,
    formLayout: "anchor",
    //
    initComponent: function() {
        var me = this;
        // set base_url
        var n = me.self.getName().split(".");
        me.base_url = "/" + n[1] + "/" + n[2] + "/";
        me.appName = n[1] + "." + n[2];
        // Variables
        me.currentQuery = {};
        // Create store
        var bs = Math.ceil(screen.height / 24);
        me.store = Ext.create("NOC.core.ModelStore", {
            model: me.model,
            customFields: me.noc.cust_model_fields || [],
            autoLoad: false,
            pageSize: bs,
            leadingBufferZone: bs,
            numFromEdge: Math.ceil(bs / 2),
            trailingBufferZone: bs
        });
        me.store.on("beforeload", me.onBeforeLoad, me);
        me.store.on("load", me.onLoad, me);
        me.store.on("exception", me.onLoadError, me);

        me.idField = me.store.idProperty;
        // Generate persistent field names
        me.persistentFields = {};
        Ext.each(me.store.model.getFields(), function(f) {
            if(f.persist) {
                me.persistentFields[f.name] = true;
            }
        });
        //
        me.hasGroupEdit = me.checkGroupEdit();
        // Create GRID card
        me.ITEM_GRID = me.registerItem(me.createGrid());
        // Create FORM card
        me.ITEM_FORM = me.registerItem(me.createForm());
        // Create Group Edit form when necessary
        if(me.hasGroupEdit) {
            me.ITEM_GROUP_FORM = me.registerItem(me.createGroupForm())
        }
        //
        Ext.apply(me, {
            items: me.getRegisteredItems(),
            activeItem: me.ITEM_GRID
        });
        // Initialize component
        me.callParent();
        me.currentRecord = null;
        // Process commands
        switch(me.getCmd()) {
            case "open":
                me.loadById(me.noc.cmd.id);
                break;
            case "history":
                me.restoreHistory(me.noc.cmd.args);
                return;
                break;
            case "new":
                me.newRecord(me.noc.cmd.args);
                break;
        }
        // Finally, load the store
        me.store.load();
    },
    //
    createGrid: function() {
        var me = this;
        // Setup Grid toolbar
        var gridToolbar = [];

        me.searchField = Ext.create("Ext.ux.form.SearchField", {
            name: "search_field",
            hideLabel: true,
            width: 400,
            typeAhead: true,
            typeAheadDelay: 500,
            hasAccess: function(app) { return app.search === true;},
            scope: me,
            handler: me.onSearch
        });

        me.refreshButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.refresh,
            tooltip: __("Refresh"),
            scope: me,
            handler: me.onRefresh
        });

        me.createButton = Ext.create("Ext.button.Button", {
            itemId: "create",
            text: __("Add"),
            glyph: NOC.glyph.plus,
            tooltip: __("Add new record"),
            hasAccess: NOC.hasPermission("create"),
            scope: me,
            handler: me.onNewRecord
        });

        me.exportButton = Ext.create("Ext.button.Button", {
            itemId: "export",
            text: __("Export"),
            glyph: NOC.glyph.arrow_down,
            tooltip: __("Save screen"),
            scope: me,
            handler: function() {
                this.save(this.grid, "managed_objects.csv");
            }
    });

        gridToolbar.push(me.searchField, me.refreshButton, me.createButton, me.exportButton);
        // admin actions
        if(me.actions || me.hasGroupEdit) {
            gridToolbar.push(me.createActionMenu());
        }
        gridToolbar = gridToolbar.concat(me.gridToolbar);
        gridToolbar.push("->");
        me.totalField = Ext.create("Ext.form.field.Display");
        gridToolbar.push(me.totalField);
        // Initialize panels
        // Filters
        var grid_rbar = null;
        me.filterGetters = [];
        me.filterSetters = [];
        if(me.filters) {
            var fh = Ext.bind(me.onFilter, me),
                filters = [{
                    title: __("Favorites"),
                    name: "fav_status",
                    ftype: "favorites"
                }].concat(me.filters);
            grid_rbar = {
                xtype: "form",
                autoScroll: true,
                itemId: "filters",
                width: 208,
                title: __("Filter"),
                padding: 4,
                tools: [
                    {
                        type: "close",
                        tooltip: __("Reset filters"),
                        scope: me,
                        handler: me.onResetFilters
                    }
                ],
                items: filters.map(function(f) {
                    // @todo: Smarter solution using Ext.Class.alias
                    var ft = {
                        boolean: "NOC.core.modelfilter.Boolean",
                        choices: "NOC.core.modelfilter.Choices",
                        lookup: "NOC.core.modelfilter.Lookup",
                        vcfilter: "NOC.core.modelfilter.VCFilter",
                        afi: "NOC.core.modelfilter.AFI",
                        vc: "NOC.core.modelfilter.VC",
                        tag: "NOC.core.modelfilter.Tag",
                        favorites: "NOC.core.modelfilter.Favorites",
                        tree: "NOC.core.modelfilter.Tree"
                    }[f.ftype];
                    var fc = Ext.Object.merge(f, {
                        referrer: me.appName
                    });
                    var fg = Ext.create(ft, fc);
                    fg.handler = fh;
                    me.filterGetters = me.filterGetters.concat(
                        Ext.bind(fg.getFilter, fg)
                    );
                    me.filterSetters = me.filterSetters.concat(
                        Ext.bind(fg.setFilter, fg)
                    );
                    return fg;
                })
            };
        }
        // Grid
        var cust_columns = me.noc.cust_grid_columns || [];
        Ext.each(cust_columns, function(c) {
            if(c.renderer && Ext.isString(c.renderer)) {
                c.renderer = eval(c.renderer);
            }
        });
        var selModel = Ext.create("Ext.selection.CheckboxModel", {
            preventFocus: true
        });
        if(me.actions) {
            selModel.on("selectionchange", me.onActionSelectionChange, me);
        }

        var rowItems = [
            {
                glyph: NOC.glyph.star,
                tooltip: __("Mark/Unmark"),
                scope: me,
                getColor: function(cls, meta, r) {
                    return r.get("fav_status") ? NOC.colors.starred : NOC.colors.unstarred;
                },
                handler: me.onFavItem
            },
            {
                glyph: NOC.glyph.edit,
                color: NOC.colors.edit,
                tooltip: __("Edit"),
                scope: me,
                handler: function(grid, rowIndex, colIndex) {
                    var me = this,
                        record = me.store.getAt(rowIndex);
                    me.onEditRecord(record);
                }
            }
        ];

        if(me.dashboardIcon){
            rowItems = rowItems.concat([
                {
                    glyph: NOC.glyph.line_chart,
                    tooltip: __("Show dashboard"),
                    scope: me,
                    handler: function(grid, rowIndex) {
                        var me = this,
                            record = me.store.getAt(rowIndex);

                        window.open(
                            '/ui/grafana/dashboard/script/noc.js?dashboard=ipsla&id=' + record.id
                        );
                    }
                }
            ]);
        }
        // @todo: Replace with preview api
        if(me.onPreview) {
            rowItems = rowItems.concat([
                {
                    glyph: NOC.glyph.search,
                    color: NOC.colors.preview,
                    tooltip: __("Preview"),
                    scope: me,
                    handler: function(grid, rowIndex, colIndex) {
                        var me = this;
                        me.onPreview(me.store.getAt(rowIndex));
                    }
                }
            ]);
        }
        if(me.preview) {
            // @todo: Detect panel instances
            var config = {
                app: me,
                xtype: "Ext.panel.Panel"
            };
            Ext.apply(config, me.preview);
            me.ITEM_PREVIEW = me.registerItem(
                Ext.create(config.xtype, config)
            );
            rowItems = rowItems.concat([
                {
                    glyph: NOC.glyph.search,
                    color: NOC.colors.preview,
                    tooltip: __("Preview"),
                    scope: me,
                    handler: function(grid, rowIndex, colIndex) {
                        var me = this;
                        me.showPreview(me.store.getAt(rowIndex));
                    }
                }
            ]);
        }

        var gridColumns = me.columns.concat(cust_columns);
        // Set up tooltips
        Ext.each(gridColumns, function(c) {
            if(!c.listeners) {
                c.listeners = {};
            }
            c.listeners.afterrender = function() {
                Ext.create("Ext.ToolTip", {
                    target: this.getEl(),
                    anchor: "top",
                    trackMouse: true,
                    html: this.tooltip || this.text
                });
            }
        });
        //
        var gridToolbars = [
            {
                xtype: "toolbar",
                items: me.applyPermissions(gridToolbar)
            }
        ];
        //
        if(me.treeFilter) {
            var treeFilterToolbar = Ext.create("NOC.core.TreeFilterToolbar", {
                field: me.treeFilter,
                url: me.base_url + "tree_lookup/",
                listeners: {
                    scope: me,
                    select: me.onFilter
                }
            });
            gridToolbars.push(treeFilterToolbar);
            me.filterGetters.push(
                Ext.bind(treeFilterToolbar.getFilter, treeFilterToolbar)
            );
        }
        //
        var gridPanel = Ext.create("Ext.grid.Panel", {
            itemId: "grid",
            store: me.store,
            columns: [
                {
                    xtype: "glyphactioncolumn",
                    width: 20 * rowItems.length,
                    sortable: false,
                    items: rowItems,
                    stateId: "rowaction"
                },
                {
                    text: __("ID"),
                    dataIndex: me.idField,
                    hidden: true
                }
            ].concat(gridColumns),
            border: false,
            autoScroll: true,
            stateful: true,
            stateId: me.appName + "-grid",
            plugins: [
            //     {
            //         ptype: "bufferedrenderer"
            //         //trailingBufferZone: 50,
            //         //leadingBufferZone: 50
            //     }
            ],
            selModel: selModel,
            dockedItems: gridToolbars,
            rbar: grid_rbar,
            viewConfig: {
                enableTextSelection: true,
                getRowClass: Ext.bind(me.getRowClass, me),
                listeners: {
                    scope: me,
                    cellclick: me.onCellClick
                }
            },
            listeners: {
                scope: me,
                itemdblclick: function(grid, record) {
                    this.onEditRecord(record);
                }
            }
        });
        // Shortcuts
        me.grid = gridPanel;
        if(me.filters) {
            me.filterPanel = me.grid.getComponent("filters");
        }
        return gridPanel;
    },
    //
    createForm: function() {
        var me = this,
            focusField = null,
            autoFocusFields;
        //
        me.saveButton = Ext.create("Ext.button.Button", {
            itemId: "save",
            text: __("Save"),
            tooltip: __("Save changes"),
            glyph: NOC.glyph.save,
            formBind: true,
            disabled: true,
            scope: me,
            // @todo: check access
            handler: me.onSave
        });
        //
        me.closeButton = Ext.create("Ext.button.Button", {
            itemId: "close",
            text: __("Close"),
            tooltip: __("Close without saving"),
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose
        });
        //
        me.resetButton = Ext.create("Ext.button.Button", {
            itemId: "reset",
            text: __("Reset"),
            tooltip: __("Reset to default values"),
            glyph: NOC.glyph.undo,
            disabled: true,
            scope: me,
            handler: me.onReset
        });
        //
        me.deleteButton = Ext.create("Ext.button.Button", {
            itemId: "delete",
            text: __("Delete"),
            tooltip: __("Delete object"),
            glyph: NOC.glyph.times,
            disabled: true,
            hasAccess: NOC.hasPermission("delete"),
            scope: me,
            handler: me.onDelete
        });
        //
        me.cloneButton = Ext.create("Ext.button.Button", {
            itemId: "clone",
            text: __("Clone"),
            tooltip: __("Copy existing values to a new object"),
            glyph: NOC.glyph.copy,
            disabled: true,
            hasAccess: NOC.hasPermission("create"),
            scope: me,
            handler: me.onClone
        });
        // Default toolbar items
        var formToolbar = [
            me.saveButton,
            me.closeButton,
            "-",
            me.resetButton,
            me.deleteButton,
            "-",
            me.cloneButton
        ];
        // Add View button
        if(me.onPreview) {
            formToolbar.push({
                text: __("View"),
                tooltip: __("Preview"),
                glyph: NOC.glyph.eye,
                // hasAccess:
                scope: me,
                handler: function() {
                    var me = this;
                    me.onPreview(me.currentRecord)
                }
            });
        }
        if(me.formToolbar && me.formToolbar.length) {
            formToolbar.push("-");
        }
        formToolbar = formToolbar.concat(me.formToolbar);
        // Prepare inlines grid
        var formInlines = [];
        me.inlineStores = [];
        if(me.inlines) {
            for(var i = 0; i < me.inlines.length; i++) {
                var inline = me.inlines[i],
                    istore = Ext.create("NOC.core.InlineModelStore", {
                        model: inline.model
                    }),
                    gp = {
                        xtype: "gridpanel",
                        columns: inline.columns,
                        store: istore,
                        selType: "rowmodel",
                        minHeight: 130,
                        dockedItems : [
                            {
                             xtype: "pagingtoolbar",
                             store: istore,
                             dock: "bottom",
                             displayInfo: true
                            }
                               ],
                        plugins: [
                            Ext.create("Ext.grid.plugin.RowEditing", {
                                clicksToEdit: 2,
                                listeners: {
                                    scope: me,
                                    beforeedit: me.onInlineBeforeEdit,
                                    edit: me.onInlineEdit
                                }
                            })
                        ],
                        tbar: [
                            {
                                text: __("Add"),
                                glyph: NOC.glyph.plus,
                                handler: function() {
                                    var grid = this.up("panel"),
                                        rowEditing = grid.plugins[0];
                                    rowEditing.cancelEdit();
                                    grid.store.insert(0, {});
                                    rowEditing.startEdit(0, 0);
                                }
                            },
                            {
                                text: __("Delete"),
                                glyph: NOC.glyph.times,
                                handler: function() {
                                    var grid = this.up("panel"),
                                        sm = grid.getSelectionModel(),
                                        rowEditing = grid.plugins[0],
                                        app = grid.up("panel").up("panel");
                                    rowEditing.cancelEdit();
                                    grid.store.remove(sm.getSelection());
                                    if(grid.store.getCount() > 0) {
                                        sm.select(0);
                                    }
                                    app.onInlineEdit();
                                }
                            }
                        ],
                        listeners: {
                            validateedit: function(editor, e) {
                                // @todo: Bring to plugin
                                var form = editor.editor.getForm();
                                // Process comboboxes
                                form.getFields().each(function(field) {
                                    e.record.set(field.name, field.getValue());
                                    if(Ext.isDefined(field.getLookupData))
                                        e.record.set(field.name + "__label",
                                                     field.getLookupData());
                                    });
                            }
                        }
                    };
                formInlines.push({
                    xtype: "fieldset",
                    anchor: "100%",
                    minHeight: 130,
                    title: inline.title,
                    collapsible: true,
                    items: [gp]
                });
                me.inlineStores.push(istore);
            }
        }

        me.formTitle = Ext.create("Ext.container.Container", {
            html: "Title",
            itemId: "form_title",
            padding: "0 0 4 0"
        });
        // Build form fields
        var formFields = [me.formTitle];
        // Append configured fields
        formFields = formFields.concat(me.fields);
        // Append custom fields
        if(me.noc.cust_form_fields) {
            formFields = formFields.concat(me.noc.cust_form_fields);
        }
        formFields = formFields.concat(formInlines);

        me.formPanel = Ext.create("Ext.container.Container", {
            itemId: "form",
            layout: "fit",
            items: {
                xtype: 'form',
                layout: me.formLayout,
                border: true,
                padding: 4,
                bodyPadding: 4,
                autoScroll: true,
                defaults: {
                    anchor: "100%",
                    enableKeyEvents: true,
                    listeners: {
                        specialkey: {
                            scope: me,
                            fn: me.onFormSpecialKey
                        }
                    }
                },
                items: formFields,
                dockedItems: {
                    xtype: "toolbar",
                    dock: "top",
                    layout: {
                        overflowHandler: "Menu"
                    },
                    items: me.applyPermissions(formToolbar)
                }
            },
            getDefaultFocus: function() {
                return focusField;
            }
        });
        me.form = me.formPanel.items.first().getForm();
        // detect autofocus field
        autoFocusFields = Ext.ComponentQuery.query("[autoFocus=true]", me.formPanel);
        if(autoFocusFields && autoFocusFields.length > 0) {
            focusField = autoFocusFields[0];
        } else {
            focusField = me.form.getFields().items[1];
        }
        me.restoreFilter(me.noc.filterValuesUrl);
        return me.formPanel;
    },
    // Show grid
    showGrid: function() {
        var me = this;
        me.showItem(me.ITEM_GRID);
        me.setHistoryHash();
    },
    // Show Form
    showForm: function() {
        var me = this;
        me.showItem(me.ITEM_FORM);
        if(me.formPanel && me.formPanel.getDefaultFocus) {
            var df = me.formPanel.getDefaultFocus();
            if(df) {
                df.focus();
            }
        }
    },
    //
    showPreview: function(record) {
        var me = this,
            item = me.showItem(me.ITEM_PREVIEW);
        if(item !== undefined) {
            item.preview(record, me.ITEM_GRID);
        }
    },
    // Save changed data
    saveRecord: function(data) {
        var me = this,
            Model = me.store.getModel(),
            record = new Model(data),
            mv = record.validate(),
            result = {};

        if(!mv.isValid()) {
            // @todo: Error report
            NOC.error(__("Invalid data!"));
            return;
        }
        // Normalize
        data = record.getData();
        for(var name in data) {
            if(me.persistentFields[name]) {
                result[name] = data[name];
            }
        }
        if(me.currentRecord) {
            result[me.idField] = me.currentRecord.get(me.idField);
        }
        me.mask("Saving ...");
        // Save data
        Ext.Ajax.request({
            url: me.base_url + (me.currentRecord ? result[me.idField] + "/" : ""),
            method: me.currentRecord ? "PUT" : "POST",
            scope: me,
            jsonData: result,
            success: function(response) {
                    // Process result
                    var data = Ext.decode(response.responseText);
                    // @todo: Update current record with data
                    if(me.currentQuery[me.idField]) {
                        delete me.currentQuery[me.idField];
                    }
                    me.showGrid();
                    me.reloadStore();
                    me.saveInlines(data[me.idField], me.inlineStores);
                    me.unmask();
                    NOC.msg.complete(__("Saved"));
            },
            failure: function(response) {
                var message = "Error saving record";
                if(response.responseText) {
                    try {
                        message = Ext.decode(response.responseText).message;
                    }
                    catch(err) {
                        console.log(response.responseText);
                    }
                }
                NOC.error(message);
                me.unmask();
            }
        });
    },
    //
    saveInlines: function(parentId, stores) {
        var me = this;
        if(stores.length > 0) {
            var istore = stores[0];
            if(parentId) {
                istore.setParent(parentId);
            }
            // Save inline
            istore.sync({
                scope: me,
                success: function() {
                    // Save next
                    me.saveInlines(parentId, stores.slice(1));
                },
                failure: function(response, op, status) {
                    me.showOpError("save", op, status);
                }
            });
        } else {
            me.showGrid();
        }
    },
    // Show Form
    onEditRecord: function(record) {
        var me = this;
        // Check permissions
        if (!me.hasPermission("read") && !me.hasPermission("update"))
            return;
        me.editRecord(record);
    },
    // New record. Hide grid and open form
    newRecord: function(defaults) {
        var me = this,
            fv = {};
        me.form.reset();
        // Calculate form field values
        Ext.merge(fv, me.store.defaultValues);
        Ext.merge(fv, defaults || {});
        me.form.setValues(fv);
        //
        me.currentRecord = null;
        me.resetInlines();
        me.setFormTitle(me.createTitle, "NEW");
        me.showForm();
        // Activate delete button
        me.deleteButton.setDisabled(true);
        me.saveButton.setDisabled(!me.hasPermission("create"));
        me.resetButton.setDisabled(!me.hasPermission("create"));
        me.cloneButton.setDisabled(true);
        // Disable custom form toolbar
        me.activateCustomFormToolbar(false);
    },
    //
    onNewRecord: function() {
        var me = this;
        me.newRecord();
    },
    // Edit record. Hide grid and open form
    editRecord: function(record) {
        var me = this,
            r = {},
            mv,
            field,
            data,
            isLookupValue = function(name) {
                return name.indexOf("__label", name.length - 7) !== -1;
            };
        me.currentRecord = record;
        me.setFormTitle(me.changeTitle, me.currentRecord.get(me.idField));
        // Process lookup fields
        data = record.getData();
        Ext.iterate(data, function(v) {
            if(isLookupValue(v)) {
                return;
            }
            field = me.form.findField(v);
            if(!field) {
                return;
            }
            if(field.isLookupField && data[v]) {
                mv = {};
                mv[field.valueField] = data[v];
                mv[field.displayField] = data[v + "__label"] || data[v];
                r[v] = field.store.getModel().create(mv);
            } else {
                r[v] = data[v];
            }
        });
        // Show edit form
        me.showForm();
        // Load records
        me.form.reset();
        me.form.setValues(r);
        me.loadInlines();
        // Activate delete button
        me.deleteButton.setDisabled(!me.hasPermission("delete"));
        me.saveButton.setDisabled(!me.hasPermission("update"));
        me.resetButton.setDisabled(!me.hasPermission("update"));
        me.cloneButton.setDisabled(!me.hasPermission("create"));
        // Enable custom form toolbar
        me.activateCustomFormToolbar(true);
        //
        me.setHistoryHash(me.currentRecord.get(me.idField));
    },
    // Delete record
    deleteRecord: function() {
        var me = this;
        pollProgress = function(url) {
            Ext.Ajax.request({
                url: url,
                method: "GET",
                scope: me,
                success: onSuccess,
                failure: onFailure
            });
        },
        onSuccess = function(response) {
            if(response.status === 202) {
                // Future in progress
                Ext.Function.defer(
                    pollProgress, 1000, me,
                    [response.getResponseHeader("Location")]
                );
            } else {
                // Process result
                me.currentRecord = null;
                me.reloadStore();
                me.showGrid();
                me.unmask();
            }
        },
        onFailure = function(response) {
            var message;
            try {
                message = Ext.decode(response.responseText).message;
            } catch(err) {
                message = "Internal error";
            }
            NOC.error(message);
            me.unmask();
        };

        me.mask("Deleting ...");
        Ext.Ajax.request({
            url: me.base_url + me.currentRecord.get(me.idField) + "/",
            method: "DELETE",
            scope: me,
            success: onSuccess,
            failure: onFailure
        });
    },
    // Reload store with current query
    reloadStore: function() {
        var me = this;
        me.store.setFilterParams(me.currentQuery);
        me.saveFilterToUrl(me.currentQuery);
        // Reload store
        // ExtJS 5.0.0 WARNING:
        // me.store.reload() sometimes leaves empty grid
        // so we must use load() instead
        me.store.load();
    },
    // Search
    onSearch: function(query) {
        var me = this;
        if(query && query.length > 0) {
            me.currentQuery.__query = query;
        } else {
            delete me.currentQuery.__query;
        }
        me.reloadStore();
    },
    saveFilterToUrl: function(filter) {
        var params = Ext.Object.toQueryString(filter, true)
            , currentHash = Ext.History.getHash()
            , index = currentHash.indexOf('?')
            , app;
        if(index === -1) {
            app = currentHash;
        } else {
            app = currentHash.substr(0, index);
        }
        if(params) {
            Ext.History.add(app + '?' + params);
        } else {
            Ext.History.add(app);
        }
    },
    // Filter
    onFilter: function() {
        var me = this,
            fexp = {};
        Ext.each(me.filterGetters, function(g) {
            fexp = Ext.Object.merge(fexp, g());
        });
        if(me.currentQuery.__query) {
            fexp.__query = me.currentQuery.__query;
        }
        me.currentQuery = fexp;
        me.reloadStore();
    },
    // Returns form data
    getFormData: function() {
        var me = this,
            fields = me.form.getFields().items,
            f, field, data, name,
            fLen = fields.length,
            values = {};
        for(f = 0; f < fLen; f++) {
            field = fields[f];
            if(field.inEditor) {
                // Skip grid inline editors
                // WARNING: Will skip other inline editors
                continue;
            }
            data = field.getModelData();
            if(Ext.isObject(data)) {
                name = field.getName();
                if(data.hasOwnProperty(name)) {
                    values[name] = data[name];
                }
            }
        }
        return values;
    },
    //
    cleanData: function(v) {

    },
    // Save button pressed
    onSave: function() {
        var me = this;
        if(!me.form.isValid()) {
            NOC.error(__("Error in data"));
            return;
        }
        var v = me.getFormData();
        if(!me.currentRecord && v[me.idField] !== undefined) {
            delete v[me.idField];
        }
        //
        me.cleanData(v);
        // Fetch comboboxes labels
        me.form.getFields().each(function(field) {
            if(Ext.isDefined(field.getLookupData)) {
                v[field.name + "__label"] = field.getLookupData();
            }
        });
        me.saveRecord(v);
    },
    // Reset button pressed
    onReset: function() {
        var me = this;
        me.form.reset();
    },
    // Delete button pressed
    onDelete: function() {
        var me = this;
        Ext.Msg.show({
            title: __("Delete record?"),
            msg: __("Do you wish to delete record? This operation cannot be undone!"),
            buttons: Ext.Msg.YESNO,
            icon: Ext.window.MessageBox.QUESTION,
            modal: true,
            fn: function(button) {
                if (button == "yes")
                    me.deleteRecord();
            }
        });
    },
    // Form hotkeys processing
    onFormSpecialKey: function(field, key) {
        var me = this;
        if (field.xtype != "textfield")
            return;
        switch(key.getKey()) {
            case Ext.EventObject.ENTER:
                key.stopEvent();
                me.onSave();
                break;
            case Ext.EventObject.ESC:
                key.stopEvent();
                me.onReset();
                break;
        }
    },
    // Set form title
    setFormTitle: function(tpl, itemId) {
        var me = this,
            t;
        if(me.formTitle) {
            t = "<b>" + Ext.String.format(tpl, me.appTitle) + "</b>";
            if(itemId !== "NEW" && itemId !== "CLONE") {
                itemId = "<b>ID: </b>" + itemId;
            } else {
                itemId = "<b>" + itemId + "</b>";
            }
            t += "<span style='float:right'>" + itemId + "</span>";
            me.formTitle.update(t);
        }
    },
    //
    activateCustomFormToolbar: function(status) {
        var me = this,
            tb = me.saveButton.ownerCt,
            afterSep = false;
        tb.items.each(function(i) {
            if(afterSep) {
                if(i.setDisabled) {
                    i.setDisabled(!status);
                }
            } else {
                if(i.itemId === "custom_sep") {
                    afterSep = true;
                }
            }
        });
    },
    //
    onResetFilters: function() {
        var me = this;
        me.filterPanel.getForm().reset();
        me.onFilter();
    },
    //
    showOpError: function(action, op, status) {
        var text = Ext.String.format("Failed to {0}", action);
        if(status) {
            var m = status.message;
            if (status.status === 400) {
                m = status.traceback;
            }
            text = Ext.String.format("Failed to {0}!<br>{1}",
                action, m);
        }
        NOC.error(text);
    },
    // "close" button pressed
    onClose: function() {
        var me = this,
            toReload = me.idField in me.currentQuery;
        if(toReload) {
            // Remove filter set by loadById
            delete me.currentQuery[me.idField];
        }
        // Apply updated filter
        me.store.setFilterParams(me.currentQuery);
        me.showGrid();
        if(toReload) {
            me.reloadStore();
        }
    },
    // "clone" button pressed
    onClone: function() {
        var me = this;
        // Reset UUID
        if(me.currentRecord && me.currentRecord.get("uuid")) {
            me.currentRecord.set("uuid", null);
            me.form.setValues({uuid: null});
        }
        // Reset parents of inline stores
        Ext.each(me.inlineStores, function(s) {
            s.cloneData();
        });
        me.currentRecord = null;  // Mark record as new
        me.setFormTitle(me.cloneTitle, "CLONE");
        me.cloneButton.setDisabled(true);
    },
    // Return Grid's row classes
    getRowClass: function(record, index, params, store) {
        var me = this;
        if(me.rowClassField) {
            var c = record.get(me.rowClassField);
            if(c) {
                return c;
            } else {
                return "";
            }
        } else {
            return "";
        }
    },
    //
    onCellClick: function(view, cell, cellIndex, record, row,
                          rowIndex, e) {
        var me = this;
        if(e.target.tagName == "A") {
            var header = view.panel.headerCt.getHeaderAtIndex(cellIndex);
            if(header.onClick) {
                header.onClick.apply(me, [record]);
            }
        }
    },
    //
    onFavItem: function(grid, rowIndex, colIndex) {
        var me = this,
            r = me.store.getAt(rowIndex),
            id = r.get(me.idField),
            action = r.get("fav_status") ? "reset" : "set",
            url = me.base_url + "favorites/item/" + id + "/" + action + "/";

        Ext.Ajax.request({
            url: url,
            method: "POST",
            scope: me,
            success: function() {
                // Invert current status
                r.set("fav_status", !r.get("fav_status"));
                grid.refresh();
            }
        });
    },
    //
    resetInlines: function() {
        var me = this;
        Ext.each(me.inlineStores, function(istore) {
            istore.loadData([]);
        });
    },
    // Load inline stores
    loadInlines: function() {
        var me = this;
        // Do not load store on new record
        if(!me.currentRecord || !me.inlineStores.length)
            return;
        var parentId = me.currentRecord.get(me.idField);
        Ext.each(me.inlineStores, function(istore) {
            istore.setParent(parentId);
            istore.load();
        });
    },
    //
    onInlineEdit: function() {
        var me = this;
        if(me.currentRecord) {
            // deprecated method
            // me.currentRecord.setDirty();
        }
    },
    //
    onInlineBeforeEdit: function(editor, context, eOpts) {
        var me = this;
    },
    // Admin action selected
    onAction: function(menu, item, e) {
        var me = this,
            records = me.grid.getSelectionModel().getSelection().map(function(o) {
                return o.get(me.idField)
            });
        if(me.hasGroupEdit && item.itemId === "group_edit") {
            me.showGroupEditForm(records);
            return;
        }
        if(item.form) {
            me.showActionForm(item, records);
        } else {
            me.runAction(item, {ids: records});
        }
    },
    //
    runAction: function(action, params) {
        var me = this;
        Ext.Ajax.request({
            url: me.base_url + "actions/" + action.itemId + "/",
            method: "POST",
            scope: me,
            params: params,
            success: function(response) {
                var r = Ext.decode(response.responseText) || "OK";
                if(action.resultTemplate) {
                    var d = action.resultTemplate.apply(r);
                    Ext.create("Ext.Window", {
                        html: d,
                        width: 600,
                        height: 400,
                        autoScroll: true,
                        layout: "fit",
                        maximizable: true,
                        title: Ext.String.format("Result: {0}", action.text)
                    }).show();
                } else {
                    NOC.info(r);
                }
            },
            failure: function() {
                NOC.error(__("Failed"));
            }
        });
    },
    //
    showActionForm: function(action, records) {
        var me = this,
            w = Ext.create("Ext.Window", {
            modal: true,
            autoShow: true,
            layout: "fit",
            items: [{
                xtype: "form",
                items: action.form
            }],
            title: Ext.String.format("{0} on {1} records",
                action.text,
                records.length),
            buttons: [{
                text: __("Run"),
                glyph: NOC.glyph.play,
                handler: function() {
                    var form = w.items.first().getForm();
                    if(!form.isValid()) {
                        NOC.error(__("Error"));
                        return;
                    }
                    var params = form.getValues();
                    params.ids = records;
                    w.close();
                    me.runAction(action, params);
                }
            }]
        });
    },
    onActionSelectionChange: function(o, selected, opts) {
        var me = this;
        me.actionMenu.setDisabled(!selected.length);
    },
    //
    // Override with
    // onPreview: function(record)
    // to create item preview
    //
    onPreview: undefined,
    //
    // Load record by id and call callback
    // Callback is the function(record)
    //
    loadById: function(id, callback) {
        var me = this,
            fp = {};
        fp[me.idField] = id;
        me.currentQuery[me.idField] = id;
        me.store.setFilterParams(fp);
        me.store.load({
            scope: me,
            callback: function(records, operation, success) {
                if(success && records.length === 1) {
                    Ext.callback(callback, me, [records[0]]);
                }
            }
        });
    },
    //
    restoreHistory: function(args) {
        var me = this;
        if(args.length === 1) {
            me.loadById(args[0], function(record) {
                me.onEditRecord(record);
            });
        }
    },
    //
    onBeforeLoad: function() {
        var me = this;
        if(me.rendered) {
            me.refreshButton.setDisabled(true);
        }
    },
    //
    onLoad: function() {
        var me = this,
            total = me.store.getTotalCount();
        me.totalField.setValue(__("Total: ") + total);
        if(me.rendered) {
            me.refreshButton.setDisabled(false);
        }
    },
    //
    onLoadError: function() {
        var me = this;
        if(me.rendered) {
            me.refreshButton.setDisabled(false);
        }
    },
    //
    onRefresh: function() {
        var me = this;
        me.reloadStore();
    },
    // Returns true if form has at least one groupEdit: true
    checkGroupEdit: function() {
        var me = this,
            check = function(seq) {
                if(!seq) {
                    return false;
                }
                for(var i = 0; i < seq.length; i++) {
                    var v = seq[i];
                    if(!v) {
                        continue;
                    }
                    if(v.groupEdit === true) {
                        return true;
                    }
                    if(v.items && v.items.length && check(v.items)) {
                        return true;
                    }
                }
                return false;
            };
        return NOC.hasPermission("update") && check(me.fields);
    },
    //
    createGroupForm: function() {
        var me = this,
            form,
            getFormItems = function(fields) {
                var items = [];
                Ext.each(fields, function(v) {
                    var x;
                    switch(v.xtype) {
                        case "fieldset":
                        case "container":
                            x = {
                                xtype: v.xtype,
                                title: v.title,
                                items: getFormItems(v.items)
                            };
                            if(v.layout) {
                                x.layout = v.layout;
                            }
                            if(v.defaults) {
                                x.defaults = v.defaults;
                            }
                            if(v.border || v.border === false) {
                                x.border = v.border;
                            }
                            if(v.padding || v.padding === 0) {
                                x.padding = v.padding;
                            }
                            items.push(x);
                            break;
                        case "checkbox":
                        case "checkboxfield":
                            if(v.groupEdit === true) {
                                x = {
                                    xtype: "combobox",
                                    fieldLabel: v.boxLabel,
                                    name: v.name,
                                    store: [
                                        [0, "Leave unchanged"],
                                        [true, "Set"],
                                        [false, "Reset"]
                                    ],
                                    value: 0
                                }
                            } else {
                                x = v.cloneConfig ? v.cloneConfig() : v;
                                if(x.setDisabled) {
                                    x.setDisabled(true);
                                } else {
                                    x.disabled = true;
                                }
                            }
                            items.push(x);
                            me.groupCheckboxFields[v.name] = true;
                            break;
                        default:
                            x = v.cloneConfig ? v.cloneConfig() : v;
                            if(x.setDisabled) {
                                x.setDisabled(x.groupEdit !== true);
                            } else {
                                x.disabled = x.groupEdit !== true;
                            }
                            items.push(x);
                            break;
                    }
                });
                return items;
            };

        me.groupCheckboxFields = {};

        me.groupFormTitle = Ext.create("Ext.container.Container", {
            html: "Title",
            padding: 4,
            style: {
                fontWeight: "bold"
            }
        });

        form = Ext.create("Ext.form.Panel", {
            padding: 4,
            bodyPadding: 4,
            autoScroll: true,
            items: [me.groupFormTitle].concat(getFormItems(me.fields)),
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: __("Save"),
                            glyph: NOC.glyph.save,
                            // formBind: true,
                            // disabled: true,
                            scope: me,
                            // @todo: check access
                            handler: me.onGroupSave
                        },
                        {
                            text: __("Close"),
                            glyph: NOC.glyph.arrow_left,
                            scope: me,
                            handler: me.onGroupClose
                        }
                    ]
                }
            ]
        });
        me.groupForm = form.getForm();
        return form;
    },
    //
    createActionMenu: function() {
        var me = this,
            items = [];
        // Group edit
        if(me.hasGroupEdit) {
            items.push({
                text: __("Group Edit"),
                itemId: "group_edit",
                glyph: NOC.glyph.edit
            });
        }
        // Other items
        if(me.actions) {
            items = items.concat(me.actions.map(function(o) {
                return {
                    text: o.title,
                    itemId: o.action,
                    form: o.form,
                    glyph: o.glyph,
                    resultTemplate: o.resultTemplate
                }
            }));
        }

        me.actionMenu = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.download,
            tooltip: __("Group actions"),
            hasAccess: NOC.hasPermission("update"),
            itemId: "action_menu",
            disabled: true,
            menu: {
                xtype: "menu",
                plain: true,
                items: items,
                listeners: {
                    click: {
                        scope: me,
                        fn: me.onAction
                    }
                }
            }
        });
        return me.actionMenu;
    },
    //
    showGroupEditForm: function(items) {
        var me = this;
        me.groupEditItems = items;
        me.groupFormTitle.update(Ext.String.format(
            me.groupChangeTitle, items.length, me.appTitle
        ));
        me.showItem(me.ITEM_GROUP_FORM);
    },
    //
    onGroupClose: function() {
        var me = this;
        me.showGrid();
    },
    //
    onGroupSave: function() {
        var me = this,
            values;
        // @todo: Form validation
        values = me.groupForm.getValues();
        // Normalize checkboxes and fields
        Ext.Object.each(values, function(v) {
            if((me.groupCheckboxFields[v] && values[v] === 0) || values[v] === "") {
                delete values[v];
            }
        });
        values.ids = me.groupEditItems;
        Ext.Ajax.request({
            url: me.base_url + "actions/group_edit/",
            method: "POST",
            scope: me,
            jsonData: values,
            success: function(response) {
                NOC.info(__("Records has been updated"));
                me.showGrid();
                me.reloadStore();
            },
            failure: function() {
                NOC.error(__("Failed"));
            }
        });
    },
    //
    onMetrics: function(record) {
        var me = this;
        me.showItem(me.ITEM_METRIC_SETTINGS).preview(record);
    },
    //
    restoreFilter: function(currentHash) {
        var me = this,
            filterStr,
            index,
            queryString;

        if(!currentHash) {
            return;
        }

        index = currentHash.indexOf('?');
        if(index !== -1) {
            queryString = currentHash.substr(index + 1);
            filterStr = Ext.Object.fromQueryString(queryString, true);
            Ext.each(me.filterSetters, function(set) {
                set(filterStr);
            });
            if('__query' in filterStr) {
                me.searchField.setValue(filterStr['__query'])
            }
            me.currentQuery = filterStr;
            me.store.setFilterParams(me.currentQuery);
        }
    }
});
