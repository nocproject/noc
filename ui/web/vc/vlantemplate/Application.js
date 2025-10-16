//---------------------------------------------------------------------
// vc.vlantemplate application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vlantemplate.Application");

Ext.define("NOC.vc.vlantemplate.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.vc.vlantemplate.Model",
    "NOC.vc.vlanprofile.LookupField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.vc.vlantemplate.Model",
  search: true,
  helpId: "reference-allocation-group",

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: "Name",
          dataIndex: "name",
          flex: 150,
        },
        {
          text: "Type",
          dataIndex: "type",
          flex: 100,
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "type",
          xtype: "combobox",
          fieldLabel: __("Type"),
          allowBlank: false,
          store: [
            ["global", "Global"],
            ["l2domain", "L2 Domain"],
            ["manual", "Manual"],
          ],
        },
        {
          name: "vlans",
          xtype: "gridfield",
          fieldLabel: __("VLANs"),
          columns: [
            {
              text: __("VLANs"),
              dataIndex: "vlan",
              editor: "textfield",
              regex: /^\s*\d+\s*(-\d+\s*)?(,\s*\d+\s*(-\d+)?)*$/,
              width: 200,
            },
            {
              dataIndex: "name",
              text: __("Name"),
              editor: "textfield",
              width: 150,
            },
            {
              dataIndex: "description",
              text: __("Description"),
              editor: "textfield",
              width: 150,
            },
            {
              text: __("VLAN Profile"),
              dataIndex: "profile",
              width: 200,
              editor: {
                xtype: "vc.vlanprofile.LookupField",
              },
              renderer: NOC.render.Lookup("profile"),
            },
          ],
        },
      ],
    });
    me.callParent();
  },
});
