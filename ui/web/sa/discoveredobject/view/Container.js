//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.view.Container");

Ext.define("NOC.sa.discoveredobject.view.Container", {
    extend: "Ext.panel.Panel",
    alias: "widget.sa.discoveredobject.container",
    controller: "sa.discoveredobject.container",
    viewModel: {
        type: "sa.discoveredobject.container"
    },
    requires: [
        "Ext.ux.form.SearchField",
        "NOC.sa.discoveredobject.controller.Container",
        "NOC.sa.discoveredobject.model.Container",
        "NOC.sa.discoveredobject.view.Grid",
        "NOC.sa.discoveredobject.view.Sidebar",
    ],
    layout: "border",
    reference: "sa-discoveredobject-list",
    tbar: [
        {
            xtype: "searchfield",
            width: 400,
            enableKeyEvents: true,
            emptyText: __("enter search text and press <Enter>"),
            triggers: {
                clear: {
                    cls: "x-form-clear-trigger",
                    hidden: true,
                    handler: "onClearSearchField"
                }
            },
            listeners: {
                keyup: "onChangeSearchField"
            }
        },
        {
            text: __("Filter"),
            glyph: NOC.glyph.filter,
            tooltip: __("Show/Hide Filter"),
            enableToggle: true,
            toggleHandler: "onToggleFilter",
            bind: {
                pressed: "{isFilterOpen}"
            },
        },
        {
            xtype: "splitbutton",
            text: __("Group Action"),
            menu: [],
            bind: {
                disabled: "{buttonDisabled}"
            },
            listeners: {
                beforerender: "onBeforeRenderGroupAction"
            },
        },
        {
            xtype: "splitbutton",
            text: __("Sync Record"),
            menu: [],
            bind: {
                disabled: "{buttonDisabled}"
            },
            listeners: {
                beforerender: "onBeforeRenderSyncRecord"
            },
        },
        {
            text: __("Scan"),
            handler: "onScan",
        }
    ],
    items: [
        {
            region: "center",
            xtype: "sa.discoveredobject.grid",
            reference: "sa-discoveredobject-grid",
        },
        {
            xtype: "sa.discoveredobject.sidebar",
            reference: "sa-discovered-sidebar",
            region: "east",
            width: 250,
            split: true,
            resizable: true,
            border: false,
            animCollapse: false,
            collapseMode: 'mini',
            hideCollapseTool: true,
            bind: {
                collapsed: "{!isFilterOpen}",
            },
            split: {
                xtype: "splitter"
            },
            listeners: {
                filterChanged: "onFilterChanged"
            }
        }
    ]
});
