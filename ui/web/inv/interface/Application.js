//---------------------------------------------------------------------
// inv.interface application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interface.Application");


Ext.define("NOC.inv.interface.Application", {
    extend: "NOC.core.Application",
    requires: [
        "NOC.sa.managedobject.LookupField",
        "NOC.core.filter.Filter",
    ],


    initComponent: function() {
        var me = this;

        me.currentObject = null;

        // Create stores
        me.l1Store = Ext.create("NOC.inv.interface.L1Store");
        me.l3Store = Ext.create("NOC.inv.interface.L3Store");
        me.l2Store = Ext.create("NOC.inv.interface.L2Store");
        me.lagStore = Ext.create("NOC.inv.interface.LAGStore");
        // Create tabs
        me.l1Panel = Ext.create("NOC.inv.interface.L1Panel", {
            app: me,
            store: me.l1Store,
            disabled: true
        });
        me.lagPanel = Ext.create("NOC.inv.interface.LAGPanel", {
            app: me,
            store: me.lagStore,
            disabled: true
        });
        me.l2Panel = Ext.create("NOC.inv.interface.L2Panel", {
            app: me,
            store: me.l2Store,
            disabled: true
        });
        me.l3Panel = Ext.create("NOC.inv.interface.L3Panel", {
            app: me,
            store: me.l3Store,
            disabled: true
        });
        //
        me.searchField = Ext.create({
            xtype: "searchfield",
            tooltip: __("When you found some descriptions in DB,<br/>" +
                "you can specify here more detailed search"),
            name: "search",
            fieldLabel: __('Detailed'),
            labelWidth: 50,
            disabled: true,
            emptytext: __("Search ..."),
            typeAhead: true,
            scope: me,
            handler: me.onSearch,
            listeners: {
                render: me.addTooltip
            }
        });
        me.searchDescriptionField = Ext.create("Ext.ux.form.SearchField", {
            fieldLabel: __("Description Search"),
            tooltip: __("Put your Search Description end press ENTER<br/>" +
                "Returns only first 300 strings with matched description."),
            labelWidth: 100,
            width: "500",
            explicitSubmit: true,
            scope: me,
            handler: me.onSearchDescriptionField,
            listeners: {
                render: me.addTooltip
            }
        });
        me.filterPan = Ext.create({
                xtype: 'NOC.Filter',
                appId: me.appId,
                reference: 'filterPanel',
                itemId: "filterPanel",
                width: 300,
                collapsed: false,
                border: true,
                split: true,
                resizable: false,
                stateful: true,
                selectionStore: 'interface.selectionStore',
            }),
            me.radioForm = Ext.create({
                xtype: 'radiogroup',
                fieldLabel: __("is managed"),
                labelWidth: 55,
                defaultType: 'radiofield',
                itemId: 'radio',
                defaults: {
                    flex: 1
                },
                layout: 'hbox',
                items: [{
                        boxLabel: 'true',
                        name: 'is_managed',
                        inputValue: 'true',
                        id: 'only_is_managed'
                    },
                    {
                        boxLabel: 'false',
                        name: 'is_managed',
                        inputValue: 'false',
                        id: 'only_is_not_managed'
                    },
                    {
                        boxLabel: 'all',
                        name: 'is_managed',
                        inputValue: 'all',
                        id: 'both'
                    },
                ]
            }),

            //
            Ext.apply(me, {
                items: [
                    Ext.create("Ext.panel.Panel", {
                        id: "search-description-panel",
                        layout: 'border',
                        items: [
                            Ext.create("Ext.tab.Panel", {
                                name: "tab",
                                region: 'center',
                                deferredRender: false,
                                itemId: "tab",
                                border: false,
                                activeTab: 0,
                                layout: "fit",
                                autoScroll: true,
                                defaults: {
                                    autoScroll: true
                                },
                                items: [
                                    me.l1Panel,
                                    me.lagPanel,
                                    me.l2Panel,
                                    me.l3Panel
                                ]
                            }),
                            {
                                xtype: 'tabpanel',
                                region: 'east',
                                title: 'Filter Panel',
                                animCollapse: true,
                                collapsible: true,
                                split: true,
                                width: 225,
                                minsize: 175,
                                maxSize: 400,
                                margins: '0 5 0 0',
                                activeTab: 0,
                                tabPosition: 'bottom',
                                items: [
                                    me.filterPan,
                                    {
                                        xtype: 'panel',
                                        title: 'One MO',
                                        layout: {
                                            type: 'vbox',
                                            align: 'stretch'
                                        },
                                        items: [{
                                                xtype: "sa.managedobject.LookupField",
                                                fieldLabel: __('Object'),
                                                labelWidth: 50,
                                                tooltip: __("Choose MO, and you'll see all it's interfaces"),
                                                name: "managedobject",
                                                itemId: "managedobject",
                                                emptytext: __("Select managed object ..."),
                                                listeners: {
                                                    render: me.addTooltip,
                                                    select: {
                                                        scope: me,
                                                        fn: me.onObjectChange
                                                    }
                                                },
                                            },
                                            {
                                                xtype: "searchfield",
                                                tooltip: __("When you found some descriptions in DB,<br/>" +
                                                    "you can specify here more detailed search"),
                                                name: "search",
                                                fieldLabel: __('Detailed'),
                                                labelWidth: 50,
                                                disabled: false,
                                                emptytext: __("Search ..."),
                                                typeAhead: true,
                                                scope: me,
                                                handler: me.onSearch,
                                                listeners: {
                                                    render: me.addTooltip
                                                }
                                            },
                                        ]

                                    }
                                ]
                            },
                        ]
                    })
                ],
                tbar: [
                    me.searchDescriptionField,
                    me.radioForm,
                    {
                        xtype: 'tbspacer',
                        width: 20
                    },
                    me.searchField,
                ]
            });
        me.callParent();
        me.radio1 = Ext.getCmp('only_is_managed')
        me.radio1.setValue(true);
        me.tabPanel = me.getComponent("tab");
    },
    // Called when managed object changed
    onObjectChange: function(combo, s) {
        var me = this;
        me.currentObject = s.get("id");
        me.loadInterfaces();
    },
    // Load object's interfaces
    loadInterfaces: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/interface/" + me.currentObject + "/",
            method: "GET",
            scope: me,
            success: me.onLoadInterfaces,
            failure: function() {
                NOC.error("Failed to get interfaces");
            }
        });
    },
    // Init stores
    onLoadInterfaces: function(response) {
        var me = this,
            data = Ext.decode(response.responseText),
            adjust = function(panel, data) {
                var d = (data || []).length > 0;
                panel.setDisabled(!d);
            }
        // Set panel visibility
        adjust(me.l1Panel, data.l1);
        adjust(me.lagPanel, data.lag);
        adjust(me.l2Panel, data.l2);
        adjust(me.l3Panel, data.l3);
        // Load data
        me.l1Store.loadData(data.l1 || []);
        me.lagStore.loadData(data.lag || []);
        me.l2Store.loadData(data.l2 || []);
        me.l3Store.loadData(data.l3 || []);
        //
        me.searchField.setDisabled(false);
        me.searchField.setValue("");
    },
    //
    onSearch: function(value) {
        var me = this;
        s = value.toLowerCase();
        // Match substring
        smatch = function(record, field, s) {
            return record.get(field).toLowerCase().indexOf(s) != -1;
        };
        // Search L1
        me.l1Store.filterBy(function(r) {
            return (
                !s ||
                smatch(r, "name", s) ||
                smatch(r, "description", s) ||
                smatch(r, "mac", s) ||
                smatch(r, "lag"));
        });
        // Search LAG
        me.lagStore.filterBy(function(r) {
            return (
                !s ||
                smatch(r, "name", s) ||
                smatch(r, "description", s));
        });
        // Search L2
        me.l2Store.filterBy(function(r) {
            return (
                !s ||
                smatch(r, "name", s) ||
                smatch(r, "description", s));
        });
        // Search L3
        me.l3Store.filterBy(function(r) {
            return (
                !s ||
                smatch(r, "name", s) ||
                smatch(r, "description", s) ||
                smatch(r, "vrf", s));
        });
    },
    //search_description handler
    onSearchDescriptionField: function(value) {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/interface/search_description/" + value + "/",
            method: "GET",
            scope: me,
            success: me.onLoadInterfaces,
            params: me.onGetFilterParams,
            failure: function() {
                NOC.error("Failed to get interfaces");
            }
        });
    },
    onGetFilterParams: function() {
        var me = this;
        var is_managed = Ext.getCmp('only_is_managed').getGroupValue()
        columnsStore = me.down('[itemId=filterPanel]').viewModel.get('filterObject')
        columnsStore['is_managed'] = is_managed
        return columnsStore
    }
});