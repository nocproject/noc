//---------------------------------------------------------------------
// ip.ipam application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.Application");

Ext.define("NOC.ip.ipam.Application", {
  extend: "NOC.core.Application",
  layout: "card",
  appId: "ip.ipam",
  itemId: "ip-ipam",
  controller: "ip.ipam",
  requires: [
    "Ext.layout.container.Card",
    "NOC.ip.ipam.view.Grid",
    "NOC.ip.ipam.view.forms.vrf.VRF",
    "NOC.ip.ipam.view.forms.prefix.Prefix",
    "NOC.ip.ipam.view.forms.prefix.PrefixPanel",
    "NOC.ip.ipam.view.forms.prefix.PrefixDeletePanel",
    "NOC.ip.ipam.view.forms.prefix.RebasePanel",
    "NOC.ip.ipam.view.forms.prefix.AddressPanel",
    "NOC.ip.ipam.view.forms.tools.ToolsForm",
    "NOC.ip.ipam.ApplicationModel",
    "NOC.ip.ipam.ApplicationController",
  ],
  viewModel: {
    type: "ip.ipam",
  },
  bind: {
    activeItem: "{activeItem}",
  },
  items: [
    {
      itemId: "ipam-vrf-list",
      xtype: "ip.ipam.grid",
      listeners: {
        ipIPAMVRFFormEdit: "onVRFFormEdit",
        ipIPAMViewPrefixContents: "onPrefixContentsOpen",
        //         ResetFilter: "onResetFilter"
      },
    },
    {
      itemId: "ipam-vrf-form",
      xtype: "ip.ipam.form.vrf",
      listeners: {
        ipIPAMVRFCloseForm: "onVRFFormClose",
      },
    },
    {
      itemId: "ipam-prefix-contents",
      xtype: "ip.ipam.prefix.contents",
      listeners: {
        ipIPAMPrefixFormEdit: "onPrefixFormEdit",
        ipIPAMPrefixFormNew: "onPrefixFormNew",
        ipIPAMPrefixDeleteFormOpen: "onPrefixDeleteFormOpen",
        ipIPAMPrefixListClose: "onPrefixContentsClose",
        ipIPAMViewPrefixContents: "onPrefixContentsOpen",
        ipIPAMVRFListOpen: "openVRFList",
        ipIPAMAddressFormEdit: "onAddressFormEdit",
        ipIPAMAddressFormNew: "onAddressFormNew",
        ipIPAMToolsFormOpen: "onToolsFormOpen",
      },
    },
    {
      itemId: "ipam-prefix-form",
      xtype: "ip.ipam.form.prefix",
      listeners: {
        ipIPAMPrefixFormClose: "onPrefixFormClose",
      },
    },
    {
      itemId: "ipam-prefix-del-form",
      xtype: "ip.ipam.form.delete.prefix",
      listeners: {
        ipIPAMPrefixDeleteFormClose: "onPrefixDeleteFormClose",
        ipIPAMParentPrefixOpen: "onPrefixContentsClose",
      },
    },
    {
      itemId: "ipam-address-form",
      xtype: "ip.ipam.address.form",
      listeners: {
        ipIPAMAddressCloseForm: "onAddressFormClose",
      },
    },
    {
      itemId: "ipam-prefix-rebase",
      xtype: "ip.ipam.form.rebase",
      listeners: {
        ipIPAMRebaseCloseForm: "onRebaseFormClose",
      },
    },
    {
      itemId: "ipam-tools-form",
      xtype: "ip.ipam.form.tools",
      listeners: {
        ipIPAMToolsFormClose: "onToolsFormClose",
      },
    },
  ],
});
