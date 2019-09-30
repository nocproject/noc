const fs = require('fs');
const postcss = require('postcss');
// processors
const atImport = require('postcss-import');
const mqpacker = require('css-mqpacker');
const cssnano = require('cssnano');
const autoprefixer = require('autoprefixer');
const copyAssets = require('postcss-copy-assets');

const bundleName = 'bundle_app';

const build = function(theme) {
    const source = 'src/application.css';
    const prodName = `dist/${bundleName}_${theme}.min.css`;
    const processors = [
        atImport,
        // autoprefixer,
        mqpacker,
        copyAssets({base: 'dist'}),
        cssnano
    ];
    fs.readFile(source, (err, css) => {
        postcss(processors)
        .process(css.toString().replace(/{theme-name}/g, theme), {from: source, to: prodName})
        .then(result => {
            fs.writeFile(prodName, result.css, () => true);
            if(result.map) {
                fs.writeFile(`${prodName}.map`, result.map, () => true)
            }
        })
    });
};

module.exports = build;
