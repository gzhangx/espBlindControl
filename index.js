const restify = require('restify');

const esp = require('./controller/esp');

const PORT = 8101;
function makeRespond(func) {
    return async (req, res, next) => {
        try {
            await func(req, res);
            next();
        } catch (err) {
            console.log(err);
            res.send('ERR');
            next();
        }
    }
}

var server = restify.createServer();
server.use(restify.plugins.queryParser());

const maps = [
    ['/esp/register', esp.register],
    ['/esp/getAction', esp.getActionByMac],
    ['/esp/putAction', esp.putActionByMac],
]

maps.forEach(m => {
    server.get(m[0], makeRespond(m[1]));
})


server.listen(PORT, function () {
    console.log('%s listening at %s', server.name, server.url);
});