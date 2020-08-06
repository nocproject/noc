//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.Tagfield");

Ext.define("NOC.fm.alarm.view.grids.Tagfield", {
    extend: "Ext.form.field.Tag",
    alias: "widget.fm.alarm.tagfield",
    controller: "fm.alarm.tagfield",
    requires: [
        "NOC.fm.alarm.view.grids.TagfieldController"
    ],
    displayField: "label",
    valueField: "id",
    queryMode: "remote",
    queryParam: "__query",
    queryCaching: false,
    queryDelay: 200,
    minChars: 2,
    pageSize: true,
    isTree: false,
    store: {
        fields: ["id", "label"],
        pageSize: 25,
        proxy: {
            type: "rest",
            pageParam: "__page",
            startParam: "__start",
            limitParam: "__limit",
            sortParam: "__sort",
            extraParams: {
                "__format": "ext"
            },
            reader: {
                type: "json",
                rootProperty: "data",
                totalProperty: "total",
                successProperty: "success"
            }
        }
    },
    config: {
        selected: null
    },
    twoWayBindable: [
        "selected"
    ],
    listeners: {
        change: "onChange"
    },
    initComponent: function() {
        this.store.proxy.url = this.url;
        if(this.isTree) {
            this.currentLeaf = false;
            this.triggers.picker.cls = "theme-classic fas fa fa-folder-open-o";
            // tree panel store
            this.treeStore = Ext.create("Ext.data.Store",
                Ext.merge(
                    Ext.clone(this.store),
                    {
                        autoLoad: true,
                        proxy: {
                            extraParams: {parent: ""}
                        },
                        listeners: {
                            scope: this,
                            load: this.onLoad
                        }
                    }, true));
            this.treePicker = this.createTreePicker();
        }
        // Fix combobox when use remote paging
        this.pickerId = this.getId() + '-picker';
        this.callParent();
    },
    setSelected: function(value, skip) {
        this.callParent([value]);
        if(!skip) {
            this.setWidgetValues(value);
        }
    },
    setWidgetValues: function(data) {
        this.setSelection(data);
    },
    createTreePicker: function() {
        var searchField = this.searchField = new Ext.create({
            xtype: "searchfield",
            width: "100%",
            emptyText: __("pattern"),
            enableKeyEvents: true,
            triggers: {
                clear: {
                    cls: "x-form-clear-trigger",
                    hidden: true,
                    scope: this,
                    handler: this.onClearSearchField
                }
            },
            listeners: {
                scope: this,
                keyup: this.onChangeSearchField
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
            displayField: this.displayField,
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
                scope: this,
                itemclick: this.onItemClick,
                itemkeydown: this.onPickerKeyDown,
                beforeitemexpand: this.onItemBeforeExpand,
                itemexpand: this.onItemExpand,
                focusleave: this.onLeaveFocusTreePicker
            }
        });
    },
    getParentNode: function() {
        var store = this.treePicker.getStore();
        if(!this.currentLeaf) {
            return store.getRootNode();
        } else {
            return store.getById(this.currentLeaf);
        }
    },
    selectItem: function(record) {
        var value = {};
        value[this.valueField] = record.id;
        value[this.displayField] = record.get("label");
        this.addValue(Ext.create("Ext.data.Model", value));
        // this.treePicker.hide();
    },
    doFilter: function() {
        var me = this, parentNode = me.getParentNode();
        if(parentNode) {
            parentNode.removeAll();
            if(this.searchField.getValue()) {
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
    loadChildren: function(id) {
        var me = this;
        if(!me.treePicker.hidden) {
            me.treePicker.mask(__("loading ..."));
        }
        this.treeStore.load({
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
    // events
    onTriggerClick: function() {
        var position,
            heightAbove = this.getPosition()[1] - Ext.getBody().getScroll().top,
            heightBelow = Ext.Element.getViewportHeight() - heightAbove - this.getHeight();
        this.treePicker.setWidth(this.getWidth());
        this.treePicker.height = Math.max(heightAbove, heightBelow) - 5;
        this.setEditable(false);
        position = this.getPosition();
        if(heightAbove > heightBelow) {
            position[1] -= this.treePicker.height - this.getHeight();
        }
        this.treePicker.showAt(position);
    },
    onLoad: function(store, records, success) {
        var parentNode = this.getParentNode();
        if(!parentNode.hasChildNodes() && success) {
            parentNode.appendChild(records.map(function(item) {
                return Ext.merge({
                    leaf: !item.get("has_children"),
                    qtip: item.get(this.displayField)
                }, item.getData());
            }));
            parentNode.expand();
        }
        if(!this.cache) { // first run, root elements
            this.cache = Ext.clone(parentNode.childNodes);
        }
    },
    onItemClick: function(view, record) {
        this.selectItem(record);
    },
    onPickerKeyDown: function(treeView, record, item, index, e) {
        var key = e.getKey();
        if(key === e.ENTER || (key === e.TAB && this.selectOnTab)) {
            this.selectItem(record);
        }
    },
    onItemBeforeExpand: function(self) {
        var node;
        if(this.currentLeaf && (this.currentLeaf !== self.getId())) {
            node = this.treePicker.getStore().getNodeById(this.currentLeaf);
            node.removeAll();
            node.appendChild(this.cache);
        }
        this.currentLeaf = self.getId();
        this.cache = Ext.clone(self.childNodes);
        if(!self.hasChildNodes()) {
            this.loadChildren(this.currentLeaf);
            return false;
        }
    },
    onItemExpand: function() {
        this.doFilter();
    },
    onLeaveFocusTreePicker: function() {
        this.setEditable(true);
        this.treePicker.hide();
    },
    // search field events
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
