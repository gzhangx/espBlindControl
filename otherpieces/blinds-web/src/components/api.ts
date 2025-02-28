const url = "http://192.168.0.119:18082";

import { util } from '@gzhangx/googleapi'



export type ControlTypes = 'servo';
export interface ControlSwitch {
    name: string;
    ctlType: ControlTypes;
    value: string;
}
export interface ShutterObj {
    name: string;
    ip: string;
    updateTime: string;
    controls: ControlSwitch[];
}
export async function getBlinds() {
    const res = await util.doHttpRequest({
        method: 'GET',
        url: `${url}/getBlinds`,
    });
    console.log(res);
    return res as any as { data: ShutterObj };
}


interface ControlUpdatePrms {
    ip: string;
    id: string;
    type: ControlTypes;
    deg: string;
}
export async function updateBlind(prm: ControlUpdatePrms) {
    const res = await util.doHttpRequest({
        method: 'POST',
        url: `http://${prm.ip}/update`,
        data: prm,
    });
    console.log(res);
    return res as any as { data: ShutterObj };
}


interface LiftUpDownParams {
    device: 0;
    dir: 'c' | 'C' | 's';
    time: number;
}
export async function sendliftUpDownCommands(cmd: LiftUpDownParams) {
    const res = await util.doHttpRequest({
        method: 'POST',
        url: `${url}/liftUpDownBlinds`,
        data: cmd,
    });
    console.log(res);
    return res as any as { data: { message: string } };
}