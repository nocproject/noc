//---------------------------------------------------------------------
// NOC dynamic dashboard
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
'use strict';

var window, document, ARGS, $, jQuery, moment, kbn;

return function(callback) {
    // Build arguments
    var args = {
        dashboard: ARGS.dashboard,
        id: ARGS.id
    };
    // Get dashboard configuration
    $.ajax({
        method: "GET",
        url: "/pm/ddash/?" + $.param(args)
    }).done(function(result) {
        callback(result);
    });
}
