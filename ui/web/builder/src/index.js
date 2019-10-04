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
const themes = ['gray', 'noc'];
const queue = [
    ...load_packages('../../../requirements/web.json'),
    ...load_packages('../../../requirements/theme-noc.json')
];

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

Promise.all(queue).then(values => {
        console.log(values);
        let stages = [
            ...assets(destDir, themes),
            ...build_css(destDir, themes),
            ...build_js.application('bundle_noc', destDir, themes),
            ...build_js.vendor('bundle_vendor', destDir, themes),
            ...build_js.boot('bundle_boot', destDir, themes),
        ];
        Promise.all(stages).then(values => {
                console.log(values);
                const output = fs.createWriteStream(`ui-web@${version}.tgz`);
                let content = fs.readFileSync('src/desktop.html').toString();

                // make desktop.html only for gray theme
                values
                .filter(value => value.hash | value.theme === '' | value.theme === 'gray')
                .forEach(value => {
                    const file = value.name.replace(/{hash}/, value.hash);
                    content = content.toString().replace(value.name, file);
                });
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
