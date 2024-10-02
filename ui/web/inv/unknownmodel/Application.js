//---------------------------------------------------------------------
// inv.unknownmodel application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.unknownmodel.Application");

Ext.define("NOC.inv.unknownmodel.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.inv.unknownmodel.Model",
    "NOC.inv.objectmodel.LookupField",
  ],
  model: "NOC.inv.unknownmodel.Model",
  search: true,
  canAdd: false,
  actions: [
    {
      title: __("Remove"),
      action: "remove",
      glyph: NOC.glyph.remove,
    },
  ],
  initComponent: function(){
    var me = this;

    me.generateBtn = Ext.create("Ext.button.Button", {
      xtype: "button",
      text: __("Generate"),
      glyph: NOC.glyph.magic,
      disabled: true,
      height: 30,
      maxWidth: 150,
      scope: me,
      handler: me.onGenerate,
    },
    );
    Ext.apply(me, {
      columns: [
        {
          text: __("Object"),
          dataIndex: "managed_object",
          width: 100,
        },
        {
          text: __("Platform"),
          dataIndex: "platform",
          width: 100,
        },
        {
          text: __("Vendor"),
          dataIndex: "vendor",
          width: 70,
        },
        {
          text: __("Part No"),
          dataIndex: "part_no",
          width: 100,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],
      formToolbar: [
      ],
      fields: [
        {
          name: "managed_object",
          xtype: "displayfield",
          fieldLabel: __("Object"),
          labelWidth: 200,
          allowBlank: true,
          uiStyle: "large",
        },
        {
          xtype: "inv.objectmodel.LookupField",
          name: "type",
          fieldLabel: __("Use connections from"),
          labelWidth: 200,
          allowBlank: true,
          uiStyle: "large",
          listeners: {
            scope: me,
            select: function(){
              me.generateBtn.setDisabled(false);
            },
          },
        },
        me.generateBtn,
      ],
    });
    me.callParent();
  },
  //
  onGenerate: function(){
    var me = this,
      formData = this.form.getValues();
    new Ext.Promise(function(resolve){
      Ext.Ajax.request({
        url: "/inv/vendor/lookup/?__format=ext&__limit=2&__query=" + me.currentRecord.get("vendor"),
        method: 'GET',
        scope: me,
        success: function(response){
          var result = Ext.decode(response.responseText);
          if(result.hasOwnProperty("total") && result.total === 1){
            resolve(result.data[0]);
          } else if(result.hasOwnProperty("total") && result.total === 0){
            NOC.error(__("Vendor not found!"));
          } else{
            NOC.error(__("Too many vendors found!"));
          }
        },
        failure: function(){
          NOC.error(__('Failed to get vendor information'));
        },
      })
    }).then(function(vendor){
      Ext.Ajax.request({
        url: "/inv/objectmodel/" + formData.type + "/",
        method: 'GET',
        scope: me,
        success: function(response){
          var result = Ext.decode(response.responseText);
          if(result.hasOwnProperty("connections")){
            NOC.run(
              "NOC.inv.objectmodel.Application",
              __("Create Model"),
              {
                cmd: {
                  cmd: "new",
                  args: {
                    description: Ext.String.format("{0} generated from {1}, platform: {2}",
                                                   me.currentRecord.get("description"),
                                                   me.currentRecord.get("managed_object"),
                                                   me.currentRecord.get("platform")),
                    data: {
                      asset: {
                        part_no: [me.currentRecord.get("part_no")],
                      },
                    },
                    connections: result.connections,
                    vendor: vendor.id,
                    vendor__label: vendor.label,
                  },
                },
              },
            );
          } else{
            NOC.error(__("No connection information"));
          }
        },
        failure: function(){
          NOC.error(__("Failed to get connection information"));
        },
      })
    });
  },
  onEditRecord: function(record){
    var me = this;
    me.callParent([record]);
    me.generateBtn.setDisabled(true);
  },
});
