//---------------------------------------------------------------------
// NOC.core.ModelApplication
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ModelApplication");

Ext.define("NOC.core.ModelApplication", {
    extend: "NOC.core.Application",
    requires: ["NOC.core.ModelStore"],
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
        var gridToolbar = [
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
        ].concat(me.gridToolbar);
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
                    items: [
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
                    ]
                }
            ].concat(me.columns).concat(cust_columns),
            border: false,
            autoScroll: true,
            stateful: true,
            stateId: app_name + "-grid",
            plugins: [Ext.create("Ext.ux.grid.AutoSize")],
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
                formBind: true,
                disabled: true,
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
        ].concat(me.formToolbar);

        var formPanel = {
            xtype: 'container',
            itemId: "form",
            layout: "fit",
            items: {
                xtype: 'form',
                border: true,
                padding: 4,
                bodyPadding: 4,
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
                    }].concat(me.fields).concat(me.noc.cust_form_fields || []),
                tbar: me.applyPermissions(formToolbar),
                listeners: {
                    beforeadd: function(me, field) {
                        if(!field.allowBlank)
                           field.labelClsExtra = "noc-label-required";
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
            record;
        if(!mv.isValid()) {
            // @todo: Error report
            return;
        }
        if (me.currentRecord) {
            // Change
            record = me.currentRecord;
            record.set(data);

        } else {
            // Create
            record = me.store.add([data])[0];
        }
        me.store.sync({
            scope: me,
            success: function() {
                this.toggle();
                this.reloadStore();
            },
            failure: function(response, op, status) {
                if(record.phantom) {
                    // Remove from store
                    me.store.remove(record);
                } else {
                    record.setDirty();
                }
                this.showOpError("save", op, status);
            }
        });
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
        me.currentRecord = null;
        me.setFormTitle(me.createTitle);
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
        // Show edit form
        me.toggle();
        // Load records
        me.form.loadRecord(record);
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
    }
});
