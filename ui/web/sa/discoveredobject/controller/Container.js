//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.controller.Container");

Ext.define("NOC.sa.discoveredobject.controller.Container", {
    extend: "Ext.app.ViewController",
    alias: "controller.sa.discoveredobject.container",

    onClearSearchField: function(searchField) {
        searchField.setValue("");
        searchField.getTrigger("clear").hide();
    },
    onChangeSearchField: function(searchField) {
        if(searchField.getValue()) {
            searchField.getTrigger("clear").show();
        } else {
            searchField.getTrigger("clear").hide();
        }
    },
    onToggleFilter: function(_, pressed) {
        this.getViewModel().set("isFilterOpen", pressed);
    },
    onBeforeRenderGroupAction: function(button) {
        this.fillMenu(button, "/sa/discoveredobject/action_lookup/", "/sa/discoveredobject/actions/send_event/");
    },
    onBeforeRenderScanRecord: function(button) {
        this.fillMenu(button, "/sa/discoveredobject/template_lookup/", "/sa/discoveredobject/actions/sync_records/");
    },
    fillMenu: function(button, url, actionUrl) {
        var actionFn = function(args, actionUrl) {
            console.log("args : ", args, actionUrl);
            Ext.Ajax.request({
                url: actionUrl,
                method: "POST",
                // jsonData: defaultHandler.args,
                success: function(response) {
                    NOC.info(button.text + __(" : Success"));
                },
                failure: function() {
                    NOC.error(button.text + __(" : Failed"));
                }
            });
        };

        Ext.Ajax.request({
            url: url,
            success: function(response) {
                var me = this,
                    defaultHandler, menuItems,
                    data = Ext.decode(response.responseText);

                defaultHandler = data.filter(function(el) {
                    return el.is_default
                })[0];
                button.setHandler(function() {
                    actionFn(defaultHandler.args, actionUrl);
                }, me);
                button.getMenu().removeAll();
                menuItems = data.filter(function(el) {
                    return !el.is_default
                }).map(function(el) {
                    return {
                        text: el.label,
                        handler: function() {
                            actionFn(el.args, actionUrl);
                        }
                    }
                });
                Ext.Array.each(menuItems, function(item) {
                    button.getMenu().add(item);
                });
            },
            failure: function() {
                NOC.error(button.text + __(" : Failed to get data for menu items"));
            }
        });
    },
});
