_noc_loaded_scripts = {};
window._noc_load_callback = null;

function load_scripts(urls, scope, callback) {
    var load = function(u, cb) {
        var url = u.pop();
        if(url == undefined)
            cb.call(scope); // All scripts loaded
        else {
            // URL starting with "@" will call _noc_load_callback on load
            var next_on_load = url.substring(0, 1) != "@";
            if(!next_on_load)
                url = url.substring(1);
            if(_noc_loaded_scripts[url]) {
                // Already loaded
                cb.call(scope);
            } else {
                console.log("Loading script " + url);
                var script_node = document.createElement("script");
                script_node.type = "text/javascript";
                script_node.src = url;

                var head = document.getElementsByTagName("head")[0];
                head.appendChild(script_node);
                window._noc_load_callback = function() {load(u, cb);};
                if(next_on_load) {
                    script_node.onreadystatechange = function() {
                        if(this.readyState == "complete")
                            cb.call(scope);
                    };
                    script_node.onload = window._noc_load_callback;
                }
                _noc_loaded_scripts[url] = true;
            }
        }
    };
    // Begin loading
    load(urls.reverse(), callback);
}

function new_load_scripts(urls, scope, callback) {
    var head = document.getElementsByTagName("head")[0],
        load_script = function(url, callback) {
            // Already loaded?
            if(_noc_loaded_scripts[url]) {
                console.log("Using cached script " + url);
                callback();
            } else {
                console.log("Loading script " + url);
                var script_node = document.createElement("script");
                script_node.type = "text/javascript";
                script_node.src = url;
                script_node.onload = function() {callback(); };
                script_node.onreadystatechange = function() {
                    if(this.readyState == "complete") {
                        callback();
                    }
                };
                head.appendChild(script_node);
            }
        },
        load_chain = function(urls) {
            console.log("Load chain", urls);
            load_script(urls[0], function() {
                _noc_loaded_scripts[urls[0]] = true;
                if(urls.length === 1) {
                    callback.call(scope);
                } else {
                    load_chain(urls.slice(1));
                }
            });
        };
    load_chain(urls);
}
