//---------------------------------------------------------------------
// NOC.sa.managedobject.RepoPreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.RepoPreview");

Ext.define("NOC.sa.managedobject.RepoPreview", {
  // extend: "NOC.core.RepoPreview",
  alias: "widget.sa.repopreview",
  requires: [
    "NOC.core.ComboBox",
  ],
  initComponent: function(){
    var me = this, topBar, index;
    me.callParent();
    me.menuBtn = Ext.create("Ext.button.Split", {
      itemId: "menuBtn",
      menu: [
        {
          text: __("Revision"),
          handler: Ext.pass(me.menuBtnFn, "revision", me),
        },
        {
          text: __("Object"),
          handler: Ext.pass(me.menuBtnFn, "object", me),
        },
      ],
    });
    me.objectCombo = Ext.create("NOC.core.ComboBox", {
      restUrl: "/sa/managedobject/lookup/",
      uiStyle: "medium-combo",
      itemId: "objectCombo",
      hidden: true,
      listeners: {
        scope: me,
        select: me.onSelectObject,
        clear: me.onClearObject,
      },
    });
    topBar = me.getDockedItems()[0];
    index = topBar.items.indexOfKey("swapRevBtn");
    topBar.insert(index, me.menuBtn);
    topBar.insert(index + 3, me.objectCombo);
    me.diffCombo.setFieldLabel(null);
    me.swapRevButton.hide();
    me.diffCombo.hide();
    me.diffCombo.un("select", me.onSelectDiff, me);
    me.diffCombo.on("select", me.localListener(me.onSelectDiff), me);
    me.sideBySideModeButton.setHandler(me.localListener(me.onSideBySide), me);
    me.prevDiffButton.setHandler(me.localListener(me.onPrevDiff, "button"), me);
    me.nextDiffButton.setHandler(me.localListener(me.onNextDiff, "button"), me);
    me.resetButton.handler = function(){
      me.clearHideCombo(me.diffCombo);
      me.clearHideCombo(me.objectCombo);
      this.requestText();
      this.requestRevisions();
      me.menuBtnFn("revision", me.currentRecord.get("id"));
    }
  },
  preview: function(record, backItem){
    var me = this;
    me.callParent(arguments);
    me.menuBtnFn("revision", record.get("id"));
    if(me.historyHashPrefix){
      me.app.setHistoryHash(
        me.currentRecord.get("id"),
        me.historyHashPrefix,
      );
    }
  },
  menuBtnFn: function(type, id){
    var me = this;
    me.compareType = type;
    switch(type){
      case "object": {
        me.clearHideCombo(me.diffCombo);
        me.objectCombo.show();
        me.menuBtn.setText(Ext.String.format("{0} {1}", __("Compare With"), __("Object")));
        break;
      }
      case "revision": {
        me.clearHideCombo(me.objectCombo);
        me.diffCombo.setValue(null);
        if(Ext.getClassName(id) !== "Ext.menu.Item"){
          me.requestRevisions(id);
        }
        me.diffCombo.show();
        me.menuBtn.setText(Ext.String.format("{0} {1}", __("Compare With"), __("Revision")));
        break;
      }
    }
  },
  onSelectObject: function(combo, record){
    var me = this;
    me.requestRevisions(record.id);
    me.diffCombo.show();
  },
  onClearObject: function(){
    var me = this;
    me.clearHideCombo(me.diffCombo);
  },
  clearHideCombo: function(combo){
    combo.setValue(null);
    combo.store.loadData([]);
    combo.hide();
  },
  localListener: function(listener, type){
    var me = this, rev1, rev2, objectId;
    return function(){
      if(me.compareType === "revision"){
        listener.call(me);
      } else if(me.compareType === "object"){
        objectId = me.objectCombo.getValue();
        if(type === "button"){
          listener.call(me, objectId);
        } else{
          rev1 = me.revCombo.getValue();
          rev2 = me.diffCombo.getValue();
          me.requestDiff(rev1, rev2, objectId);
        }
      }
    }
  },
});
