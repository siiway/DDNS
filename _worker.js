/*
https://github.com/siiway/DDNS/blob/master/_worker.js
出处 / From: https://opswill.com/articles/cloudflare-worker-ip-info-api.html
并作出了一点点修改
---
- /ip: 返回纯 ip
- /json: 返回 json 数据 (大量信息警告)
- /: 跳转 github 文件处
*/

export default {
    async fetch(request) {
        if (request.url.pathname === '/ip') {
            return await handleIPRequest(request);
        } else if (request.url.pathname === '/json') {
            return await handleJSONRequest(request);
        } else if (request.url.pathname === '/') {
            return redirect('https://github.com/siiway/DDNS/blob/master/_worker.js', 301);
        } else {
            return await notFound(request);
        }
    },

    async handleIPRequest(request) {
        return new Response(request.headers.get('CF-Connecting-IP'), {
            headers: {
                "Content-Type": "text/plain;charset=UTF-8"
            }
        });
    },

    async handleJSONRequest(request) {
        const data = {
            Method: request.method,
            Url: request.url,
            IP: {
                IP: request.headers.get('CF-Connecting-IP'),
                Continent: request.cf.continent,
                Country: request.cf.country,
                IsEU: request.cf.isEUCountry,
                Region: request.cf.region,
                RegionCode: request.cf.regionCode,
                City: request.cf.city,
                Latitude: request.cf.latitude,
                Longitude: request.cf.longitude,
                PostalCode: request.cf.postalCode,
                MetroCode: request.cf.metroCode,
                Colo: request.cf.colo,
                ASN: request.cf.asn,
                ASOrganization: request.cf.asOrganization,
                Timezone: request.cf.timezone
            },
            Headers: {},
            Security: {}
        };

        // 遍历并存储每个 HTTP 头，~~排除以 cf- 开头的 HTTP 头~~
        request.headers.forEach((value, name) => {
            // if (!name.toLowerCase().startsWith('cf-')) {
            data.Headers[name] = value;
            // }
        });

        // 遍历 request.cf 并存储所需对象的属性到 Security 中
        for (const key in request.cf) {
            if (
                key == 'clientTcpRtt'
                || key == 'tlsCipher'
                || key == 'tlsVersion'
                || key == 'httpProtocol'
                || key == 'clientHandshake'
                || key == 'clientFinished'
                || key == 'serverHandshake'
                || key == 'serverFinished'
                || key == 'corporateProxy'
                || key == 'verifiedBot'
                || key == 'score'

            ) {
                if (typeof request.cf[key] === 'object') {
                    for (const innerKey in request.cf[key]) {
                        data.Security[innerKey] = request.cf[key][innerKey];
                    }
                } else {
                    data.Security[key] = request.cf[key];
                }
            }
        }

        var dataJson = JSON.stringify(data, null, 4);
        console.log(dataJson);

        return new Response(dataJson, {
            headers: {
                "Content-Type": "application/json;charset=UTF-8"
            }
        })
    },

    async notFound(request) {
        return new Response("404 Not Found", {
            status: 404,
            headers: {
                "Content-Type": "text/plain;charset=UTF-8"
            }
        });
    }
};
