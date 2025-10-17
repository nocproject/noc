//---------------------------------------------------------------------
// aaa.group application
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.aaa.group.Application");

Ext.define("NOC.aaa.group.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.aaa.group.Model",
    "NOC.aaa.group.Permission",
  ],
  model: "NOC.aaa.group.Model",
  search: true,
  recordReload: true,
  maskElement: "el",
  // actions: [
  //     {
  //         title: __("Delete selected groups"),
  //         run: "groupDelete",
  //         glyph: NOC.glyph.trash
  //     }
  // ],
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 130,
        },
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          autoFocus: true,
          tabIndex: 10,
          uiStyle: "large",
        },
        {
          name: "permissions",
          xtype: "noc.group.permission",
          fieldLabel: __("Permissions"),
          allowBlank: true,
        },
      ],
    });
    me.callParent();
  },
  onNewRecord: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/aaa/group/new_permissions/",
      method: "GET",
      scope: me,
      success: function(response){
        var me = this,
          data = Ext.decode(response.responseText).data;
        me.newRecord(data);
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  onReset: function(){
    var me = this, msg = __("Reset");
    me.mask(msg);
    Ext.TaskManager.start({
      run: function(){
        me.form.findField("permissions").resetAllPermission();
        me.unmask(msg);
      },
      interval: 0,
      repeat: 1,
      scope: me,
    });
    me.callParent();
  },
  // groupDelete: function() {
  //     console.log("not implemented");
  // }
});
