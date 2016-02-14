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
    },

        //
    // Validation rules
    //
    rules: {
        //
        // Check regular expression
        //
        regex: function(re) {
            return function(value) {
                return re.test(value);
            }
        }
    },
    msg: {
        started: function(message) {
            webix.message({
                type: "started",
                text: message,
                expire: 2000
            });
        },
        complete: function(message) {
            webix.message({
                type: "complete",
                text: message,
                expire: 2000
            });
        },
        failed: function(message) {
            webix.message({
                type: "failed",
                text: message,
                expire: 2000
            });
        },
        info: function(message) {
            webix.message({
                type: "info",
                text: message,
                expire: 2000
            });
        }
    },
    format: {
        lookup: function(v) {
            if(v.id === undefined) {
                return v;
            } else {
                return v.value;
            }
        }
    },
    notification: function(v) {
        if(!("Notification" in window)) {
            return; // Not supported
        }
        if(Notification.permission === "granted") {
            new Notification(v);
        } else if (Notification.permission !== "denied") {
            Notification.requestPermission(function(permission) {
                if(permission === "granted") {
                    new Notification(v);
                }
            });
        }
    }
};