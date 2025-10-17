//---------------------------------------------------------------------
// phone.dialplan application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.dialplan.Application");

Ext.define("NOC.phone.dialplan.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.phone.dialplan.Model",
  ],
  model: "NOC.phone.dialplan.Model",
  search: true,
  helpId: "reference-dialplan",

  initComponent: function(){
    var me = this;

    me.cardButton = Ext.create("Ext.button.Button", {
      text: __("Card"),
      glyph: NOC.glyph.eye,
      scope: me,
      handler: me.onCard,
    });

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 100,
        },
        {
          text: __("Mask"),
          dataIndex: "mask",
          width: 150,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          uiStyle: "medium",
          allowBlank: false,
        },
        {
          name: "mask",
          xtype: "textfield",
          fieldLabel: __("Mask"),
          allowBlank: false,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
      ],

      formToolbar: [
        me.cardButton,
      ],
    });
    me.callParent();
  },

  //
  onCard: function(){
    var me = this;
    if(me.currentRecord){
      window.open(
        "/api/card/view/dialplan/" + me.currentRecord.get("id") + "/",
      );
    }
  },
});
