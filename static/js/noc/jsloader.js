_noc_loaded_scripts = {};

function load_scripts(urls, scope, callback) {
    var load = function(u, cb) {
        var url = u.pop();
        if(url == undefined)
            cb.call(scope);
        else {
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
                var next = function() {load(u, cb);}
                script_node.onreadystatechange = next;
                script_node.onload = next;
                _noc_loaded_scripts[url] = true;
            }
        }
    }
    // Begin loading
    load(urls.reverse(), callback);
}
