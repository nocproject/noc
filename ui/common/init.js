NOC = {
    // Configuration
    config: {

    },
    // Create namespace
    namespace: function(ns) {
        var p = window,
            parts = ns.split("."),
            i, pn;
        for(i in parts) {
            pn = parts[i];
            if(p[pn] === undefined) {
                p[pn] = {};
            }
            p = p[pn];
        }
    }
};