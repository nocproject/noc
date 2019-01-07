//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.ContainerModel");

Ext.define("NOC.fm.alarm.view.grids.ContainerModel", {
    extend: "Ext.app.ViewModel",
    alias: "viewmodel.fm.alarm.container",
    data: {
        total: {
            alarmsTotal: 0,
            selected: []
        }
    },
    formulas: {
        totalCount: function(get) {
            var selected = get("total.selected"),
                displayFilter = get("displayFilter.hasProfiles"),
                summary = this.getView().getController().generateSummaryHtml(
                    selected.filter(function(item) {
                        return item.summary > 0;
                    }),
                    displayFilter,
                    true
                );
            summary = "<div>" + summary + "</div>";
            return "<div style='display: flex; justify-content: space-between'>"
                + summary
                + "<div>" + __("Total: ") + get("total.alarmsTotal") + "</div>"
                + "</div>";
        }
    }
});