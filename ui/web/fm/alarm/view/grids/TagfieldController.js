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

    onChangeTagValue: function(self) {
        var view = this.getView(),
            selected = self.getPicker().getSelectionModel().getSelection();
        if(view.treePicker) {
            view.treePicker.getController().selectNode(selected);
        }
        view.setSelected(selected, true);
    },
});