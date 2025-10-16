//---------------------------------------------------------------------
// phone.numbercategory application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.numbercategory.Application");

Ext.define("NOC.phone.numbercategory.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.phone.numbercategory.Model",
    "NOC.phone.dialplan.LookupField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.phone.numbercategory.Model",
  search: true,
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 100,
        },
        {
          text: __("Active"),
          dataIndex: "is_active",
          width: 50,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Order"),
          dataIndex: "order",
          width: 50,
          align: "right",
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
          name: "is_active",
          xtype: "checkbox",
          boxLabel: __("Is Active"),
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: false,
        },
        {
          name: "order",
          xtype: "numberfield",
          fieldLabel: __("Order"),
          uiStyle: "small",
        },
        {
          name: "rules",
          xtype: "gridfield",
          fieldLabel: __("Rules"),
          columns: [
            {
              text: __("DialPlan"),
              dataIndex: "dialplan",
              width: 100,
              renderer: NOC.render.Lookup("dialplan"),
              editor: "phone.dialplan.LookupField",
            },
            {
              text: __("Mask"),
              dataIndex: "mask",
              width: 200,
              editor: "textfield",
            },
            {
              text: __("Is Active"),
              dataIndex: "is_active",
              width: 50,
              renderer: NOC.render.Bool,
              editor: "checkbox",
            },
            {
              text: __("Description"),
              dataIndex: "description",
              flex: 1,
              editor: "textfield",
            },
          ],
        },
      ],
    });
    me.callParent();
  },
});
