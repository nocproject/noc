//---------------------------------------------------------------------
// main.mimetype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.mimetype.Application");

Ext.define("NOC.main.mimetype.Application", {
  extend: "NOC.core.ModelApplication",
  requires: ["NOC.main.mimetype.Model"],
    
  model: "NOC.main.mimetype.Model",
    
  columns: [
    {
      text: __("Extension"),
      dataIndex: "extension",
    },
    {
      text: __("MIME Type"),
      dataIndex: "mime_type",
      flex: 1,
    },
  ],
    
  fields: [
    {
      xtype: "textfield",
      fieldLabel: __("Extension"),
      name: "extension",
      allowBlank: false,
      regex: /^\.[a-zA-Z0-9-]+$/,
    },

    {
      xtype: "textfield",
      fieldLabel: __("MIME Type"),
      name: "mime_type",
      allowBlank: false,
      width: 500,
      regex: /^[a-zA-Z0-9-]+\/[a-zA-Z0-9-]+$/,
    },
  ],
});
