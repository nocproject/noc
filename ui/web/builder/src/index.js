const version = '0.0.2';
const build_css = require('./build_css');
const build_js = require('./build_js');
const fs = require('fs');
const load_packages = require('./load_packages');
const tar = require('tar-fs');
const zlib = require("zlib");

const distDir = 'dist';
const destDir = `${distDir}/ui/pkg/noc`;
// const args = process.argv.slice(2);
const themeName = 'gray';
let queue = load_packages();

fs.mkdirSync(destDir, {recursive: true});

// ToDo test theme-noc, perhaps need other resources!
function assets(dest, theme) {
    const assetDirs = [
        '.pkg_cache/ui/pkg/fontawesome/fonts',
        `.pkg_cache/ui/pkg/extjs/classic/theme-${theme}/resources/images`
    ];
    assetDirs.forEach(dir => {
        const name = dir.substr(dir.lastIndexOf('/') + 1);
        tar.pack(dir).pipe(tar.extract(`${dest}/${name}`));
    });
}

Promise.all(queue)
.then(values => {
        console.log(values);
        console.log('loading done');
        assets(destDir, themeName);
        build_css(destDir, themeName);
        build_js.application('bundle_noc', destDir, themeName);
        build_js.vendor('bundle_vendor', destDir, themeName);
        build_js.boot('bundle_boot', destDir, themeName);
        fs.copyFileSync('src/desktop.html', `${destDir}/desktop.html`);
    },
    error => {
        console.error(error);
    })
.finally(() => {
    const output = fs.createWriteStream(`ui-web-${version}.tgz`);
    tar.pack(distDir).pipe(zlib.createGzip()).pipe(output);
    console.log('Done');
});
