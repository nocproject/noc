//---------------------------------------------------------------------
// ip.ipam.prefix & address list
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.prefix.PrefixAddressLists");

Ext.define("NOC.ip.ipam.view.forms.prefix.PrefixAddressLists", {
    extend: "Ext.panel.Panel",
    alias: "widget.ip.ipam.list.prefixAddress",
    controller: "ip.ipam.list.prefixAddress",
    layout: "vbox",
    requires: [
        "NOC.ip.ipam.view.forms.prefix.PrefixAddressListsController"
    ],
    scrollable: true,
    bodyPadding: 4,
    bubbleEvents: [
        "ipIPAMVRFListOpen",
        "ipIPAMPrefixFormEdit",
        "ipIPAMViewPrefixContents",
        "ipIPAMAddressFormEdit",
        "ipIPAMAddressFormNew"
    ],
    items: [
        {
            layout: "hbox",
            border: false,
            width: "100%",
            items: [
                {
                    layout: "hbox",
                    flex: 4,
                    border: false,
                    items: [
                        {
                            border: false,
                            tpl: [
                                "<span class='nav-vrf ipam-nav'>{vrf__label}</span>"
                            ],
                            bind: {
                                data: "{prefix}"
                            },
                            listeners: {
                                element: "el",
                                delegate: "span.nav-vrf",
                                click: "onVRFListOpen"
                            }
                        },
                        {
                            border: false,
                            tpl: [
                                "<tpl for='.'>",
                                "<span",
                                "<tpl if='xindex !== xcount'>",
                                " class='breadcrumb nav-{id} ipam-nav'",
                                "</tpl>",
                                ">{name}</span>",
                                "</tpl>"
                            ],
                            bind: {
                                data: "{prefix.path}"
                            },
                            listeners: {
                                element: "el",
                                delegate: "span.breadcrumb",
                                click: "onNavigationClick"
                            }
                        }
                    ]
                },
                {
                    xtype: "textfield",
                    flex: 2,
                    emptyText: __("Quick Jump..."),
                    listeners: {
                        specialkey: "onQuickJump"
                    }
                },
                {
                    xtype: "combo",
                    flex: 2,
                    fieldLabel: __("Favorites"),
                    labelAlign: "right",
                    emptyText: __("Select Bookmark"),
                    bind: {
                        store: "{bookmarkStore}"
                    },
                    listeners: {
                        select: "onSelectBookmark"
                    }
                }
            ]
        },
        {
            xtype: "displayfield",
            padding: 10,
            width: "100%",
            fieldStyle: "text-align: center;",
            bind: {
                value: "<b>" + "{prefix.description}" + "</b>"
            }
        },
        {
            layout: "hbox",
            border: false,
            bodyPadding: 10,
            width: "100%",
            bind: {
                hidden: "{noPrefixes}"
            },
            items: [
                {
                    xtype: "displayfield",
                    flex: 3,
                    value: "<b>" + __("Allocated Prefixes") + "</b>"
                },
                {
                    xtype: "button",
                    text: __("Show Free") + " " + __("Prefix"),
                    handler: "onShowFreePrefixes",
                    bind: {
                        hidden: "{noFreePrefixes}"
                    }
                }
            ]
        },
        {
            xtype: "dataview",
            itemId: "ipam-prefix-grid",
            width: "100%",
            itemSelector: "tr.prefix-row",
            tpl: [
                "<table class='ipam'>",
                "  <thead style='text-align: left;'>",
                "    <tr>",
                "      <th></th>",
                "      <th></th>",
                "      <th></th>",
                "      <th>" + __("Prefix") + "</th>",
                "      <th></th>",
                "      <th>" + __("State") + "</th>",
                "      <th>" + __("Project") + "</th>",
                "      <th>" + __("AS") + "</th>",
                "      <th>" + __("VLAN") + "</th>",
                "      <th>" + __("Description") + "</th>",
                "      <th>" + __("Usage") + "</th>",
                "      <th>" + __("Address Usage") + "</th>",
                "      <th>" + __("TT") + "</th>",
                "      <th>" + __("Labels") + "</th>",
                "    </tr>",
                "  </thead>",
                "  <tbody>",
                "    <tpl for='.'>",
                "    <tr class='prefix-row {row_class}'>",
                "      <td class='prefix-bookmark' style='cursor: pointer;'>",
                "         <tpl if='!isFree'>",
                "         <tpl if='has_bookmark'><i class='fa fa-star'></i>",
                "         <tpl else><i class='fa fa-star-o'></i></tpl>",
                "         </tpl>",
                "      </td>",
                "      <td class='prefix-edit' style='cursor: pointer;'>",
                "        <tpl if='!isFree && permissions.change'><i title='" + __("Edit Prefix") + "' class='fa fa-edit'></i></tpl>",
                "      </td>",
                "      <td class='prefix-card' style='cursor: pointer;'>",
                "        <tpl if='!isFree && permissions.view'><a href='/api/card/view/prefix/{id}/'",
                "          style='color: black;' target='_blank' title='" + __("Open Prefix Card") + "'>",
                "          <i class='fa fa-id-card-o'></i></a></tpl>",
                "      </td>",
                "      <td>{name}</td>",
                "      <td class='prefix-view' style='cursor: pointer;'>",
                "         <tpl if='isFree && permissions.add_prefix'><i title='" + __("Add Prefix") + "' class='fa fa-plus'></i>",
                "         <tpl elseif='!isFree && permissions.view'><i title='" + __("Show Prefix") + "' class='fa fa-eye'></i></tpl>",
                "      </td>",
                "      <td>{state}</td>",
                "      <td>{project}</td>",
                "      <td>{as}</td>",
                "      <td>{vlan}</td>",
                "      <td>{description}</td>",
                "      <td>{usage}</td>",
                "      <td>{address_usage}</td>",
                "      <td>{tt}</td>",
                "      <td>{labels}</td>",
                "    </tr>",
                "    </tpl>",
                "  </tbody>",
                "</table>"
            ],
            bind: {
                store: "{prefixStore}",
                hidden: "{noPrefixes}"
            },
            prepareData: function(data) {
                var permissions = this.up("[itemId=ip-ipam]").getViewModel().get("prefix.permissions");
                return Ext.apply({permissions: permissions}, data);
            },
            listeners: {
                itemclick: "onViewPrefixContents"
            },
            emptyText: __("WARNING!!!&nbsp;This prefix is empty! Please add nested prefixes."),
        },
        {
            layout: "hbox",
            border: false,
            bodyPadding: 10,
            width: "100%",
            bind: {
                hidden: "{noAddresses}"
            },
            items: [
                {
                    xtype: "displayfield",
                    flex: 3,
                    value: "<b>" + __("Assigned Addresses") + "</b>"
                },
                {
                    xtype: "button",
                    text: __("Show Free") + " " + __("Address"),
                    handler: "onShowFreeAddresses",
                    bind: {
                        hidden: "{noFreeAddresses}"
                    }
                }
            ]
        },
        {
            xtype: "dataview",
            itemId: "ipam-address-grid",
            width: "100%",
            itemSelector: "tr.address-row",
            tpl: [
                "<table class='ipam'>",
                "  <thead style='text-align: left;'>",
                "    <tr>",
                "      <th>" + __("Address") + "</th>",
                "      <th>" + __("Name") + "</th>",
                "      <th></th>",
                "      <th>" + __("State") + "</th>",
                "      <th>" + __("Project") + "</th>",
                "      <th>" + __("FQDN") + "</th>",
                "      <th>" + __("MAC") + "</th>",
                "      <th>" + __("Managed Object") + "</th>",
                "      <th>" + __("GW") + "</th>",
                "      <th>" + __("Description") + "</th>",
                "      <th>" + __("Source") + "</th>",
                "      <th>" + __("TT") + "</th>",
                "      <th>" + __("Labels") + "</th>",
                "    </tr>",
                "  </thead>",
                "  <tbody>",
                "    <tpl for='.'>",
                "    <tr class='address-row {row_class}'>",
                "      <td>{address}</td>",
                "      <td>{name}</td>",
                "      <td class='address-view' style='cursor: pointer;'>",
                "         <tpl if='isFree && permissions.add_address'><i title='" + __("Add Address") + "' class='fa fa-plus'></i>",
                "         <tpl elseif='!isFree && permissions.change'><i title='" + __("Edit Address") + "' class='fa fa-edit'></i></tpl>",
                "      </td>",
                "      <td>{state}</td>",
                "      <td>{project}</td>",
                "      <td>{fqdn}</td>",
                "      <td>{mac}</td>",
                "      <td><a href='/api/card/view/managedobject/{mo_id}/' target='_blank'>{mo_name}",
                "<tpl if='subinterface'>@{subinterface}</tpl></a></td>",
                "      <td><tpl if='is_router'><i class='fa fa-check'/><tpl else><i class='fa fa-minus'></i></tpl>",
                "      </td>",
                "      <td>{short_desc}</td>",
                "      <td>{source}</td>",
                "      <td>{tt}</td>",
                "      <td>{labels}</td>",
                "    </tr>",
                "    </tpl>",
                "  </tbody>",
                "</table>"
            ],
            bind: {
                store: "{addressStore}",
                hidden: "{noAddresses}"
            },
            prepareData: function(data) {
                var permissions = this.up("[itemId=ip-ipam]").getViewModel().get("prefix.permissions");
                return Ext.apply({permissions: permissions}, data);
            },
            listeners: {
                itemclick: "onViewAddresses"
            },
            emptyText: __("WARNING!!!&nbsp;This prefix is empty! Please add nested addresses."),
        },
        {
            layout: "hbox",
            border: false,
            bodyPadding: 10,
            width: "100%",
            bind: {
                hidden: "{noRanges}"
            },
            items: [
                {
                    xtype: "displayfield",
                    value: "<b>" + __("Address Ranges") + "</b>"
                }
            ]
        },
        {
            xtype: "dataview",
            itemId: "ipam-range-grid",
            width: "100%",
            itemSelector: "tr.range-row",
            tpl: [
                "<table class='ipam'>",
                "  <thead>",
                "    <tr>",
                "      <th style='width: 20px;'></th>",
                "      <th>" + __("Name") + "</th>",
                "      <th>" + __("From Address") + "</th>",
                "      <th>" + __("To Address") + "</th>",
                "      <th>" + __("Description") + "</th>",
                "    </tr>",
                "  </thead>",
                "  <tbody>",
                "    <tpl for='.'>",
                "    <tr class='range-row {row_class}'>",
                "      <td><div class='ipam-range' style='background-color: {color};'></div></td>",
                "      <td>{name}</td>",
                "      <td>{from_address}</td>",
                "      <td>{to_address}</td>",
                "      <td>{description}</td>",
                "    </tr>",
                "    </tpl>",
                "  </tbody>",
                "</table>"
            ],
            bind: {
                store: "{rangeStore}",
                hidden: "{noRanges}"
            }
        }
    ]
});
