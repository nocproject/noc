//---------------------------------------------------------------------
// peer.person application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.person.Application");

Ext.define("NOC.peer.person.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.RepoPreview",
    "NOC.peer.person.Model",
    "NOC.peer.rir.LookupField",
  ],
  model: "NOC.peer.person.Model",
  search: true,
  columns: [
    {
      text: __("Nic-hdl"),
      dataIndex: "nic_hdl",
      flex: 1,
    },
    {
      text: __("Person/Role Name"),
      dataIndex: "person",
      flex: 1,
    },
    {
      text: __("Type"),
      dataIndex: "type",
      renderer: function(a){
        return {P: "Person", R: "Role"}[a];
      },
      flex: 1,
    },
    {
      text: __("RIR"),
      dataIndex: "rir",
      renderer: NOC.render.Lookup("rir"),
      flex: 1,
    },
  ],
  fields: [
    {
      name: "nic_hdl",
      xtype: "textfield",
      fieldLabel: __("Nic-hdl"),
      allowBlank: false,
      anchor: "70%",
    },
    {
      name: "type",
      xtype: "combobox",
      fieldLabel: __("Type"),
      allowBlank: false,
      store: [
        ["P", "Person"],
        ["R", "Role"],     
      ],
    },
    {
      name: "person",
      xtype: "textfield",
      fieldLabel: __("Person/Role Name"),
      allowBlank: false,
      anchor: "70%",
    },
    {
      name: "address",
      xtype: "textareafield",
      fieldLabel: __("Address"),
      allowBlank: false,
      anchor: "70%",
    },
    {
      name: "phone",
      xtype: "textareafield",
      fieldLabel: __("Phone"),
      allowBlank: false,
      anchor: "70%",
    },
    {
      name: "fax_no",
      xtype: "textareafield",
      fieldLabel: __("Fax-no"),
      anchor: "70%",
    },
    {
      name: "email",
      xtype: "textareafield",
      fieldLabel: __("Email"),
      allowBlank: false,
      anchor: "70%",
    },
    {
      name: "rir",
      xtype: "peer.rir.LookupField",
      fieldLabel: __("RIR"),
      allowBlank: false,
    },
    {
      name: "extra",
      xtype: "textareafield",
      fieldLabel: __("Extra"),
      anchor: "70%",
    },
  ],
  filters: [
    {
      title: "By RIR",
      name: "rir",
      ftype: "lookup",
      lookup: "peer.rir",
    },
  ],
  preview: {
    xtype: "NOC.core.RepoPreview",
    syntax: "rpsl",
    // ToDo need check nic_hdl variable in previewName
    previewName: "Person RPSL: {0}",
    restUrl: "/peer/person/{0}/repo/rpsl/",
  },
});
