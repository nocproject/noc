const fs = require('fs');
const url = require('url');
const tar = require('tar-fs');
const bz2 = require('unbzip2-stream');

function load(filename) {
    const content = fs.readFileSync(filename);
    const requirements = JSON.parse(content.toString());
    const reqUrl = url.parse(requirements.url);
    const protocol = reqUrl.protocol.replace(':', '');
    let client, queue = [];

    function makeGet(url, resolve, reject) {
        client.get(url, (response) => {
            if(response.statusCode === 200) {
                response.pipe(bz2()).pipe(tar.extract('.pkg_cache', {
                        finish: () => resolve(`${url} status : ${response.statusCode}`)
                    })
                );
            } else {
                reject(`${url} status : ${response.statusCode}`);
            }
            response.on('error', (error) => {
                reject(`${url} status : ${error}`);
            });
        });
    }

    function loadPackage(pkg) {
        return new Promise((resolve, reject) => {
            let url = `${requirements.url}${pkg.name}`;
            if(pkg.version === 'latest') {
                new Promise((resolve, reject) => {
                    client.get(`${url}.latest`, (response) => {
                        let data = '';
                        response.on('data', (chunk) => {
                            data += chunk;
                        });
                        response.on('end', () => {
                            resolve(data.replace(/[^\x20-\x7E]+/g, ""));
                        });
                    }).on("error", (err) => {
                        reject("Error: " + err.message);
                    });
                })
                .then((version) => {
                    makeGet(`${url}@${version}.tar.bz2`, resolve, reject);
                })
                .catch((error) => reject(error));
            } else {
                makeGet(`${url}@${pkg.version}.tar.bz2`, resolve, reject);
            }
        });
    }

    if(['http', 'https'].includes(protocol)) {
        client = require(protocol);
    } else {
        console.error(`Unknowns protocol: ${protocol}`);
    }

    requirements.packages.forEach(pkg => {
        queue.push(loadPackage(pkg));
    });
    return queue;
}

module.exports = load;
