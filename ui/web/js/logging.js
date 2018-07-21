//
// Create console.* stub if missed
//
if (!window.console) {
    window.console = {};
}
if(!window.console.log) {
    window.console.log = function() {};
}
if(!window.console.debug) {
    window.console.debug = function() {};
}
if(!window.console.info) {
    window.console.info = function() {};
}
if(!window.console.warn) {
    window.console.warn = function() {};
}
if(!window.console.error) {
    window.console.error = function() {};
}
