//---------------------------------------------------------------------
// inv.inv AddObject form
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.AddObjectForm");

Ext.define("NOC.inv.inv.AddObjectForm", {
  extend: "Ext.panel.Panel",
  requires: ["NOC.inv.objectmodel.LookupField"],
  app: null,
  padding: 4,

  initComponent: function(){
    var me = this,
      title = __("Create new top-level object");

    me.form = Ext.create("Ext.form.Panel", {
      layout: "anchor",
      defaults: {
        anchor: "100%",
        labelWidth: 40,
      },
      items: [
        {
          xtype: "inv.objectmodel.LookupField",
          name: "type",
          fieldLabel: __("Type"),
          uiStyle: "large",
          allowBlank: false,
        },
        {
          xtype: "textfield",
          name: "name",
          fieldLabel: __("Name"),
          uiStyle: "medium",
          allowBlank: false,
        },
        {
          xtype: "textfield",
          name: "serial",
          fieldLabel: __("Serial"),
          uiStyle: "medium",
          allowBlank: true,
        },
      ],
    });

    Ext.apply(me, {
      title: title,
      items: [me.form],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          padding: "4 4 4 0",
          items: [
            {
              text: __("Save"),
              glyph: NOC.glyph.save,
              scope: me,
              handler: me.onPressAdd,
            },
            {
              text: __("Close"),
              scope: me,
              glyph: NOC.glyph.arrow_left,
              handler: me.onPressClose,
            },
          ],
        },
      ],
    });
    me.callParent();
  },

  onPressClose: function(){
    var me = this;
    me.app.showItem(me.app.ITEM_MAIN);
  },

  onPressAdd: function(){
    var me = this,
      values = me.form.getValues();
    Ext.Ajax.request({
      url: "/inv/inv/add_group/",
      method: "POST",
      jsonData: {
        name: values.name,
        type: values.type,
        serial: values.serial,
        container: me.groupContainer ? me.groupContainer.get("id") : null,
      },
      scope: me,
      success: function(response){
        var objectId = Ext.decode(response.responseText);
        me.app.showItem(me.app.ITEM_MAIN);
        if(me.groupContainer){
          me.app.store.reload({node: me.groupContainer});
          me.app.showObject(objectId, false);
          me.groupContainer.expand();
        } else{
          me.app.store.reload({
            callback: function(){
              me.app.showObject(objectId, false);
            },
          });
        }
        me.app.setHistoryHash(objectId);
      },
      failure: function(){
        NOC.error(__("Failed to save"));
      },
    });
  },

  setContainer: function(container){
    var me = this;
    me.groupContainer = container;
    me.setTitle(__("Add object to ") + (container ? container.getPath("name") : __("Root")));
  },
});
