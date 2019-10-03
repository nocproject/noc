const loader = require('./loader');
const UglifyJS = require("uglify-js");
const fs = require('fs');
const apps = require('./applications');
const vendors = require('./vendors');
const boots = require('./boots');

const cache = [];

function appendFile(name, file) {
    console.log(`append file : ${file}`);
    let content = fs.readFileSync(file);
    fs.appendFileSync(name, content);
}

function makeNames(dir, name) {
    return {
        prod: `${dir}/${name}.min.js`,
        dev: `${dir}/${name}.js`
    }
}

function minify(destDir, bundleName, files) {
    const {prod: prodName, dev: devName} = makeNames(destDir, bundleName);
    let bundle = fs.openSync(devName, 'w');

    files.forEach(file => {
        appendFile(devName, file);
    });
    console.log(`Cache size is ${files.length} file(s)`);
    fs.closeSync(bundle);

    const code = fs.readFileSync(devName, "utf8");
    bundle = fs.openSync(prodName, 'w');
    fs.appendFileSync(prodName, UglifyJS.minify(code).code);
    fs.closeSync(bundle);
}

const application = function(bundleName, destDir, theme) {
    apps.forEach(filename => {
        let requires = loader(filename);
        requires.order.forEach(file => {
            if(!cache.includes(file)) {
                cache.push(file);
            }
        });
    });

    minify(destDir, bundleName, cache);
};

const vendor = function(bundleName, destDir, themes) {
    themes.forEach(theme => minify(destDir, `${bundleName}_${theme}`, vendors(theme)));
};

const boot = function(bundleName, destDir, theme) {
    minify(destDir, bundleName, boots)
};

module.exports = {application, vendor, boot};
