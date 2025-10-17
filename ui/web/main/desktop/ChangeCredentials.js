//---------------------------------------------------------------------
// Login window
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.ChangeCredentials");

Ext.define("NOC.main.desktop.ChangeCredentials", {
  extend: "Ext.Window",
  title: __("Change Password"),
  layout: "fit",
  autoShow: true,
  draggable: false,
  resizable: false,
  closable: false,
  modal: true,
  app: null,
  fields: [],
  width: 400,
    
  initComponent: function(){
    var me = this;
    //
    me.form = Ext.create("Ext.form.Panel", {
      bodyPadding: 4,
      border: false,
      defaults: {
        enableKeyEvents: true,
        anchor: "100%",
        listeners: {
          scope: me,
          specialkey: me.onSpecialKey,
        },
      },
      items: me.fields,
      buttonAlign: "center",
      buttons: [
        {
          text: __("Close"),
          glyph: NOC.glyph.times,
          scope: me,
          handler: me.onClose,
        },
        {
          text: __("Reset"),
          glyph: NOC.glyph.undo,
          scope: me,
          handler: me.onReset,
        },
        {
          text: __("Change"),
          glyph: NOC.glyph.save,
          disabled: true,
          formBind: true,
          scope: me,
          handler: me.onChangeCredentials,
        },
      ],
    });

    Ext.apply(me, {
      items: [me.form],
    });
    me.callParent()
  },
  //
  afterRender: function(){
    var me = this;
    me.callParent();
    // Focus on first field
    me.form.getForm().getFields().first().focus();
  },
  // Close button pressed. Close window
  onClose: function(){
    var me = this;
    me.close();
  },
  // Reset button pressed. Clear form
  onReset: function(){
    var me = this;
    me.form.getForm().reset();
  },
  // Change credentials form pressed
  onChangeCredentials: function(){
    var me = this,
      form = me.form.getForm();
    if(form.isValid()){
      me.changeCredentials(form.getValues());
    }
  },
  //
  changeCredentials: function(values){
    var me = this;
    Ext.Ajax.request({
      method: "PUT",
      url: "/api/login/change_credentials",
      jsonData: {
        user: NOC.username,
        old_password: values.old_password,
        new_password: values.new_password,
        retype_password: values.retype_password,
      },
      scope: me,
      success: function(response){
        var status = Ext.decode(response.responseText);
        if(status.status){
          NOC.info(__("Credentials has been changed"));
          me.close();
        } else{
          NOC.error(__("Failed to change credentials: ") + status.message);
        }
      },
      failure: function(response){
        var status = Ext.decode(response.responseText);
        NOC.error(__("Failed to change credentials: ") + status.error);
      },
    });
  },
  //
  onSpecialKey: function(field, key){
    var me = this;
    if(field.xtype !== "textfield")
      return;
    switch(key.getKey()){
      case Ext.EventObject.ENTER:
        key.stopEvent();
        me.onChangeCredentials();
        break;
      case Ext.EventObject.ESC:
        key.stopEvent();
        me.onReset();
        break;
    }
  },
});
