//---------------------------------------------------------------------
//  Inspector abstract class
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.inv.map.inspectors.Inspector');

Ext.define('NOC.inv.map.inspectors.Inspector', {
    extend: 'Ext.panel.Panel',

    title: undefined,
    scrollable: 'vertical',
    bodyStyle: {
        background: '#c0c0c0'
    },
    defaults: {
        padding: 4
    },

    preview: function(name, segmentId, objectId) {
        var url = '/inv/map/' + segmentId + '/info/' + name + '/';

        if(name === 'managedobject' || name === 'link') {
            url += objectId.split("-")[0] + '/';
        }

        Ext.Ajax.request({
            url: url,
            method: "GET",
            scope: this,
            success: function(response) {
                var values = Ext.decode(response.responseText);
                this.update(values);
                this.enableButtons(values);
            }
        });
    },

    enableButtons: Ext.emptyFn
});