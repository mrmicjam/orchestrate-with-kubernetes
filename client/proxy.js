var http = require('http'),
    httpProxy = require('http-proxy');

proxy = httpProxy.createProxyServer();

proxy.on('proxyRes', function (proxyRes, req, res) {
    console.log('RAW Response from the target', JSON.stringify(proxyRes.headers, true, 2));
});

// Listen for the `error` event on `proxy`.
proxy.on('error', function (err, req, res) {
    res.writeHead(500, {
        'Content-Type': 'text/plain'
    });

    res.end('Something went wrong. And we are reporting a custom error message.');
});

http.createServer(function (req, res) {
        console.log('URL: ', req.url);
        if (req.url.match(/^\/api/i)) {
            // Route api requests to a different port
            proxy.web(req, res, {target: "http://localhost:8081"});
        } else {
            proxy.web(req, res, {target: "http://localhost:8082"});
        }
    }
).listen(8080);
