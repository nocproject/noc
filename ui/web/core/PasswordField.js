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
    initComponent: function() {
        this.setTriggers({
            hide: {
                cls: "fas fa fa-eye",
                hidden: false,
                handler: this.showKey
            },
            show: {
                cls: "fas fa fa-eye-slash",
                hidden: true,
                handler: this.hideKey
            }
        });
        this.callParent();
    },
    showKey: function(self) {
        self.getTriggers().show.show();
        self.getTriggers().hide.hide();
        self.inputEl.dom.setAttribute("type", "text")
    },
    hideKey: function(self) {
        self.getTriggers().hide.show();
        self.getTriggers().show.hide();
        self.inputEl.dom.setAttribute("type", "password");
    }
});