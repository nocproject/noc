//---------------------------------------------------------------------
// main.imagestore application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.imagestore.Application");

Ext.define("NOC.main.imagestore.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.imagestore.Model",
  ],
  model: "NOC.main.imagestore.Model",
  search: true,

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 150,
        },
        {
          text: __("Type"),
          dataIndex: "type",
          width: 150,
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "meduim",
        },
        {
          name: "content_type",
          xtype: "displayfield",
          fieldLabel: __("Content Type"),
          allowBlank: true,
          uiStyle: "meduim",
        },
        {
          layout: "hbox",
          border: false,
          items: [
            {
              xtype: "displayfield",
              name: "filename",
              fieldLabel: __("File name"),
              allowBlank: true,
              width: 400,
            },
            {
              xtype: "filefield",
              name: "file",
              flex: 1,
              buttonOnly: true,
              hideLabel: true,
              buttonText: __("Select File..."),
              listeners: {
                change: me.setAttachmentName,
              },
            },
          ],
        },
      ],
    });
    me.callParent();
  },
  setAttachmentName: function(field, value){
    var filename = value.replace(/(^.*([\\/]))?/, "");
    field.previousSibling().setValue(filename)
  },
  onSave: function(){
    var me = this,
      data = new FormData();
    data.append("name", me.down("[name=name]").getValue());
    data.append("filename", me.down("[name=filename]").getValue());
    var file = me.down("[name=file]");
    if(file.getValue()){
      data.append("file", file.fileInputEl.dom.files[0]);
    }
    Ext.Ajax.request({
      method: "POST",
      url: me.base_url + (me.currentRecord ? me.currentRecord.get([me.idField]) + "/" : ""),
      rawData: data,
      headers: {"Content-Type": null},
      scope: me,
      success: function(){
        var me = this;
        me.showItem(me.ITEM_GRID);
        me.reloadStore();
        NOC.info(__("Records has been saved"));
      },
      failure: function(){
        NOC.error(__("Failed"));
      },
    });
  },
});
