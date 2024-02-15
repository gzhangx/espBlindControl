const url = "http://192.168.0.40:18082";

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