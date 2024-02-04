const fs = require('fs');
const blindsInfoJson = 'blindsInfo.json';
function registerBlinds(req, res) {
    console.log(`Got request id=${req.query.id}`, 'query', req.query, 'prms', req.params, 'body', req.body);
    const body = req.body;
    if (!body) {
        console.log('registerBlinds: No body');
        return res.json({ msg: 'No body' });    
    }
    const name = body.name?.trim();
    if (!name) {
        const msg = 'registerBlinds: No name';
        console.log(msg);
        return res.json({ msg});    
    }
    const controls = body.controls;
    if (!controls || !controls.length) {
        const msg = 'registerBlinds: No controls';
        console.log(msg);
        return res.json({ msg });
    }

    const ip = body.ip;
    if (!ip) {
        const msg = 'registerBlinds: No ip';
        console.log(msg);
        return res.json({ msg });
    }
    
    console.log('server post data', body);

    const allData = loadData();
    const thisControl = allData[name] || {};
    thisControl.name = name;
    thisControl.ip = ip;
    thisControl.controls = controls;
    thisControl.updateTime = new Date().toISOString();
    allData[name] = thisControl;
    fs.writeFileSync(blindsInfoJson, JSON.stringify(allData));
    res.json({ msg: 'Hello from blind!' });
}

function loadData() {
    try {
        return JSON.parse(fs.readFileSync(blindsInfoJson))
    } catch (exc) {
        console.log(exc, 'failed to load '+blindsInfoJson);
    }
    return {};
}

function getBlinds(req, res) {
    console.log('somone is calling ' + Date.now()+" " + req.query.ip+" id="+req.query.id)
    res.json(loadData());
}

module.exports = {
    registerBlinds,
    getBlinds,
}