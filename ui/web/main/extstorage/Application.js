//---------------------------------------------------------------------
// main.extstorage application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.extstorage.Application");

Ext.define("NOC.main.extstorage.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.extstorage.Model",
  ],
  model: "NOC.main.extstorage.Model",
  search: true,

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: "Name",
          dataIndex: "name",
          width: 150,
        },
        {
          text: __("Proto"),
          dataIndex: "url",
          width: 100,
          renderer: function(value){
            var i = value.indexOf("://");
            if(i === -1){
              return "OSFS"
            } else{
              return value.substring(0, i)
            }
          },
        },
        {
          text: __("Type"),
          dataIndex: "type",
          width: 120,
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
          name: "url",
          xtype: "textfield",
          fieldLabel: __("URL"),
          allowBlank: false,
          uiStyle: "large",
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
            ["config_mirror", __("Config Mirror")],
            ["config_upload", __("Config Upload")],
            ["beef", __("Beef")],
            ["beef_test", __("Beef Test")],
            ["beef_test_config", __("Beef Test Config")],
          ],
          uiStyle: "medium",
        },
      ],
    });
    me.callParent();
  },
});
