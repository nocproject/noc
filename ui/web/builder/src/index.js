const build_css = require('./build_css');
const build_js = require('./build_js');
const fs = require('fs');
const load_packages = require('./load_packages');
const tar = require('tar-fs');

const destDir = 'dist';
// const args = process.argv.slice(2);
const themeName = 'gray';
let queue = load_packages();

fs.mkdirSync(destDir);

// ToDo test theme-noc, perhaps need other resources!
function assets(theme) {
    const assetDirs = [
        '.pkg_cache/ui/pkg/fontawesome/fonts',
        `.pkg_cache/ui/pkg/extjs/classic/theme-${theme}/resources/images`
    ];
    assetDirs.forEach(dir => {
        const name = dir.substr(dir.lastIndexOf('/') + 1);
        tar.pack(dir).pipe(tar.extract(`${destDir}/${name}`));
    });
}

Promise.all(queue)
.then(values => {
        console.log(values);
        console.log('loading done');
        assets(themeName);
        build_css(themeName);
        build_js.application('bundle_noc', themeName);
        build_js.vendor('bundle_vendor', themeName);
        build_js.boot('bundle_boot', themeName);
        fs.copyFileSync('src/desktop.html', `${destDir}/desktop.html`);
    },
    error => {
        console.error(error);
    })
.finally(() => console.log('Done'));
