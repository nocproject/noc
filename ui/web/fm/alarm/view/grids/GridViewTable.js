//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.GridViewTable");

Ext.define("NOC.fm.alarm.view.grids.GridViewTable", {
  extend: "Ext.view.Table",
  mixins: [
    "NOC.core.mixins.Export",
  ],
  enableTextSelection: true,
  destroy: function(){
    if(this.contextMenu){
      this.contextMenu.destroy();
    }
    this.callParent();
  },
  getRowClass: function(record){
    var filter, freshCI,
      cls = record.get("row_class"),
      status = record.get("status"),
      duration = record.get("duration");

    if(status === "C"){
      return "noc-recent-alarms";
    }
    if(this.up().getViewModel()){
      filter = this.up().getViewModel().get("displayFilter.duration");
    }
    if(cls){
      if(filter && filter.on){
        freshCI = "fm-blur-" + filter.row4.opacity;
        if(duration < filter.row1.duration * 60){
          freshCI = "fm-blur-" + filter.row1.opacity;
        } else if(duration < filter.row2.duration * 60){
          freshCI = "fm-blur-" + filter.row2.opacity;
        } else if(duration < filter.row3.duration * 60){
          freshCI = "fm-blur-" + filter.row3.opacity;
        }
        return cls + " " + freshCI;
      } else{
        return cls;
      }
    } else{
      return "";
    }
  },
  isHidden: function(){
    if(!this.contextMenu){
      return true;
    }
    return this.contextMenu.isHidden();
  },
  listeners: {
    itemcontextmenu: function(view, record, node, index, event){
      if(!this.contextMenu){
        this.contextMenu = Ext.create("Ext.menu.Menu", {
          itemId: "fm-alarm-contextmenu",
          items: [
            {
              text: __("Refresh"),
              glyph: NOC.glyph.refresh,
              scope: this,
              handler: this.onContextMenuRefresh,
            },
            {
              itemId: "favItemMenu",
              glyph: NOC.glyph.star,
              scope: this,
            },
            {
              text: __("Save screen"),
              glyph: NOC.glyph.arrow_down,
              scope: this,
              handler: function(){
                var grid = this.getRefOwner();
                this.save(grid, grid.reference + ".csv");
              },
            },
            {
              text: __("Filter"),
              glyph: NOC.glyph.filter,
              menu: [
                {
                  itemId: "objectFilterMenuItem",
                  text: __("Object"),
                  reference: "managed_object",
                  scope: this,
                  handler: Ext.pass(this.onContextMenuFilter, record),
                },
                {
                  itemId: "segmentFilterMenuItem",
                  text: __("Segment"),
                  reference: "segment",
                  scope: this,
                  handler: Ext.pass(this.onContextMenuFilter, record),
                },
                {
                  itemId: "classFilterMenuItem",
                  text: __("Class"),
                  reference: "alarm_class",
                  scope: this,
                  handler: Ext.pass(this.onContextMenuFilter, record),
                },
              ],
            },
          ],
        });
      }
      event.stopEvent();
      var favItemMenu = this.contextMenu.items.get("favItemMenu"),
        objectFilterMenuItem = this.contextMenu.down("#objectFilterMenuItem"),
        segmentFilterMenuItem = this.contextMenu.down("#segmentFilterMenuItem"),
        classFilterMenuItem = this.contextMenu.down("#classFilterMenuItem");

      favItemMenu.setText(record.get("fav_status") ? __("Remove from favorites") : __("Add to favorites"));  
      favItemMenu.setHandler(Ext.pass(this.onContextMenuAddToFavorites, record), this);
      classFilterMenuItem.setHandler(Ext.pass(this.onContextMenuFilter, record), this);
      objectFilterMenuItem.setHandler(Ext.pass(this.onContextMenuFilter, record), this);
      segmentFilterMenuItem.setHandler(Ext.pass(this.onContextMenuFilter, record), this);

      this.contextMenu.showAt(event.getXY());
      return false;
    },
  },
  //
  onContextMenuRefresh: function(){
    this.getRefOwner().getController().fireViewEvent("fmAlarmReload", this.getRefOwner());
  },
  //
  onContextMenuAddToFavorites: function(record){
    this.getRefOwner().getController().onFavItem(this, undefined, undefined, undefined, undefined, record);
  },
  //
  onContextMenuFilter: function(record, item){
    var value = {}, vm = this.up("[itemId=fm-alarm]").getViewModel();
    // ToDo remove after implement ahead mode (with selection binding) in comboTree
    // if(item.reference !== "segment") {
    value[item.reference] = Ext.create("Ext.data.Model", {
      id: record.get(item.reference),
      label: record.get(item.reference + "__label"),
    });
    // } else {
    // value[item.reference] = record.get(item.reference);
    // }
    vm.set("activeFilter", Ext.merge(vm.get("activeFilter"), value));
  },
  //
  tooltip: function(record){
    var tooltipFromData = "<span class='noc-alarm-tooltip-flat'>" + __("no comments") + "</span>";

    if(record.get("logs").length){
      tooltipFromData = "<table><thead><tr><th>" + __("Date") + "</th><th>" + __("User") + "</th><th>" + __("Message") + "</th></tr></thead><tbody>";
      for(var j = 0; j < record.get("logs").length; j++){
        var r = record.get("logs")[j];
        tooltipFromData += "<tr><td>" + Ext.util.Format.date(r.timestamp, "d.m.Y H:i")
                + "</td><td>" + r.user + "</td><td style='white-space: pre-line;'>" + Ext.String.htmlEncode(r.message) + "</td></tr>";
      }
      tooltipFromData += "</tbody></table>";
    }
    return tooltipFromData;
  },

});
