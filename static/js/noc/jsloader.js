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
