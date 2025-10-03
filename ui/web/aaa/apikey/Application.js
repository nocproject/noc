//---------------------------------------------------------------------
// aaa.apikey application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.aaa.apikey.Application");

Ext.define("NOC.aaa.apikey.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.aaa.apikey.Model",
    "NOC.core.PasswordGenerator",
    "NOC.core.PasswordField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.aaa.apikey.Model",
  search: true,
  helpId: "reference-apikey",

  initComponent: function(){
    var me = this;
    me.keyField = Ext.create({
      name: "key",
      xtype: "password",
      fieldLabel: __("API Key"),
      allowBlank: false,
      margin: "0 5 0 0",
      maxLength: 24,
      maxLengthText: __("The maximum length for this field is {0}"),
      minWidth: 390,
      uiStyle: "large",
    });
    me.keyGenerator = Ext.create("NOC.core.PasswordGenerator");
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 150,
        }, {
          text: __("Active"),
          dataIndex: "is_active",
          width: 25,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Expires"),
          dataIndex: "expires",
          flex: 1,
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
          name: "is_active",
          xtype: "checkbox",
          boxLabel: __("Active"),
        }, /*
                {
                    name: "expires"
                }, */
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          xtype: "container",
          layout: {
            type: "hbox",
            align: "center",
          },
          margin: "0 0 5",
          items: [
            me.keyField,
            {
              xtype: "button",
              padding: "0 15 0 15",
              text: __("Generate key"),
              scope: me,
              handler: me.generateKey,
            },
          ],
        },
        {
          name: "access",
          xtype: "gridfield",
          fieldLabel: __("Access"),
          columns: [
            {
              text: __("API"),
              dataIndex: "api",
              width: 150,
              editor: "textfield",
            },
            {
              text: __("Role"),
              dataIndex: "role",
              width: 150,
              editor: "textfield",
            },
          ],
        },
        {
          name: "acl",
          xtype: "gridfield",
          fieldLabel: __("ACL"),
          columns: [
            {
              text: __("Prefix"),
              dataIndex: "prefix",
              width: 150,
              editor: "textfield",
            },
            {
              text: __("Active"),
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
  generateKey: function(){
    var me = this;
    me.keyField.setValue(me.keyGenerator.generate(24));
  },
});
