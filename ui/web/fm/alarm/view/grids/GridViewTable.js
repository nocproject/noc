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
        "NOC.core.Export"
    ],
    enableTextSelection: true,
    destroy: function() {
        if(this.contextMenu) {
            this.contextMenu.destroy();
        }
        this.callParent();
    },
    getRowClass: function(record) {
        var c = record.get("row_class"),
            status = record.get("status"),
            duration = record.get("duration"),
            filter = this.up().getViewModel().get("displayFilter.duration"),
            freshCI = "fm-blur-" + filter.row4.opacity;

        if(status === "C") {
            return "noc-recent-alarms";
        }
        if(c) {
            if(filter.on) {
                if(duration < filter.row1.duration * 60) {
                    freshCI = "fm-blur-" + filter.row1.opacity;
                } else if(duration < filter.row2.duration * 60) {
                    freshCI = "fm-blur-" + filter.row2.opacity;
                } else if(duration < filter.row3.duration * 60) {
                    freshCI = "fm-blur-" + filter.row3.opacity;
                }
                return c + " " + freshCI;
            } else {
                return c;
            }
        } else {
            return "";
        }
    },
    isHidden: function() {
        if(!this.contextMenu) {
            return true;
        }
        return this.contextMenu.isHidden();
    },
    listeners: {
        itemcontextmenu: function(view, record, node, index, event) {
            if(!this.contextMenu) {
                this.contextMenu = Ext.create("Ext.menu.Menu", {
                    itemId: "fm-alarm-contextmenu",
                    items: [
                        {
                            text: __("Refresh"),
                            glyph: NOC.glyph.refresh,
                            scope: this,
                            handler: this.onContextMenuRefresh
                        },
                        {
                            text: __("Save screen"),
                            glyph: NOC.glyph.arrow_down,
                            scope: this,
                            handler: function() {
                                var grid = this.getRefOwner();
                                this.save(grid, grid.reference + ".csv");
                            }
                        },
                        {
                            text: __("Filter"),
                            glyph: NOC.glyph.filter,
                            menu: [
                                {
                                    text: __("Object"),
                                    reference: "managed_object",
                                    scope: this,
                                    handler: Ext.pass(this.onContextMenuFilter, record)
                                },
                                {
                                    text: __("Segment"),
                                    reference: "segment",
                                    scope: this,
                                    handler: Ext.pass(this.onContextMenuFilter, record)
                                },
                                {
                                    text: __("Class"),
                                    reference: "alarm_class",
                                    scope: this,
                                    handler: Ext.pass(this.onContextMenuFilter, record)
                                }
                            ]
                        }
                    ]
                });
            }
            event.stopEvent();
            this.contextMenu.showAt(event.getXY());
            return false;
        }
        //     beforerefresh: function(cmp) {
        //         me.gridPanel.plugins[0].bodyTop = 0;
        //     }
    },
    //
    onContextMenuRefresh: function() {
        this.getRefOwner().getController().fireViewEvent("fmAlarmReload", this.getRefOwner());
    },
    //
    onContextMenuFilter: function(record, item) {
        var value = {}, vm = this.up("[itemId=fm-alarm]").getViewModel();
        // ToDo remove after implement ahead mode (with selection binding) in comboTree
        // if(item.reference !== "segment") {
        value[item.reference] = Ext.create("Ext.data.Model", {
            id: record.get(item.reference),
            label: record.get(item.reference + "__label")
        });
        // } else {
        // value[item.reference] = record.get(item.reference);
        // }
        vm.set("activeFilter", Ext.merge(vm.get("activeFilter"), value));
    }
});
