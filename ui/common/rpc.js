var API = (function() {
    var r = {
        _base_url: "/api/" + document.location.pathname.split("/")[2] + "/api/",
        tid: 0
    };
    for(var api in SDL) {
        if(!SDL.hasOwnProperty(api)) {
            continue;
        }
        r[api] = {};
        for(var mi in SDL[api]) {
            var method = SDL[api][mi];
            r[api][method] = (function(r, api, method) {
                return function() {
                    var defer = webix.promise.defer();
                    webix.ajax().headers({
                        "Content-Type": "text/json"
                    }).post(
                        r._base_url + api + "/",
                        JSON.stringify({
                            id: r.tid++,
                            jsonrpc: "2.0",
                            method: method,
                            params: Array.prototype.slice.call(arguments)
                        })
                    ).then(function(resp) {
                        var data = resp.json();
                        if(!data.error) {
                            defer.resolve(data.result);
                        } else {
                            defer.reject(data.error);
                        }
                    }, function(err) {
                        defer.reject(err);
                    });
                    return defer;
                };
            })(r, api, method);
        }
    }
    return r;
})();


webix.proxy.rpc = {
    $proxy: true,

    load: function(view, callback, params) {
        var r = {dynamic: true},
            state = {},
            source = this.source,
            i, j, p, v, method;
        if(view.getState) {
            state = view.getState();
        }
        if(state.sort) {
            // Todo: Convert to list
            r.sort = state.sort;
        }
        // Strip query from url
        if((i = source.indexOf("?")) !== -1) {
            p = source.substring(i + 1).split("&");
            // Process parameters
            for(j in p) {
                v = p[j].split("=");
                if((v[0] === "start") || (v[0] === "count")) {
                    r[v[0]] = parseInt(v[1]);
                }
            }
            source = source.substring(0, i);
        }
        if(source.substring(source.length - 7) === ":lookup") {
            // Combo lookup
            source = source.substring(0, source.length - 7);
            method = "lookup_items";
        } else {
            method = "get_items";
        }
        API[source][method](r).then(
            function(data) {
                webix.ajax.$callback(
                    view,
                    callback,
                    JSON.stringify(data),  // Need to pass JSON object
                    data
                );
            }
        );
    }
};
