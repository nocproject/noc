const fs = require('fs');
const url = require('url');
const tar = require('tar-fs');
const bz2 = require('unbzip2-stream');
const content = fs.readFileSync('../../../requirements/web.json');
const requirements = JSON.parse(content.toString());
const reqUrl = url.parse(requirements.url);
const protocol = reqUrl.protocol.replace(':', '');

function load() {
    let client, queue = [];

    function loadPackage(pkg) {
        return new Promise((resolve, reject) => {
            const filename = `${pkg.name}@${pkg.version}.tar.bz2`;
            const url = `${requirements.url}/${filename}`;
            client.get(url, (response) => {
                if(response.statusCode === 200) {
                    response.pipe(bz2()).pipe(tar.extract('.pkg_cache', {
                            finish: () => resolve(`${filename} status : ${response.statusCode}`)
                        })
                    );
                } else {
                    reject(`${filename} status : ${response.statusCode}`);
                }
                response.on('error', (error) => {
                    reject(`${filename} status : ${error}`);
                });
            });
        });
    }

    if(['http', 'https'].includes(protocol)) {
        client = require(protocol);
    } else {
        console.error(`Unknowns protocol: ${protocol}`);
    }

    // loadPackage(requirements.packages[0]).then(response => {
    //     console.log(response);
    // });
    requirements.packages.forEach(pkg => {
        queue.push(loadPackage(pkg));
    });
    return queue;
}

module.exports = load;
