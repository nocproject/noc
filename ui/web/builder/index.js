const build_css = require('./build_css');
const build_js = require('./build_js');
const load_packages = require('./load_packages');

load_packages();
build_css();
build_js();
