//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.TagfieldController");
Ext.define("NOC.fm.alarm.view.grids.TagfieldController", {
    extend: "Ext.app.ViewController",
    alias: "controller.fm.alarm.tagfield",

    onChange: function(self) {
        var selected = self.getPicker().getSelectionModel().getSelection();
        this.getView().setSelected(selected, true);
    }
});