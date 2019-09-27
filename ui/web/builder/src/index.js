const build_css = require('./build_css');
const build_js = require('./build_js');
const fs = require('fs');
const load_packages = require('./load_packages');
const tar = require('tar-fs');

const destDir = 'dist';
const assetDirs = [
    '.pkg_cache/ui/pkg/fontawesome/fonts',
    '.pkg_cache/ui/pkg/extjs/classic/theme-gray/resources/images'
];
let queue = load_packages();

fs.mkdirSync(destDir);
Promise.all(queue)
.then(values => {
        console.log(values);
        console.log('loading done');
        assetDirs.forEach(dir => {
            const name = dir.substr(dir.lastIndexOf('/') + 1);
            tar.pack(dir).pipe(tar.extract(`${destDir}/${name}`));
        });
        build_css();
        build_js.application('bundle_noc');
        build_js.vendor('bundle_vendor');
        fs.copyFileSync('src/desktop.html', `${destDir}/desktop.html`);
    },
    error => {
        console.error(error);
    })
.finally(() => console.log('Done'));
