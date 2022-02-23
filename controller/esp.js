const fs = require('fs');
const store = {
    iots: {},
    hasStore: false,
};

const STORE_NAME = 'store.json';

function saveStore() {
    fs.writeFileSync(STORE_NAME, JSON.stringify(store.iots));
}

function loadStore() {
    if (!store.hasStore) {
        try {
            store.iots = JSON.parse(fs.readFileSync(STORE_NAME));
        } catch (err) {
            console.log(err);
        }
    }
    store.hasStore = true;
}

function register(req, res) {
    loadStore();    
    const query = req.query;
    console.log(query);
    function logRsp(msg) {
        res.send(msg);
        console.log(msg);
    }
    if (!query) return logRsp('err no query');
    const { mac, ip, action } = query;
    if (action === 'get') {
        return res.send((store.iots));
    }
    if (!mac) return logRsp('err no mac');
    if (!ip) return logRsp('err no ip');
    const me = store.iots[mac];
    if (!me) {
        store.iots[mac] = query;
    } else {
        me.ip = ip;
    }
    saveStore();
    res.send('OK');
}


function getActionByMac(req, res) {
    loadStore();
    const query = req.query;
    console.log(query);
    function logRsp(msg) {
        res.send(msg);
        console.log(msg);
    }
    if (!query) return logRsp('err no query');
    const { mac, } = query;    
    if (!mac) return logRsp('err no mac');    
    const me = store.iots[mac];
    if (!me) {
        return logRsp('err not found');    
    }    
    res.send(`OK=1&${me.actions}`);
}

function putActionByMac(req, res) {
    loadStore();
    const query = req.query;
    console.log(query);
    function logRsp(msg) {
        res.send(msg);
        console.log(msg);
    }
    if (!query) return logRsp('err no query');
    const { mac, action} = query;
    if (!mac) return logRsp('err no mac');
    if (!action) return logRsp('err no action');
    const me = store.iots[mac];
    if (!me) {
        return logRsp('err not found');
    }
    me.action = action;
    res.send(`OK`);
}

module.exports = {
    register,
    getActionByMac,
    putActionByMac,
}