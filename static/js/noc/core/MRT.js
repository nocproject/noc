//---------------------------------------------------------------------
// Map/Reduce task abstraction
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.MRT");

Ext.define("NOC.core.MRT", {
    mixins: {
        observable: 'Ext.util.Observable'
    },
    // scope: null,
    url: null,
    taskId: null,
    success: null,
    failure: null,

    constructor: function(config) {
        config = config || {};
        Ext.apply(this, config);
        this.addEvents(
            "beforetask",
            "taskcomplete",
            "taskexception",
            "check"
        );
        this.mixins.observable.constructor.call(this);
    },
    // Run new MRT
    run: function() {
        var me = this;

        if(me.fireEvent("beforetask", me) !== false ) {
            Ext.Ajax.request({
                url: me.url,
                method: "POST",
                scope: me,
                jsonData: {
                    selector: me.selector
                },
                success: function(response) {
                    this.taskId = Ext.decode(response.responseText);
                    me.checkMRT();
                },
                failure: function() {
                    this.fireEvent("taskexception", this);
                    Ext.callback(me.failure, me.scope, []);
                }
            });
        }
    },
    // Check running MRT
    checkMRT: function() {
        var me = this;

        Ext.Ajax.request({
            url: me.url + me.taskId + "/",
            method: "GET",
            scope: me,
            success: function(response) {
                var r = Ext.decode(response.responseText);
                if(r.ready) {
                    // MRT Finished
                    this.fireEvent("taskcomplete", this, [r.result]);
                    Ext.callback(me.success, me.scope, [r.result]);
                } else
                    // Wait and recheck
                    Ext.defer(Ext.bind(me.checkMRT, me), 1000);
            },
            failure: function() {
                this.fireEvent("taskexception", this);
                Ext.callback(me.failure, me.scope);
            }
        });
    }
});
