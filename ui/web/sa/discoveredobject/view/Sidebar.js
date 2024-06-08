//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.view.Sidebar");

Ext.define("NOC.sa.discoveredobject.view.Sidebar", {
    extend: "Ext.form.Panel",
    alias: "widget.sa.discoveredobject.sidebar",
    controller: "sa.discoveredobject.sidebar",
    requires: [
        "NOC.core.ComboBox",
        "NOC.core.label.LabelField",
        "NOC.sa.discoveredobject.controller.Sidebar",
        "NOC.sa.discoveredobject.widget.Check",
        "NOC.sa.discoveredobject.widget.Source",
    ],
    title: __("Filter"),
    reference: "sa-discoveredobject-filter",
    config: {
        value: {},
    },
    twoWayBindable: ["value"],
    publishes: ["value"],
    scrollable: "y",
    minWidth: 250,
    layout: {
        type: "vbox",
        align: "right"
    },
    items: [
        {
            xtype: "form",
            border: false,
            minWidth: this.minWidth - 30,
            width: "100%",
            padding: "5 10 0 10",
            defaults: {
                labelAlign: "top",
                width: "100%",
                uiStyle: undefined,
            },
            items: [
                {
                    xtype: "hiddenfield",
                    name: "__query",
                    listeners: {
                        change: "setFilter"
                    }
                },
                {
                    xtype: "core.combo",
                    restUrl: "/wf/state/lookup/",
                    name: "state",
                    fieldLabel: __("By State:"),
                    listeners: {
                        select: "setFilter"
                    },
                    query: {
                        "allowed_models": "sa.ManagedObject"
                    },
                },
                {
                    xtype: "labelfield",
                    name: "labels",
                    fieldLabel: __("By Labels:"),
                    toBufferTrigger: false,
                    filterProtected: false,
                    query: {
                        "allow_models": ["sa.ManagedObject"]
                    },
                    listeners: {
                        change: "setFilter"
                    }
                },
                {
                    xtype: "datefield",
                    name: "last_update",
                    startDay: 1,
                    fieldLabel: __("By Last Update:"),
                    format: "d.m.Y",
                    emptyText: __("dd.mm.yyyy"),
                    listeners: {
                        change: "setFilter"
                    }
                },
                {
                    xtype: "sourcefield",
                    name: "source",
                    items: [
                        {
                            text: __("ETL"),
                            value: "etl"
                        },
                        {
                            text: __("Discovery"),
                            value: "scan"
                        },
                        {
                            text: __("Manual"),
                            value: "manual"
                        }
                    ],
                    listeners: {
                        change: "setFilter"
                    }
                },
                {
                    xtype: "textarea",
                    name: "addresses",
                    fieldLabel: __("By IP list (max. 2000):"),
                    listeners: {
                        change: "setFilter"
                    },
                },
                {
                    xtype: "checkfield",
                    name: "checks",
                    listeners: {
                        change: "setFilter",
                        updateLayout: function() {
                            Ext.defer(function() {
                                this.updateLayout();
                            }, 25, this);
                        }
                    }
                }
            ],
            buttons: [
                {
                    xtype: "button",
                    itemId: "clean-btn",
                    minWidth: 50,
                    text: __("Clean All"),
                    handler: "cleanAllFilters"
                }
            ],
        }
    ],
});
