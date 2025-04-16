//---------------------------------------------------------------------
// peer.maintainer application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.maintainer.Application");

Ext.define("NOC.peer.maintainer.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.RepoPreview",
    "NOC.peer.maintainer.Model",
    "NOC.peer.person.LookupField",
    "NOC.peer.person.M2MField",
    "NOC.peer.rir.LookupField",
  ],
  model: "NOC.peer.maintainer.Model",
  search: true,
  columns: [
    {
      text: __("Maintainer"),
      dataIndex: "maintainer",
      flex: 1,
    },
    {
      text: __("Description"),
      dataIndex: "description",
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
      name: "maintainer",
      xtype: "textfield",
      fieldLabel: __("Maintainer"),
      allowBlank: false,
    },
    {
      name: "description",
      xtype: "textfield",
      fieldLabel: __("Description"),
      allowBlank: false,
    },
    {
      name: "password",
      xtype: "textfield",
      fieldLabel: __("Password"),
      allowBlank: true,
    },
    {
      name: "rir",
      xtype: "peer.rir.LookupField",
      fieldLabel: __("RIR"),
      allowBlank: false,
    },
    {
      xtype: "peer.person.M2MField",
      name: "admins",
      fieldLabel: __("Admin-c"),
      buttons: ["add", "remove"],
      allowBlank: false,
    },
    {
      name: "extra",
      xtype: "textareafield",
      fieldLabel: __("Extra"),
      allowBlank: true,
      width: 600, 
      height: 100,
      fieldStyle: {
        fontFamily: "Courier",
      },
    },
  ],
  preview: {
    xtype: "NOC.core.RepoPreview",
    syntax: "rpsl",
    previewName: "Maintainer RPSL: {0}",
    restUrl: "/peer/maintainer/{0}/repo/rpsl/",
  },
});
