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
                this.getViewModel().set("total.selected", Ext.Array.map(records, function(record) {
                    return Ext.merge(record.clone().data, {summary: 0});
                }, this));
                this.getViewModel().set("total.selectionFiltered", Ext.Array.map(records, function(record) {
                    return Ext.merge(record.clone().data, {summary: 0});
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
    onStoreSelectionChange: function(grid) {
        var selection = Ext.Array.flatten(Ext.Array.map(grid.getSelection(), function(item) {
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
        this.getView().up("[reference=fmAlarm]").getController().activeSelectionFiltered();
        this.getViewModel().set("total.objects", Ext.Array.reduce(grid.getSelection(), function(prev, item) {
            return prev + item.get("total_objects");
        }, 0));
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
                        if(a.display_order > b.display_order) {
                            return 1;
                        } else {
                            return -1;
                        }
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
    },
    addGroupComment: function() {
        var grid = this.lookupReference("fmAlarmActive"),
            ids = grid.getSelection().map(function(alarm) {
                return alarm.id
            }),
            view = this.getView(),
            msg = new Ext.window.MessageBox().prompt(
                __("Set group comment"),
                __("Please enter comment"),
                function(btn, text) {
                    if(btn === "ok") {
                        Ext.Ajax.request({
                            url: "/fm/alarm/comment/post/",
                            method: "POST",
                            jsonData: {
                                ids: ids,
                                msg: text
                            },
                            success: function() {
                                view.up("[itemId=fmAlarm]").getController().reloadActiveGrid();
                                NOC.info(__("Success"));
                            },
                            failure: function() {
                                NOC.error(__("Failed to save group comment"));
                            }
                        });
                    }
                },
                this
            );
        msg.setWidth(500);
    },
    addGroupEscalate: function() {
        var grid = this.lookupReference("fmAlarmActive"),
            ids = grid.getSelection().map(function(alarm) {
                return alarm.id
            });
        Ext.Ajax.request({
            url: "/fm/alarm/escalate/",
            method: "POST",
            jsonData: {
                ids: ids
            },
            scope: this,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                if(data.status) {
                    NOC.info(_("Escalated"));
                } else {
                    NOC.error(__("Escalate failed : ") + (data.hasOwnProperty("error") ? data.error : "unknowns error!"));
                }
            },
            failure: function() {
                NOC.error(__("Escalate failed"));
            }
        });
    },
    onActiveResetSelection: function() {
        this.lookupReference("fmAlarmActive").setSelection(null);
    },
    createMaintenance: function() {
        var selection = this.lookupReference("fmAlarmActive").getSelection(),
            objects = selection.map(function(alarm) {
                return {
                    object: alarm.get("managed_object"),
                    object__label: alarm.get("managed_object__label")
                }
            }),
            args = {
                direct_objects: objects,
                subject: __("created from alarms list at ") + Ext.Date.format(new Date(), "d.m.Y H:i P"),
                contacts: NOC.email ? NOC.email : NOC.username,
                start_date: Ext.Date.format(new Date(), "d.m.Y"),
                start_time: Ext.Date.format(new Date(), "H:i"),
                stop_time: "12:00",
                suppress_alarms: true
            };
        Ext.create("NOC.maintenance.maintenancetype.LookupField")
            .getStore()
            .load({
                params: {__query: "РНР"},
                callback: function(records) {
                    if(records.length > 0) {
                        Ext.apply(args, {
                            type: records[0].id
                        })
                    }
                    NOC.launch("maintenance.maintenance", "new", {
                        args: args
                    });
                }
            });
    },
    openAlarmDetailReport: function() {
        var selection = this.lookupReference("fmAlarmActive").getSelection(),
            ids = selection.map(function(alarm) {
                return alarm.id
            });
        NOC.launch("fm.reportalarmdetail", "new", {ids: ids});

    },
    onNewBasket: function(container) {
        this.openBasket("new", container);
    },
    onUpdateBasket: function(container, record) {
        this.openBasket("update", container, record);
    },
    onUpdateOpenBasket: function(container, record) {
        this.openBasket("data-update", container, record);
    },
    openBasket: function(action, container, record) {
        var me = this,
            title = "NEW",
            form = container.up().down("[itemId=fmAlarmBasketForm]");

        form.removeAll();
        form.add(
            {
                xtype: "textfield",
                fieldLabel: __("Name"),
                anchor: "100%",
                value: Ext.isEmpty(record) ? __("Basket at ") + Ext.Date.format(new Date(), "d.m.Y H:i P") : record.get("label"),
            }
        );
        switch(action) {
            case "new": {
                form.add(me.createCondition({managed_object: null, address: null, ip: null}, 0));
                this.setFormTitle(__("New") + " " + __("Basket"), {id: "NEW"});
                this.toggleBasket(container);
                break;
            }
            case "data-update": {
                if(Ext.isEmpty(record)) { // click on x
                    this.setFormTitle(__("New") + " " + __("Basket"), {id: "NEW"});
                    form.add(me.createCondition({managed_object: null, address: null, ip: null}, 0));
                } else {
                    title = record.get("label");
                    Ext.each(record.get("conditions"), function(condition, index) {
                        form.add(me.createCondition(condition, index));
                    });
                    me.updateBasketGrid(form, record.get("conditions")[0].managed_object);
                    this.setFormTitle(__("Edit") + " " + __("Basket"), {id: record.get("id")});
                }
                break;
            }
            case "update": {
                title = record.get("label");
                Ext.each(record.get("conditions"), function(condition, index) {
                    form.add(me.createCondition(condition, index));
                });
                me.updateBasketGrid(form, record.get("conditions")[0].managed_object);
                this.setFormTitle(__("Edit") + " " + __("Basket"), {id: record.get("id")});
                this.toggleBasket(container);
                break;
            }
        }
    },
    onBasketClose: function(container) {
        this.toggleBasket(container);
    },
    toggleBasket: function(component) {
        var alarmList = component.up("[reference=fmAlarmList]"),
            container = alarmList.lookupReference("fmAlarmListContainer"),
            form = alarmList.lookupReference("fmAlarmBasket");
        if(container.isHidden()) {
            container.show();
            form.hide();
        } else {
            container.hide();
            form.show();
        }
    },
    createCondition: function(condition, index) {
        var me = this;
        return {
            xtype: "fieldset",
            layout: "anchor",
            title: __("Condition") + " " + (index + 1),
            itemId: "condition" + index,
            defaults: {
                anchor: "100%",
            },
            border: true,
            collapsible: true,
            items: [
                {
                    xtype: "container",
                    layout: "hbox",
                    defaults: {
                        xtype: "textfield",
                        allowBlank: true,
                        labelAlign: "top",
                        margin: "0 10",
                        flex: 1,
                        listeners: {
                            change: {
                                buffer: 500, // Задержка в миллисекундах
                                fn: function(field, newValue, oldValue) {
                                    if(newValue.length >= 3) { // Минимальное количество символов
                                        me.updateBasketGrid(field, newValue);
                                        console.log("Сработало событие после ввода символа:", index, field.name, newValue);
                                    }
                                }
                            }
                        }
                    },
                    items: [
                        {
                            name: "name",
                            fieldLabel: "Managed Object",
                            value: condition.managed_object
                        },
                        {
                            name: "address",
                            fieldLabel: "Address",
                            value: condition.address
                        },
                        {
                            name: "ip",
                            fieldLabel: "IP",
                            value: condition.ip
                        }
                    ],
                },
                {
                    xtype: "container",
                    layout: {
                        type: "hbox",
                        pack: "end"
                    },
                    margin: "0 0 10 0",
                    defaults: {
                        margin: "10 10 0 0"
                    },
                    items: [
                        {
                            xtype: "button",
                            text: __("Add"),
                            handler: function(button) {
                                var form = button.up("[itemId=fmAlarmBasketForm]"),
                                    index = Math.max(...Ext.Array.map(
                                        Ext.Array.filter(form.getRefItems(), function(fieldSet) {return Ext.String.startsWith(fieldSet.itemId, "condition");}),
                                        function(fieldSet) {return parseInt(fieldSet.getItemId().replace("condition", ""));}
                                    )) + 1;
                                form.add(me.createCondition({managed_object: null, address: null, ip: null}, index));
                            }
                        },
                        {
                            xtype: "button",
                            text: __("Remove"),
                            handler: function(button) {
                                button.up("[itemId=fmAlarmBasketForm]").remove(button.up("[itemId=condition" + index + "]"));
                            }
                        }
                    ],
                }
            ],
        }
    },
    setFormTitle: function(tpl, data) {
        var t = "<b>" + Ext.String.format(tpl, __("Basket")) + "</b>",
            formTitle = this.view.down("[itemId=formTitle]"),
            itemId = data.id;
        if(itemId !== "NEW" && itemId !== "CLONE") {
            itemId = "<b>ID:</b>" + itemId;
        } else {
            itemId = "<b>" + itemId + "</b>";
        }
        t += "<span style='float:right'>" + itemId + "</span>";
        formTitle.update(t);
    },
    updateBasketGrid: function(container, value) {
        var store = container.up("[reference=fmAlarmBasket]").down("[itemId=fmAlarmBasketGrid]").getStore();

        store.getProxy().setExtraParam("__query", value);
        store.load();
    }
});
