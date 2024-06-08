//---------------------------------------------------------------------
// inv.inv Contacts panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.contacts.ContactsPanel");

Ext.define("NOC.inv.inv.plugins.contacts.ContactsPanel", {
  extend: "Ext.panel.Panel",
  requires: [
  ],
  title: __("Contacts"),
  closable: false,
  scrollable: true,
  padding: 4,

  initComponent: function(){
    var me = this;

    me.displayAdminField = Ext.create("Ext.container.Container", {
      maxHeight: 150,
      width: "100%",
      scrollable: true,
      style: {
        marginLeft: '10px',
        'font-size': '12px',
      },
    });

    me.editAdminField = Ext.create("Ext.form.field.HtmlEditor", {
      height: 150,
      hidden: true,
    });

    me.displayBillField = Ext.create("Ext.container.Container", {
      maxHeight: 150,
      width: "100%",
      scrollable: true,
      style: {
        marginLeft: '10px',
        'font-size': '12px',
      },
    });

    me.editBillField = Ext.create("Ext.form.field.HtmlEditor", {
      height: 150,
      hidden: true,
    });

    me.displayTechField = Ext.create("Ext.container.Container", {
      maxHeight: 150,
      width: "100%",
      scrollable: true,
      style: {
        marginLeft: '10px',
        'font-size': '12px',
      },
    });

    me.editTechField = Ext.create("Ext.form.field.HtmlEditor", {
      height: 150,
      hidden: true,
    });

    me.editButton = Ext.create("Ext.button.Button", {
      text: __("Edit"),
      glyph: NOC.glyph.edit,
      scope: me,
      handler: me.onEdit,
    });

    me.saveButton = Ext.create("Ext.button.Button", {
      text: __("Save"),
      glyph: NOC.glyph.save,
      scope: me,
      handler: me.onSave,
      hidden: true,
    });

    // Grids
    Ext.apply(me, {
      items: [
        {
          xtype: "container",
          html: "<b>Administrative Contacts:</b>",
        },
        me.displayAdminField,
        me.editAdminField,
        {
          xtype: "container",
          html: "<b>Billing Contacts:</b>",
        },
        me.displayBillField,
        me.editBillField,
        {
          xtype: "container",
          html: "<b>Technical Contacts:</b>",
        },
        me.displayTechField,
        me.editTechField,
      ],
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        padding: "0 0 4 0",
        items: [
          me.editButton,
          me.saveButton,
        ],
      }],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    me.displayAdminField.update(data.contacts_administrative);
    me.editAdminField.setValue(data.contacts_administrative);
    me.displayBillField.update(data.contacts_billing);
    me.editBillField.setValue(data.contacts_billing);
    me.displayTechField.update(data.contacts_technical);
    me.editTechField.setValue(data.contacts_technical);
  },
  //
  onEdit: function(){
    var me = this;
    // Toolbar
    me.editButton.hide();
    me.saveButton.show();
    // Swap buttons
    me.displayAdminField.hide();
    me.editAdminField.show();
    me.displayBillField.hide();
    me.editBillField.show();
    me.displayTechField.hide();
    me.editTechField.show();
  },
  //
  onSave: function(){
    var me = this,
      adminValue = me.editAdminField.getValue(),
      billValue = me.editBillField.getValue(),
      techValue = me.editTechField.getValue();
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/contacts/",
      method: "POST",
      jsonData: {
        administrative: adminValue,
        billing: billValue,
        technical: techValue,
      },
      scope: me,
      success: function(){
        me.editButton.show();
        me.saveButton.hide();
        me.editAdminField.hide();
        me.editBillField.hide();
        me.editTechField.hide();
        me.displayAdminField.update(adminValue);
        me.displayBillField.update(billValue);
        me.displayTechField.update(techValue);
        me.displayAdminField.show();
        me.displayBillField.show();
        me.displayTechField.show();
      },
      failure: function(){
        NOC.error(__("Failed to save data"));
      },
    });
  },
});
