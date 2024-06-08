//---------------------------------------------------------------------
// NOC.core.PasswordField
// password field
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.PasswordField");

Ext.define("NOC.core.PasswordField", {
  extend: "Ext.form.field.Text",
  alias: "widget.password",
  inputType: "password",
  triggers: {
    switch: {
      cls: "fas fa fa-eye",
      hidden: false,
      handler: function(field, trigger){
        var hideCls = "fas fa fa-eye",
          showCls = "fas fa fa-eye-slash",
          type = field.inputEl.dom.getAttribute("type"),
          inputTag = field.inputEl.dom,
          triggerEl = trigger.getStateEl();

        if(type === "password"){
          inputTag.setAttribute("type", "text");
          triggerEl.removeCls(hideCls);
          triggerEl.addCls(showCls);
        } else{
          inputTag.setAttribute("type", "password");
          triggerEl.removeCls(showCls);
          triggerEl.addCls(hideCls);
        }
      },
    },
  },
});