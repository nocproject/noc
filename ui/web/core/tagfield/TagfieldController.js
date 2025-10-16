//---------------------------------------------------------------------
// Tagfield controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.tagfield.TagfieldController");
Ext.define("NOC.core.tagfield.TagfieldController", {
  extend: "Ext.app.ViewController",
  alias: "controller.core.tagfield",

  onChangeTagValue: function(self){
    var view = this.getView(),
      selected = self.getPicker().getSelectionModel().getSelection();
    if(view.lazyLoadTree){
      view.treePicker.getController().selectNode(selected);
    }
    view.setSelected(selected, true);
  },
});
