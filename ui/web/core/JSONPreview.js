//---------------------------------------------------------------------
// NOC.core.JSONPreview monaco editor
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.JSONPreview");

Ext.define("NOC.core.JSONPreview", {
  extend: "NOC.core.MonacoPanel",
  requires: [
    "NOC.core.ShareWizard",
  ],
  app: null,
  restUrl: null,
  previewName: null,
  config: {
    saveDisabled: false,
    shareDisabled: false,
  },
  initComponent: function(){
    this.tbar = [
      {
        itemId: "close",
        text: __("Close"),
        glyph: NOC.glyph.arrow_left,
        handler: "onBack",
      },
      "-",
      {
        itemId: "save",
        text: __("Save"),
        glyph: NOC.glyph.save,
        disabled: this.saveDisabled,
        handler: "onSave",
      },
      "-",
      {
        text: __("Share"),
        glyph: NOC.glyph.share,
        disabled: this.shareDisabled,
        handler: "onShare",
      },
    ];
    // setup editor language
    this.items[0].language = "json";
    this.callParent();
  },
  onShare: function(){
    Ext.Msg.show({
      title: __("Share item?"),
      msg: __("Would you like to share item and contribute to Open-Source project?"),
      buttons: Ext.Msg.YESNO,
      modal: true,
      scope: this,
      fn: function(button){
        if(button === "yes"){
          this.doShare()
        }
      },
    })
  },
  onSave: function(){
    var restUrl = this.restUrl.replace("{0}", this.currentRecord.get("id")) 
    Ext.Ajax.request({
      url: restUrl,
      method: "POST",
      scope: this,
      success: function(){
        NOC.info(__("JSON saved"));
      },
      failure: function(){
        NOC.error(__("Failed to save JSON"))
      },
    });
  },
  doShare: function(){
    var restUrl = this.restUrl.replace("{0}", this.currentRecord.get("id")).replace("/json/", "/share_info/"),
      wizard = Ext.create("NOC.core.ShareWizard", {
        restUrl: restUrl,
      });
    wizard.startProcess();
  },
});