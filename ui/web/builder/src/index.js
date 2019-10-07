const version = '0.0.3';
const build_css = require('./build_css');
const build_js = require('./build_js');
const fs = require('fs');
const load_packages = require('./load_packages');
const tar = require('tar-fs');
const zlib = require("zlib");

const distDir = 'dist';
const destDir = `${distDir}/ui/pkg/noc`;
// const args = process.argv.slice(2);
const themes = ['gray', 'noc'];
const queue = [
    ...load_packages('../../../requirements/web.json'),
    ...load_packages('../../../requirements/theme-noc.json')
];

const template = '{% if setup.theme == "{theme}" %}\n' +
    '<link rel="stylesheet" type="text/css" href="/ui/pkg/noc/bundle_app_{app_hash}_{theme}.min.css " />\n' +
    '<script type="text/javascript" src="/ui/pkg/noc/bundle_vendor_{vendor_hash}_{theme}.min.js"></script>\n' +
    '{% endif %}';

fs.mkdirSync(destDir, {recursive: true});

// ToDo test theme-noc, perhaps need other resources!
function assets(dest, theme) {
    const assetDirs = [
        '.pkg_cache/ui/pkg/fontawesome/fonts'
    ];
    return assetDirs.map(dir =>
        new Promise((resolve, reject) => {
            const name = dir.substr(dir.lastIndexOf('/') + 1);
            tar.pack(dir).pipe(
                tar.extract(`${dest}/${name}`, {
                    finish: () => resolve({name: name, hash: null})
                })
            );
        })
    );
}

function writeDesktop(data) {
    const dest = `${distDir}/services/web/apps/main/desktop/templates`;
    fs.mkdirSync(dest, {recursive: true});
    fs.writeFileSync(`${dest}/desktop.html`, data);
}

function hash(values, file, theme) {
    for(let i = 0; i < values.length; i++) {
        if(values[i].file === file && values[i].theme === theme) {
            return values[i].hash;
        }
    }
    return null;
}

Promise.all(queue).then(values => {
        let stages = [
            ...assets(destDir, themes),
            ...build_css(destDir, themes),
            ...build_js.application('bundle_noc', destDir, themes),
            ...build_js.vendor('bundle_vendor', destDir, themes),
            ...build_js.boot('bundle_boot', destDir, themes),
        ];
        Promise.all(stages).then(values => {
                const output = fs.createWriteStream(`ui-web@${version}.tgz`);
                let content = fs.readFileSync('src/desktop.html').toString();
                let themeSpecific = [];
                // make desktop.html add hash
                values.filter(value => value.hash | value.theme === '')
                .forEach(value => {
                    const file = value.name.replace(/{hash}/, value.hash);
                    content = content.replace(value.name, file);
                });
                // add hash to theme specific files
                themes.forEach(theme => {
                    const appHash = hash(values,'bundle_app_{hash}', theme);
                    const vendorHash = hash(values, 'bundle_vendor_{hash}', theme);
                    let body;
                    body = template.replace(/{theme}/g, theme);
                    body = body.replace(/{app_hash}/, appHash);
                    themeSpecific.push(body.replace(/{vendor_hash}/, vendorHash));
                });
                content = content.replace(/{theme_specific}/, themeSpecific.join('\n'));
                writeDesktop(content);
                tar.pack(distDir).pipe(zlib.createGzip()).pipe(output);
                console.log('Done');
            },
            error => {
                console.error(error);
            }
        ).catch(console.error);
    },
    error => {
        console.error(error);
    }
);
