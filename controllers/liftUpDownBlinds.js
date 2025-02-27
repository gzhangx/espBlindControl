const i2c = require('i2c-bus');
//i2cset -y 1 0x08 0x43 0 1 255 i


export async function sendLiftUpDownCommand(req, res) {
    console.log('Got request sendLiftUpDownCommand ', req.body);
    const body = req.body;
    if (!body) {
        console.log('sendLiftUpDownCommand: No body');
        return res.json({ msg: 'No body' });
    }

    const { dir, timeStr, deviceStr } = body;
    const time = parseInt(timeStr);
    let device = 0;
    if (deviceStr) {
        device = parseint(deviceStr);
        if (isNaN(device)) {
            return res.json({
                msg: 'Bad Device ' + deviceStr
            })    
        }
        if (device < 0 || device > 0x7f) {
            return res.json({
                msg: 'Bad Device ' + deviceStr
            })    
        }
    }
    console.log(`sendLiftUpDownCommand dir=${dir} time=${time}`);
    if (isNaN(time)) {
        return res.json({
            msg:'Bad time ' + timeStr
        })
    }
    await sendCommand(dir, time, device);
    return res.json({
        msg: 'done',
        dir,
        time,
    })
}

const DEVICE_ADDR = 0x08;

function getDirection(dir) {
    if (dir === 'C') return 0x43; 'c'
    if (dir === 'c') return 0x63; 'C'
    return 0x73; //s
}


async function sendCommand(dir, time, device = 0) {
    return await i2c.openPromisified(1).then(async dev => {
        const rbuf = Buffer.alloc(3);
        //dev.i2cRead(DEVICE_ADDR, 3, rbuf).then(() => {
        //    console.log('read dne', rbuf);
        //});
        const buf = createI2cBuffer(getDirection(dir), time, device)
        await dev.i2cWrite(DEVICE_ADDR, buf.length, buf);
        dev.close();
    });
}


function createI2cBuffer(cmd, time, device = 0) {

    const pre = Buffer.from([cmd, device]);
    const timeBuf = Buffer.alloc(4);
    timeBuf.writeUInt32BE(time);
    let start = 0;
    while (start < timeBuf.length && timeBuf[start] === 0) {
        start++;
    }

    // If all bytes are zero, return a single zero byte
    if (start === timeBuf.length) {
        start = timeBuf.length - 1;
    }

    // Slice the Buffer from the first non-zero byte
    const result = timeBuf.subarray(start);
    return Buffer.concat([pre, result]);
}