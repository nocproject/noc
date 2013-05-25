//---------------------------------------------------------------------
// NOC.core.ModelApplication
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ModelApplication");

Ext.define("NOC.core.ModelApplication", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.core.ModelStore",
        "NOC.core.InlineModelStore"
    ],
    layout: "fit",
    search: false,
    filters: null,
    gridToolbar: [],  // Additional grid toolbar buttons
    formToolbar: [],  // Additional form toolbar buttons
    currentRecord: null,
    appTitle: null,
    createTitle: "Create {0}",
    changeTitle: "Change {0}",
    rowClassField: undefined,
    actions: undefined,

    initComponent: function() {
        var me = this;
        // set base_url
        var n = this.self.getName().split("."),
            app_name = n[1] + "." + n[2];
        me.base_url = "/" + n[1] + "/" + n[2] + "/";
        // Variables
        me.currentQuery = {};
        // Create store
        me.store = Ext.create("NOC.core.ModelStore", {
            model: me.model,
            customFields: me.noc.cust_model_fields || [],
            autoLoad: false,
            pageSize: 1  // Increased by AutoSize plugin
        });
        // Setup Grid toolbar
        var gridToolbar = [];
        gridToolbar = gridToolbar.concat([
            {
                xtype: "textfield",
                name: "search_field",
                itemId: "search_field",
                emptyText: "Search...",
                inputType: "search",
                hideLabel: true,
                width: 200,
                hasAccess: function(app) { return app.search === true;},
                listeners: {
                    change: {
                        fn: me.onSearch,
                        scope: me,
                        buffer: 200
                    }
                }
            },
            {
                itemId: "create",
                text: "Add",
                iconCls: "icon_add",
                tooltip: "Add new record",
                hasAccess: NOC.hasPermission("create"),
                scope: me,
                handler: me.onNewRecord
            }
        ]);
        // admin actions
        if(me.actions) {
            gridToolbar = gridToolbar.concat([{
                iconCls: "icon_table_go",
                tooltip: "Group actions",
                hasAccess: NOC.hasPermission("update"),
                itemId: "action_menu",
                disabled: true,
                menu: {
                    xtype: "menu",
                    plain: true,
                    items: me.actions.map(function(o) {
                        return {
                            text: o.title,
                            itemId: o.action,
                            form: o.form,
                            resultTemplate: o.resultTemplate
                        }
                    }),
                    listeners: {
                        click: {
                            scope: me,
                            fn: me.onAction
                        }
                    }
                }
            }]);
        }
        gridToolbar = gridToolbar.concat(me.gridToolbar);
        // Initialize panels
        // Filters
        var grid_rbar = null;
        me.filterGetters = [];
        if(me.filters) {
            var fh = Ext.bind(me.onFilter, me),
                filters = [{
                    title: "Favorites",
                    name: "fav_status",
                    ftype: "favorites"
                }].concat(me.filters);
            grid_rbar = {
                xtype: "form",
                itemId: "filters",
                width: 208,
                title: "Filter",
                padding: 4,
                tools: [
                    {
                        type: "close",
                        tooltip: "Reset filters",
                        scope: me,
                        handler: me.onResetFilters
                    }
                ],
                items: filters.map(function(f) {
                    var ft = {
                        boolean: "NOC.core.modelfilter.Boolean",
                        lookup: "NOC.core.modelfilter.Lookup",
                        vcfilter: "NOC.core.modelfilter.VCFilter",
                        afi: "NOC.core.modelfilter.AFI",
                        vc: "NOC.core.modelfilter.VC",
                        tag: "NOC.core.modelfilter.Tag",
                        favorites: "NOC.core.modelfilter.Favorites"
                    }[f.ftype];
                    var fc = Ext.Object.merge(f, {
                        referrer: app_name
                    });
                    var fg = Ext.create(ft, fc);
                    fg.handler = fh;
                    me.filterGetters = me.filterGetters.concat(
                        Ext.bind(fg.getFilter, fg)
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
        var selModel;
        if(me.actions) {
            selModel = Ext.create("Ext.selection.CheckboxModel", {
                listeners: {
                    scope: me,
                    selectionchange: me.onActionSelectionChange
                }
            });
        } else {
            selModel = Ext.create("Ext.selection.CheckboxModel");
        }

        var rowItems = [
            {
                tooltip: "Mark/Unmark",
                scope: me,
                getClass: function(col, meta, r) {
                    return r.get("fav_status") ? "icon_star" : "icon_star_grey";
                },
                handler: me.onFavItem
            },
            {
                iconCls: "icon_page_edit",
                tooltip: "Edit",
                scope: me,
                handler: function(grid, rowIndex, colIndex) {
                    var me = this,
                        record = me.store.getAt(rowIndex);
                    me.onEditRecord(record);
                }
            }
        ];
        if(me.onPreview) {
            rowItems = rowItems.concat([
                {
                    iconCls: "icon_magnifier",
                    tooltip: "Preview",
                    scope: me,
                    handler: function(grid, rowIndex, colIndex) {
                        var me = this;
                        me.onPreview(me.store.getAt(rowIndex));
                    }
                }
            ]);
        }

        var gridPanel = {
            xtype: "gridpanel",
            itemId: "grid",
            store: me.store,
            features: [
                {ftype: "selectable", id: "selectable"}
            ],
            columns: [
                {
                    xtype: "actioncolumn",
                    width: 40,
                    sortable: false,
                    items: rowItems
                }
            ].concat(me.columns).concat(cust_columns),
            border: false,
            autoScroll: true,
            stateful: true,
            stateId: app_name + "-grid",
            plugins: [Ext.create("Ext.ux.grid.AutoSize")],
            selModel: selModel,
            dockedItems: [
                {
                    xtype: "toolbar",
                    items: me.applyPermissions(gridToolbar)
                },
                {
                    xtype: "pagingtoolbar",
                    store: me.store,
                    dock: "bottom",
                    displayInfo: true
                }
            ],
            rbar: grid_rbar,
            viewConfig: {
                getRowClass: Ext.bind(me.getRowClass, me),
                listeners: {
                    scope: me,
                    cellclick: me.onCellClick
                }
            },
            listeners: {
                itemdblclick: {
                    scope: me,
                    fn: function(grid, record) {
                        this.onEditRecord(record);
                    }
                }
            }
        };
        // Form
        var formToolbar = [
            {
                itemId: "save",
                text: "Save",
                iconCls: "icon_disk",
                // formBind: true,
                // disabled: true,
                scope: me,
                // @todo: check access
                handler: me.onSave
            },
            {
                itemId: "close",
                text: "Close",
                iconCls: "icon_arrow_undo",
                scope: me,
                handler: me.onClose
            },
            "-",
            {
               itemId: "reset",
               text: "Reset",
               iconCls: "icon_cancel",
               disabled: true,
               scope: me,
               handler: me.onReset
            },
            {
               itemId: "delete",
               text: "Delete",
               iconCls: "icon_delete",
               disabled: true,
               hasAccess: NOC.hasPermission("delete"),
               scope: me,
               handler: me.onDelete
            },
            "-",
            {
                itemId: "clone",
                text: "Clone",
                iconCls: "icon_page_copy",
                disabled: true,
                hasAccess: NOC.hasPermission("create"),
                scope: me,
                handler: me.onClone
            }
        ];
        // Add View button
        if(me.onPreview) {
            formToolbar = formToolbar.concat([
                {
                    text: "View",
                    iconCls: "icon_magnifier",
                    // hasAccess:
                    scope: me,
                    handler: function() {
                        var me = this;
                        me.onPreview(me.currentRecord)
                    }
                }
            ]);
        }
        me.toolbarIdLabel = Ext.create("Ext.toolbar.TextItem", {
            text: "ID:"
        })
        formToolbar = formToolbar.concat(me.formToolbar);
        formToolbar = formToolbar.concat([
            "->",
            me.toolbarIdLabel
        ]);

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
                                    edit: me.onInlineEdit
                                }
                            })
                        ],
                        tbar: [
                            {
                                text: "Add",
                                iconCls: "icon_add",
                                handler: function() {
                                    var grid = this.up("panel"),
                                        rowEditing = grid.plugins[0];
                                    rowEditing.cancelEdit();
                                    grid.store.insert(0, {});
                                    rowEditing.startEdit(0, 0);
                                }
                            },
                            {
                                text: "Delete",
                                iconCls: "icon_delete",
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
                    },
                    r = {
                        xtype: "fieldset",
                        anchor: "100%",
                        title: inline.title,
                        collapsible: true,
                        items: [gp]
                    }
                formInlines = formInlines.concat(r);
                me.inlineStores = me.inlineStores.concat(istore);
            }
        }
        var formPanel = {
            xtype: 'container',
            itemId: "form",
            layout: "fit",
            items: {
                xtype: 'form',
                border: true,
                padding: 4,
                bodyPadding: 4,
                autoScroll: true,
                defaults: {
                    enableKeyEvents: true,
                    listeners: {
                        specialkey: {
                            scope: me,
                            fn: me.onFormSpecialKey
                        }
                    }
                },
                items: [
                    {
                        xtype: "container",

                        html: "Title",
                        itemId: "form_title",
                        padding: 4,
                        style: {
                            fontWeight: "bold"
                        }
                    },
                    {
                        xtype: "hiddenfield",
                        name: "id"
                    }].concat(me.fields).concat(me.noc.cust_form_fields || []).concat(formInlines),
                tbar: me.applyPermissions(formToolbar),
                listeners: {
                    beforeadd: function(me, field) {
                        // Change label style for required fields
                        if(field.xtype == "fieldset") {
                            for(var key in field.items.items) {
                                if (!field.items.items[key].allowBlank)
                                    field.items.items[key].labelClsExtra = "noc-label-required";
                            }
                        } else {
                            if(!field.allowBlank)
                               field.labelClsExtra = "noc-label-required";
                        }
                    }
                }
            }
        };

        Ext.apply(me, {
            items: [gridPanel, formPanel]
        });

        // Initialize component
        me.callParent(arguments);
        me.currentRecord = null;
        // Create shortcuts
        var grid = me.getComponent("grid"),
            form = me.getComponent("form").items.first(),
            gt = grid.dockedItems.items[1],
            ft = form.dockedItems.first();
        me.grid = grid;
        me.form = form.getForm();
        me.search_field = gt.getComponent("search_field");
        me.actionMenu = gt.getComponent("action_menu");
        me.create_button = gt.getComponent("create");
        me.saveButton = ft.getComponent("save");
        me.closeButton = ft.getComponent("close");
        me.resetButton = ft.getComponent("reset");
        me.deleteButton = ft.getComponent("delete");
        me.cloneButton = ft.getComponent("clone");
        me.formTitle = form.getComponent("form_title");
        if(me.filters) {
            me.filterPanel = me.grid.getComponent("filters");
        }
        // Process commands
        if(me.noc.cmd && me.noc.cmd.cmd == "open") {
            me.store.setFilterParams({id: me.noc.cmd.id});
        }
        // Finally, load the store
        me.store.load();
    },
    // Toggle Grid/Form
    toggle: function() {
        // swap items. Because 'fit' layout accept only 1 item
        var me = this;
        me.items.items = [me.items.last(), me.items.first()];
        me.items.last().hide();
        me.items.first().show();
        // Apply changes to form toolbar
        if(me.items.first().itemId === "form") {
            // Switched to form
            // console.log("Switched to form");
        }
        // Layout
        me.doLayout();
        me.doComponentLayout();
    },
    // Save changed data
    saveRecord: function(data) {
        var me = this,
            mv = Ext.create(me.model, data).validate(),
            record,
            rIndex = null;
        if(!mv.isValid()) {
            // @todo: Error report
            NOC.error("Invalid data!");
            return;
        }
        if (me.currentRecord) {
            // Change
            record = me.currentRecord;
            record.set(data);
        } else {
            // Create
            record = me.store.add([data])[0];
            rIndex = me.store.indexOf(record);
        }
        me.store.sync({
            scope: me,
            success: function() {
                var me = this,
                    parent = record.get("id");
                if(!parent && rIndex != null) {
                    parent = me.store.getAt(rIndex).get("id");
                }
                me.saveInlines(parent, me.inlineStores);
            },
            failure: function(response, op, status) {
                if(record.phantom) {
                    // Remove from store
                    me.store.remove(record);
                } else {
                    record.setDirty();
                }
                this.showOpError("save", op, status);
                console.log(response.responseText);
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
            // Save completed
            me.toggle();
            me.reloadStore();
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
    // Set focus to first non-hidden field
    // @todo: check for hidden attribute
    focusOnFirstField: function() {
        var me = this;
        me.form.getFields().items[1].focus(false, 100);
    },
    // New record. Hide grid and open form
    onNewRecord: function(defaults) {
        var me = this,
            defaultValues = me.store.defaultValues;
        me.form.reset();
        if(defaultValues) {
            me.form.setValues(defaultValues);
        }
        if(defaults) {
            me.form.setValues(defaults);
        }
        me.currentRecord = null;
        me.resetInlines();
        me.setFormTitle(me.createTitle);
        me.toolbarIdLabel.setText("NEW");
        me.toggle();
        // Focus on first field
        me.focusOnFirstField();
        // Activate delete button
        me.deleteButton.setDisabled(true);
        me.saveButton.setDisabled(!me.hasPermission("create"));
        me.resetButton.setDisabled(!me.hasPermission("create"));
        me.cloneButton.setDisabled(true);
        // Disable custom form toolbar
        me.activateCustomFormToolbar(false);
    },
    // Edit record. Hide grid and open form
    editRecord: function(record) {
        var me = this;
        me.currentRecord = record;
        me.setFormTitle(me.changeTitle);
        me.toolbarIdLabel.setText("ID: " + me.currentRecord.get("id"));
        // Show edit form
        me.toggle();
        // Load records
        me.form.loadRecord(record);
        me.loadInlines();
        // Focus on first field
        me.focusOnFirstField();
        // Activate delete button
        me.deleteButton.setDisabled(!me.hasPermission("delete"));
        me.saveButton.setDisabled(!me.hasPermission("update"));
        me.resetButton.setDisabled(!me.hasPermission("update"));
        me.cloneButton.setDisabled(!me.hasPermission("create"));
        // Enable custom form toolbar
        me.activateCustomFormToolbar(true);
    },
    // Delete record
    deleteRecord: function() {
        var me = this;
        me.store.remove(me.currentRecord);
        me.currentRecord = null;
        me.store.sync();
        me.toggle();
    },
    // Reload store with current query
    reloadStore: function() {
        var me = this;
        if(me.currentQuery)
            me.store.setFilterParams(me.currentQuery);
        me.store.load();
    },
    // Search
    onSearch: function() {
        var me = this,
            v = me.search_field.getValue();
        if(v)
            me.currentQuery["__query"] = v;
        else
            delete me.currentQuery["__query"];
        me.reloadStore();
    },
    // Filter
    onFilter: function() {
        var me = this,
            fexp = {};
        Ext.each(me.filterGetters, function(g) {
            fexp = Ext.Object.merge(fexp, g());
        });
        if(me.currentQuery["__query"])
            fexp["__query"] = me.currentQuery["__query"];
        me.currentQuery = fexp;
        me.reloadStore();
    },
    // Save button pressed
    onSave: function() {
        var me = this;
        if(!me.form.isValid()) {
            NOC.error("Error in data");
            return;
        }
        var v = me.form.getFieldValues();
        if(!me.currentRecord && v.id)
            v.id = null;
        // Fetch comboboxes labels
        me.form.getFields().each(function(field) {
            if(Ext.isDefined(field.getLookupData))
                v[field.name + "__label"] = field.getLookupData();
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
            title: "Delete record?",
            msg: "Do you wish to delete record? This operation cannot be undone!",
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
    setFormTitle: function(tpl) {
        var me = this;
        me.formTitle.update(Ext.String.format(tpl, me.appTitle));
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
            text = Ext.String.format("Failed to {0}!<br>{1}",
                action, status.message);
        }
        NOC.error(text);
    },
    // "close" button pressed
    onClose: function() {
        var me = this;
        me.toggle();
        me.reloadStore();
    },
    // "clone" button pressed
    onClone: function() {
        var me = this;
        me.currentRecord = null;  // Mark record as new
        me.setFormTitle(me.createTitle);
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
            id = r.get("id"),
            action = r.get("fav_status") ? "reset" : "set",
            url = me.base_url + "favorites/item/" + id + "/" + action + "/";

        Ext.Ajax.request({
            url: url,
            method: "POST",
            scope: me,
            success: function() {
                // Invert current status
                r.set("fav_status", !r.get("fav_status"));
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
        var parentId = me.currentRecord.get("id");
        Ext.each(me.inlineStores, function(istore) {
            istore.setParent(parentId);
            istore.load();
        });
    },
    //
    onInlineEdit: function() {
        var me = this;
        if(me.currentRecord) {
            me.currentRecord.setDirty();
        }
    },
    // Admin action selected
    onAction: function(menu, item, e) {
        var me = this,
            records = me.grid.getSelectionModel().getSelection().map(function(o) {
                return o.get("id")
            });
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
                    var d = me.templates[action.resultTemplate](r);
                    Ext.create("Ext.Window", {
                        html: d,
                        width: 600,
                        height: 400,
                        title: Ext.String.format("Result: {0}", action.text)
                    }).show();
                } else {
                    NOC.info(r);
                }
            },
            failure: function() {
                NOC.error("Failed");
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
                text: "Run",
                iconCls: "icon_tick",
                handler: function() {
                    var form = w.items.first().getForm();
                    if(!form.isValid()) {
                        NOC.error("Error");
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
    onPreview: undefined
});
