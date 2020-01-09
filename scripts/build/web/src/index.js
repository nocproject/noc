const version = '0.1.0';
const build_css = require('./build_css');
const build_js = require('./build_js');
const fs = require('fs');
const load_packages = require('./load_packages');
const tar = require('tar-fs');
const zlib = require("zlib");

const distDir = '../../../dist';
let packageDir = `/ui/pkg/web`;
const destDir = `${distDir}${packageDir}`;
// const args = process.argv.slice(2);
const themes = ['gray', 'noc'];
const langs = ['ru', 'en'];
const queue = [
    ...load_packages('../../../requirements/web.json'),
    ...load_packages('../../../requirements/theme-noc.json')
];

const themeTemplate = '{% if setup.theme == "{theme}" %}\n' +
    `<link rel="stylesheet" type="text/css" href="${packageDir}/app.{app_hash}.{theme}.css" />\n` +
    `<script type="text/javascript" src="${packageDir}/vendor.{vendor_hash}.{theme}.js"></script>\n` +
    '{% endif %}';

const bundleTemplate = `<script type="text/javascript" src="${packageDir}/boot.{hash}.js"></script>\n` +
    '<!-- Include the translations -->\n' +
    `<script type="text/javascript" src="/ui/web/locale/{{ language }}/ext-locale-{{ language }}.js"></script>\n` +
    `<script type="text/javascript" src="${packageDir}/app.{hash}.js"></script>\n`;

fs.mkdirSync(destDir, {recursive: true});
fs.mkdirSync(`${destDir}.debug`, {recursive: true});

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

function writeBundle(name, data) {
    fs.writeFileSync(`${destDir}/${name}.html`, data);
}

function hash(values, file, theme) {
    for(let i = 0; i < values.length; i++) {
        if(values[i].name === file && values[i].theme === theme) {
            return values[i].hash;
        }
    }
    return null;
}

Promise.all(queue).then(values => {
        let stages = [
            // ...assets(destDir, themes),
            ...build_css(destDir, themes),
            ...build_js.application('app', destDir, themes),
            ...build_js.vendor('vendor', destDir, themes),
            ...build_js.boot('boot', destDir, themes),
        ];
        // make index.html add hash
        Promise.all(stages).then(values => {
                const output = fs.createWriteStream(`ui-web.tgz`);
                langs.forEach(lang => {
                    themes.forEach(theme => {
                        let content = fs.readFileSync('src/desktop.html').toString();
                        content = content.replace(/{language}/g, lang);
                        content = content.replace(/{theme}/g, theme);
                        content = content.replace(/{packageDir}/g, packageDir);
                        values.filter(value => value.hash | value.theme === '')
                        .forEach(value => {
                            const file = value.name.replace(/{hash}/, value.hash);
                            content = content.replace(value.name, file);
                        });
                        const appHash = hash(values, 'app.{hash}', theme);
                        const vendorHash = hash(values, 'vendor.{hash}', theme);
                        content = content.replace(/{theme}/g, theme);
                        content = content.replace(/{app_hash}/, appHash);
                        content = content.replace(/{vendor_hash}/, vendorHash);
                        writeBundle(`index.${theme}.${lang}`, content);
                    });
                });
                fs.copyFileSync(`${destDir}/index.gray.ru.html`, `${destDir}/index.html`);
                // tar.pack(distDir).pipe(zlib.createGzip()).pipe(output);
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
