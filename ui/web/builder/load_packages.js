const fs = require('fs');
const url = require('url');
const request = require('sync-request');
const tar = require('tar-fs');
const bz2 = require('unbzip2-stream');
const zlib = require("zlib");
const content = fs.readFileSync('../../../requirements/web.json');
const requirements = JSON.parse(content.toString());
const reqUrl = url.parse(requirements.url);
const protocol = reqUrl.protocol.replace(':', '');

let client;

if(['http', 'https'].includes(protocol)) {
    client = require(protocol);
} else {
    console.error(`Unknowns protocol: ${protocol}`);
}

function getPackage(pkg) {
    return new Promise((resolve, reject) => {
        const filename = `${pkg.name}@${pkg.version}.tar.bz2`;
        const url = `${requirements.url}/${filename}`;
        client.get(url, (response) => {
            let chunks_of_data = [];
            const output = fs.createWriteStream('xxx.tar.bz2');
            // response.pipe(bz2()).write(output);
            // response.on('data', (fragments) => {
            //     chunks_of_data.push(fragments);
            // });
            //
            // response.on('end', () => {
            //     let response_body = Buffer.concat(chunks_of_data);
            //     resolve(response_body.toString());
            // });
            //
            console.log('get done!');
            resolve(response.statusCode);
            response.on('error', (error) => {
                reject(error);
            });
        });
    });
}

// async function download() {
//     try {
//         let http_promise = getPackage();
//         let response_body = await http_promise;
//
//         console.log(response_body);
//     } catch(error) {
//
//         console.log(error);
//     }
// }

function load() {
    function loadPackage(pkg) {
        {
            const filename = `${pkg.name}@${pkg.version}.tar.bz2`;
            const url = `${requirements.url}/${filename}`;
            let res = request('GET', url);
            console.log(url);

            try {
                // const input = fs.createReadStream(res.getBody());
                const output = fs.createWriteStream(filename.replace('.bz2', ''), {flags: 'a'});
                // input.pipe(bz2()).write(output);
                res.getBody().write(output);
            } catch(error) {
                console.log(error);
            }
            // output.write(res.getBody(), function() {
            //     // Now the data has been written.
            //     console.log('file closed');
            // }).pipe(bz2);
            console.log('xxx');
//     let code = download(url);
//     console.log(`${url} : ${code}`);
//             getPackage(url).then((response) => {
//                 console.log(response);
//             }).catch((error) => {
//                 console.log(error);
//             });
            // client.get(url, (res) => {
            //     console.log('statusCode:', res.statusCode);
            //     console.log('headers:', res.headers);
            //     //
            //     //     // res.on('data', (d) => {
            //     //     //     process.stdout.write(d);
            //     //     // });
            //     //
            // }).on('error', (e) => {
            //     console.error(e);
            // });
        }
    }

    // requirements.packages.forEach(pkg => loadPackage(pkg));
    // loadPackage(requirements.packages[0]);
    getPackage(requirements.packages[0]).then(response => {
        console.log(response);
    });
    console.log('Done');
}

module.exports = load;
