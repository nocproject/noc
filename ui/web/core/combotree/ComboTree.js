//---------------------------------------------------------------------
// NOC.core.Combotree
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.combotree.ComboTree");

Ext.define("NOC.core.combotree.ComboTree", {
    extend: "Ext.form.field.ComboBox",
    requires: [
        "Ext.data.Store",
        "Ext.data.proxy.Rest",
        "Ext.data.reader.Json",
        "Ext.data.TreeStore",
        "Ext.data.Model",
        "Ext.tree.Panel",
        "Ext.ux.form.SearchField"
    ],
    mixins: [
        "Ext.util.StoreHolder"
    ],
    alias: 'widget.noc.core.combotree',
    triggerCls: "theme-classic fas fa fa-folder-open-o",
    valueField: "id",
    displayField: "label",
    displayTpl: false,
    editable: true,
    typeAhead: true,
    queryMode: "remote",
    queryParam: "__query",
    queryCaching: false,
    queryDelay: 200,
    forceSelection: false,
    minChars: 2,
    triggerAction: "all",
    query: {},
    stateful: false,
    autoSelect: false,
    pageSize: true,
    currentLeaf: false,
    triggers: {
        clear: {
            cls: "x-form-clear-trigger",
            hidden: true,
            weight: -1,
            handler: function(field) {
                field.setValue(null);
                field.fireEvent("select", field);
            }
        }
    },
    listeners: {
        change: function(field, value) {
            if(value == null || value === "") {
                this.getTrigger("clear").hide();
                return;
            }
            this.getTrigger("clear").show();
        }
    },
    initComponent: function() {
        var me = this, i, path, proxyCfg, treeProxyCfg, storeCfg,
            model = Ext.create("Ext.data.Model", {
                fields: ["label", "id", "has_children"]
            }),
            readerCfg = {
                rootProperty: "data",
                totalProperty: "total",
                successProperty: "success"
            },
            defaultProxyCfg = {
                type: "rest",
                pageParam: "__page",
                startParam: "__start",
                limitParam: "__limit",
                sortParam: "__sort",
                extraParams: {
                    __format: "ext"
                },
                reader: readerCfg
            };

        // Calculate restUrl
        path = me.$className.split(".");
        if(!me.restUrl && path[0] === "NOC" && path[path.length - 1] === "ComboTree") {
            me.restUrl = "/";
            for(i = 1; i < path.length - 1; i++) {
                me.restUrl += path[i] + "/";
            }
        }

        if(!me.restUrl) {
            throw "Cannot determine restUrl for " + me.$className;
        }

        proxyCfg = Ext.apply({url: me.restUrl + "lookup/"}, defaultProxyCfg);
        storeCfg = {
            proxy: proxyCfg,
            autoLoad: true,
            remoteFilter: false,
            model: model,
            remoteSort: true,
            sorters: [
                {
                    property: "name"
                }
            ]
        };
        // typeahead store
        me.bindStore(storeCfg);
        // tree panel store
        treeProxyCfg = Ext.apply({
                url: me.restUrl + "lookup/"
            },
            Ext.merge({
                extraParams: {parent: ""}
            }, Ext.clone(defaultProxyCfg), true)
        );
        var treeStoreCfg = Ext.merge(
            Ext.clone(storeCfg),
            {
                proxy: treeProxyCfg,
                listeners: {
                    scope: me,
                    load: this.onLoad
                }
            }, true);
        me.treeStore = Ext.create("Ext.data.Store", treeStoreCfg);
        me.treePicker = me.createTreePicker();
        // Fix combobox when use remote paging
        me.pickerId = me.getId() + '-picker';
        me.callParent();
    },
    onTriggerClick: function() {
        var me = this, position,
            heightAbove = me.getPosition()[1] - Ext.getBody().getScroll().top,
            heightBelow = Ext.Element.getViewportHeight() - heightAbove - me.getHeight();
        me.treePicker.setWidth(me.getWidth());
        me.treePicker.height = Math.max(heightAbove, heightBelow) - 5;
        me.setEditable(false);
        position = me.getPosition();
        if(heightAbove > heightBelow) {
            position[1] -= me.treePicker.height - me.getHeight();
        }
        me.treePicker.showAt(position);
    },
    onLeaveFocusTreePicker: function() {
        this.setEditable(true);
        this.treePicker.hide();
    },
    createTreePicker: function() {
        var me = this,
            searchField = me.searchField = new Ext.create({
                xtype: "searchfield",
                width: "100%",
                emptyText: __("pattern"),
                enableKeyEvents: true,
                triggers: {
                    clear: {
                        cls: "x-form-clear-trigger",
                        hidden: true,
                        scope: me,
                        handler: me.onClearSearchField
                    }
                },
                listeners: {
                    scope: me,
                    keyup: me.onChangeSearchField
                }
            });
        return new Ext.tree.Panel({
            baseCls: Ext.baseCSSPrefix + "boundlist",
            shrinkWrap: 2,
            shrinkWrapDock: true,
            animCollapse: true,
            singleExpand: false,
            useArrows: true,
            scrollable: true,
            floating: true,
            displayField: me.displayField,
            columns: me.columns,
            manageHeight: false,
            collapseFirst: false,
            rootVisible: false,
            root: {
                expanded: true,
                children: []
            },
            // ToDo make variable for theme
            bodyStyle: {
                background: "#ecf0f1"
            },
            tbar: [
                searchField
            ],
            listeners: {
                scope: me,
                itemclick: me.onItemClick,
                itemkeydown: me.onPickerKeyDown,
                beforeitemexpand: me.onItemBeforeExpand,
                itemexpand: me.onItemExpand,
                focusleave: me.onLeaveFocusTreePicker
            }
        });
    },
    selectItem: function(record) {
        var me = this, value = {};
        value[this.valueField] = record.id;
        value[this.displayField] = record.get("label");
        me.setValue(Ext.create("Ext.data.Model", value));
        me.treePicker.hide();
    },
    getStoreListeners: Ext.emptyFn,
    loadChildren: function(id) {
        var me = this;
        if(!me.treePicker.hidden) {
            me.treePicker.mask(__("loading ..."));
        }
        me.treeStore.load({
            params: {
                parent: id
            },
            callback: function() {
                if(!me.treePicker.hidden) {
                    me.treePicker.unmask();
                }
            }
        });
    },
    getParentNode: function() {
        var me = this, store = me.treePicker.getStore();
        if(!me.currentLeaf) {
            return store.getRootNode();
        } else {
            return store.getById(me.currentLeaf);
        }
    },
    doFilter: function() {
        var me = this, parentNode = me.getParentNode();
        if(parentNode) {
            parentNode.removeAll();
            if(me.searchField.getValue()) {
                parentNode.appendChild(me.cache.filter(
                    function(node) {
                        return node.data[me.displayField].toLowerCase()
                        .indexOf(me.searchField.getValue().toLowerCase()) !== -1;
                    }
                ));
            } else {
                parentNode.appendChild(me.cache);
                parentNode.expand();
            }
        }
    },
    // event handlers
    onLoad: function(store, records, success) {
        var me = this, parentNode = me.getParentNode();
        if(!parentNode.hasChildNodes() && success) {
            parentNode.appendChild(records.map(function(item) {
                return Ext.merge({
                    leaf: !item.get("has_children"),
                    qtip: item.get(me.displayField)
                }, item.getData());
            }));
            parentNode.expand();
        }
        if(!me.cache) { // first run, root elements
            me.cache = Ext.clone(parentNode.childNodes);
        }
    },
    onItemClick: function(view, record) {
        this.selectItem(record);
    },
    onItemBeforeExpand: function(self) {
        var me = this, node;
        if(me.currentLeaf && (me.currentLeaf !== self.getId())) {
            node = me.treePicker.getStore().getNodeById(me.currentLeaf);
            node.removeAll();
            node.appendChild(me.cache);
        }
        me.currentLeaf = self.getId();
        me.cache = Ext.clone(self.childNodes);
        if(!self.hasChildNodes()) {
            me.loadChildren(me.currentLeaf);
            return false;
        }
    },
    onItemExpand: function() {
        this.doFilter();
    },
    onPickerKeyDown: function(treeView, record, item, index, e) {
        var key = e.getKey();
        if(key === e.ENTER || (key === e.TAB && this.selectOnTab)) {
            this.selectItem(record);
        }
    },
    onDestroy: function() {
        var me = this;
        me.bindStore(null);
        me.callParent();
    },
    onClearSearchField: function(self) {
        self.setValue();
        self.getTrigger("clear").hide();
        this.doFilter();
    },
    onChangeSearchField: function(self) {
        if(self.getValue() == null || !self.getValue().length) {
            this.onClearSearchField(self);
            return;
        }
        this.doFilter();
        self.getTrigger("clear").show();
    }
});