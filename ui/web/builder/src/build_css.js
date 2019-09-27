// not found
// ui/web/css/highlight.css
// ui/web/css/diff.css
// ui/web/css/pygments.css

const fs = require('fs');
const postcss = require('postcss');
// processors
const atImport = require('postcss-import');
const mqpacker = require('css-mqpacker');
const cssnano = require('cssnano');
const autoprefixer = require('autoprefixer');
const copyAssets = require('postcss-copy-assets');

const bundleName = 'bundle_app';
const prodName = `dist/${bundleName}.min.css`;

const build = function() {
    const processors = [
        atImport,
        autoprefixer,
        mqpacker,
        copyAssets({ base: 'dist'}),
        cssnano
    ];
    fs.readFile('src/app.css', (err, css) => {
        postcss(processors)
        .process(css, { from: 'src/app.css', to: prodName })
        .then(result => {
            fs.writeFile(prodName, result.css, () => true);
            if ( result.map ) {
                fs.writeFile(`${prodName}.map`, result.map, () => true)
            }
        })
    });
};

module.exports = build;
