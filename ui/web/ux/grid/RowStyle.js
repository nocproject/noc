Ext.define("Ext.ux.grid.RowStyle", {
  extend: "Ext.plugin.Abstract",
  alias: "plugin.rowstyle",

  init: function(grid){
    var view = grid.getView();
    view.getRowClass = function(record){
      return record.get("row_class") || "";
    };
  },
});
