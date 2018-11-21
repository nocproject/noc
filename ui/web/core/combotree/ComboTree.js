//---------------------------------------------------------------------
// NOC.core.Combotree
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.combotree.ComboTree");

Ext.define("NOC.core.combotree.ComboTree", {
    extend: "Ext.form.field.Picker",
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
    triggerCls: "theme-classic fas fa fa-folder-open-o",
    valueField: "id",
    editable: false,
    config: {
        displayField: "label",
        displayTpl: false
    },
    triggers: {
        clear: {
            cls: "x-form-clear-trigger",
            hidden: true,
            weight: -1,
            handler: function(field) {
                field.setValue();
                field.fireEvent("select", field);
            }
        }
    },
    currentLeaf: false,
    initComponent: function() {
        var me = this, i, path, proxy, store,
            model = Ext.create("Ext.data.Model", {
                fields: ["label", "id", "level"]
            }),
            readerCfg = {
                rootProperty: "data",
                totalProperty: "total",
                successProperty: "success"
            },
            defaultProxyCfg = {
                type: "json",
                pageParam: "__page",
                startParam: "__start",
                limitParam: "__limit",
                sortParam: "__sort",
                extraParams: {
                    __format: "ext",
                    parent: ""
                },
                reader: readerCfg
            };

        // Calculate restUrl
        path = me.$className.split(".");
        if(!me.restUrl && path[0] === 'NOC' && path[path.length - 1] === 'ComboTree') {
            me.restUrl = "/";
            for(i = 1; i < path.length - 1; i++) {
                me.restUrl += path[i] + "/";
            }
        }

        if(!me.restUrl) {
            throw "Cannot determine restUrl for " + me.$className;
        }

        proxy = Ext.create("Ext.data.proxy.Rest", Ext.apply({url: me.restUrl + "lookup/"}, defaultProxyCfg));
        store = {
            proxy: proxy,
            autoLoad: true,
            remoteFilter: false,
            model: model,
            pageSize: 500,
            remoteSort: true,
            sorters: [
                {
                    property: "name"
                }
            ]
        };
        me.bindStore(store);
        me.callParent();
    },
    createPicker: function() {
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
            }),
            picker = me.picker = new Ext.tree.Panel({
                baseCls: Ext.baseCSSPrefix + "boundlist",
                shrinkWrapDock: 2,
                rootVisible: false,
                root: {
                    expanded: true,
                    children: []
                },
                animCollapse: true,
                singleExpand: false,
                useArrows: true,
                scrollable: true,
                floating: true,
                displayField: me.displayField,
                columns: me.columns,
                height: 300,
                manageHeight: false,
                collapseFirst: false,
                tbar: [
                    searchField
                ],
                listeners: {
                    scope: me,
                    itemclick: me.onItemClick,
                    itemkeydown: me.onPickerKeyDown,
                    beforeitemexpand: me.onItemBeforeExpand,
                    itemexpand: me.onItemExpand
                }
            });
        if(!picker.initialConfig.height) {
            picker.on({
                beforeshow: me.onBeforePickerShow,
                scope: me
            });
        }
        // view = picker.getView();
        // if (Ext.isIE9 && Ext.isStrict) {
        //     // In IE9 strict mode, the tree view grows by the height of the horizontal scroll bar when the items are highlighted or unhighlighted.
        //     // Also when items are collapsed or expanded the height of the view is off. Forcing a repaint fixes the problem.
        //     view.on({
        //         scope: me,
        //         highlightitem: me.repaintPickerView,
        //         unhighlightitem: me.repaintPickerView,
        //         afteritemexpand: me.repaintPickerView,
        //         afteritemcollapse: me.repaintPickerView
        //     });
        // }
        return picker;
    },
    selectItem: function(record) {
        var me = this;
        me.setValue(record.data);
        me.fireEvent("select", me, record);
        me.collapse();
    },
    getDisplayValue: function(tplData) {
        tplData = tplData || this.displayTplData;
        return this.getDisplayTpl().apply(tplData);
    },
    applyDisplayTpl: function(displayTpl) {
        var me = this;
        if(!displayTpl) {
            displayTpl = new Ext.XTemplate('<tpl for=".">' + '{[typeof values === "string" ? values : values["' + me.getDisplayField() + '"]]}' + '</tpl>');
            displayTpl.auto = true;
        } else if(!displayTpl.isTemplate) {
            displayTpl = new Ext.XTemplate(displayTpl);
        }
        return displayTpl;
    },
    setValue: function(value) {
        var me = this;
        if(value == null || value === "") {
            me.callParent(null);
            me.setRawValue(value);
            me.getTrigger("clear").hide();
            return me;
        }
        me.getTrigger("clear").show();
        if(value.hasOwnProperty(me.valueField)) { // Ext.data.NodeInterface
            me.callParent([value[me.valueField]]);
            me.setRawValue(me.getDisplayValue(value));
            return me;
        }
        // ToDo use simple 'restUrl/<item_id>', which property use as label?
        Ext.Ajax.request({
            url: me.restUrl + value + "/get_path/",
            method: "GET",
            scope: me,
            success: function(response) {
                var k, data = Ext.decode(response.responseText).data;
                for(k = 0; k < data.length; k++) {
                    if(data[k].id === value) {
                        var v = {};
                        v[me.valueField] = value;
                        v[me.displayField] = data[k][me.displayField];
                        me.setValue(v);
                        break;
                    }
                }
            },
            failure: function() {
                NOC.error(__("Restore tree state"));
            }
        });
    },
    getValue: function() {
        return this.value;
    },
    setRawValue: function(rawValue) {
        this.callParent([rawValue]);
    },
    getSubmitValue: function() {
        var value = this.getValue();
        if(Ext.isEmpty(value)) {
            value = "";
        }
        return value;
    },
    getStoreListeners: function(store) {
        if(!store.isEmptyStore) {
            return {
                load: this.onLoad
            };
        }
    },
    loadChildren: function(id) {
        var me = this;
        var picker = me.getPicker();
        if(picker.isExpanded) {
            picker.mask(__("loading ..."));
        }
        me.store.load({
            params: {
                parent: id
            },
            callback: function() {
                if(picker.isExpanded) {
                    picker.unmask();
                }
            }
        })
    },
    getParentNode: function() {
        var me = this, store = this.getPicker().getStore();
        if(!me.currentLeaf) {
            return store.getRootNode();
        } else {
            return store.getById(me.currentLeaf)
        }
    },
    doFilter: function() {
        var me = this, parentNode = me.getParentNode();
        console.log(parentNode);
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
            node = me.getPicker().getStore().getNodeById(me.currentLeaf);
            node.removeAll();
            node.appendChild(me.cache);
        }
        me.currentLeaf = self.getId();
        me.cache = Ext.clone(self.childNodes);
        if(!self.hasChildNodes()) {
            me.loadChildren(me.currentLeaf);
            return false
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
    onBeforePickerShow: function(picker) {
        var me = this,
            heightAbove = me.getPosition()[1] - Ext.getBody().getScroll().top,
            heightBelow = Ext.Element.getViewportHeight() - heightAbove - me.getHeight();
        picker.height = Math.max(heightAbove, heightBelow) - 5;
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