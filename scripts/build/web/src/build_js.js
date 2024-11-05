const loaderJS = require('./loader');
const UglifyJS = require("uglify-js");
const fs = require('fs');
const apps = require('./applications');
const vendors = require('./vendors');
const boots = require('./boots');

const loader = loaderJS.parse;
const sha1 = loaderJS.sha1;
const cache = [];

function appendFile(name, file){
  let content = fs.readFileSync(file);
  try{
    UglifyJS.parse(content.toString());
    fs.appendFileSync(name, content);
  }
  catch(error){
    console.error(`Error parsing file ${file}: ${error.message}`);
    if(error.line !== undefined && error.col !== undefined){
      console.error(`Error at line ${error.line}, column ${error.col}`);
    }
    console.error(error.stack);
  }
}

function makeNames(dir, name, theme){
  return {
    prod: `${dir}/${name}.{hash}${theme}.js`,
    dev: `${dir}.debug/${name}.js`,
  }
}

function minify(destDir, bundleName, files, theme){
  const{prod: prodName, dev: devName} = makeNames(destDir, bundleName, theme);
  let bundle = fs.openSync(devName, 'w');

  files.forEach(file => {
    appendFile(devName, file);
  });
  // console.log(`Cache size is ${files.length} file(s)`);
  fs.closeSync(bundle);

  const code = fs.readFileSync(devName, "utf8");
  const minified = UglifyJS.minify(code).code;
  const hash = sha1(minified);
  bundle = fs.openSync(prodName.replace(/{hash}/, hash), 'w');
  fs.appendFileSync(prodName.replace(/{hash}/, hash), minified);
  fs.closeSync(bundle);
  return new Promise((resolve, reject) => resolve({name: `${bundleName}.{hash}`, theme: `${theme.replace(/\./, '')}`, hash: hash}));
}

const application = function(bundleName, destDir, theme){
  apps.forEach(filename => {
    let requires = loader(filename);
    requires.order.forEach(file => {
      if(!cache.includes(file)){
        cache.push(file);
      }
    });
  });

  return [minify(destDir, bundleName, cache, '')];
};

const vendor = function(bundleName, destDir, themes){
  return themes.map(theme => minify(destDir, bundleName, vendors(theme), `.${theme}`));
};

const boot = function(bundleName, destDir, theme){
  return [minify(destDir, bundleName, boots, '')];
};

module.exports = {application, vendor, boot};
