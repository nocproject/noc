//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.grids.ContainerController");
Ext.define("NOC.fm.alarm.view.grids.ContainerController", {
    extend: "Ext.app.ViewController",
    alias: "controller.fm.alarm.container",
    initViewModel: function() {
        var profiles = Ext.create("NOC.fm.alarm.store.Profile", {autoLoad: false});
        profiles.load({
            scope: this,
            callback: function(records) {
                this.getViewModel().set("total.selected", Ext.Array.map(records, function(item) {
                    return Ext.merge(item.data, {summary: 0});
                }, this));
            }
        });
    },
    onReload: function(grid) {
        grid.getStore().reload();
    },
    onStoreLoaded: function(self, store) {
        this.getViewModel().set("total.alarmsTotal", store.getTotalCount());
    },
    onSelectAlarm: function(grid, record) {
        this.fireViewEvent("fmAlarmSelectItem", record);
    },
    onStoreSelectionChange: function(store) {
        var selection = Ext.Array.flatten(Ext.Array.map(store.getSelection(), function(item) {
                return item.get("total_subscribers").concat(item.get("total_services"))
            })),
            selectionSummary = Ext.Array.reduce(selection, function(prev, item) {
                if(prev.hasOwnProperty(item.profile)) {
                    prev[item.profile] += item.summary
                } else {
                    prev[item.profile] = item.summary
                }
                return prev;
            }, {}),
            selected = this.getViewModel().get("total.selected");
        this.getViewModel().set("total.selected", Ext.Array.map(selected, function(item) {
            return Ext.merge(item, {
                summary: (selectionSummary.hasOwnProperty(item.id)) ? selectionSummary[item.id] : 0
            });
        }));
    },
    //
    generateSummaryHtml: function(records, filter, force) {
        var isEmpty = function(array) {
                if(!array) {
                    return true;
                }
                return array.length === 0;
            },
            isEqual = function(item1, item2) {
                return item1.id === item2.id;
            },
            intersect = function(array1, array2) {
                var intersection = [], i, j, len1, len2;
                if(isEmpty(array1) || isEmpty(array2)) {
                    return [];
                }
                len1 = array1.length;
                len2 = array2.length;
                for(i = 0; i < len1; i++) {
                    for(j = 0; j < len2; j++) {
                        if(isEqual(array1[i], array2[j])) {
                            intersection.push(array1[i]);
                        }
                    }
                }
                return intersection;
            },
            contains = function(array, element) {
                var i, len = array.length;
                for(i = 0; i < len; i++) {
                    if(isEqual(element, array[i])) {
                        return true;
                    }
                }
                return false;
            },
            minus = function(array1, array2) {
                var acc = [], i, len1;
                if(isEmpty(array1)) {
                    return [];
                }
                len1 = array1.length;
                for(i = 0; i < len1; i++) {
                    if(!contains(array2, array1[i])) {
                        acc.push(array1[i]);
                    }
                }
                return acc;
            },
            summaryHtml = function(records) {
                var summaryHtml = "",
                    summarySpan = "<span class='x-summary'>",
                    badgeSpan = "<span class='x-display-tag'>",
                    closeSpan = "</span>",
                    sortFn = function(a, b) {
                        return (a.display_order > b.display_order) ? 1 : -1;
                    },
                    iconTag = function(cls, title) {
                        return "<i class='" + cls + "' title='" + title + "'></i>";
                    },
                    badgeTag = function(value) {
                        return badgeSpan + value + closeSpan;
                    },
                    profileHtml = function(profile) {
                        return iconTag(profile.icon, profile.label)
                            + badgeTag(profile.summary);
                    },
                    profilesHtml = function(profiles) {
                        if(profiles.length) {
                            summaryHtml += summarySpan;
                            summaryHtml += profiles.map(profileHtml).join("");
                            summaryHtml += closeSpan;
                        }
                    };
                profilesHtml(Ext.Array.sort(records, sortFn));
                return summaryHtml;
            };
        if(!Ext.Object.isEmpty(filter)) {
            if(filter.include) {
                return summaryHtml(intersect(records, filter.array));
            } else {
                return summaryHtml(minus(records, filter.array));
            }
        }
        if(force) {
            return summaryHtml(records);
        }
        // use html from backend
        return "";
    }
});