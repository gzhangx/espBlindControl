"use client";
import Image from "next/image";

import { useEffect, useState } from 'react'

import { ShutterObj, getBlinds, updateBlind } from '../components/api';
export default function Home() {

  const [controls, setControls] = useState<ShutterObj[]>([]);
  const [curText, setCurText] = useState('');
  useEffect(() => {
    getBlinds().then(b => {
      console.log(b.data);
      setControls(Object.values(b.data));
    }).catch((err:any) => {
      console.log('get blind error', err);
    })
  }, []);
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      
      <div className="">
        <div className="grid grid-cols-1 gap-x-8 gap-y-6 sm:grid-cols-2">
      {
            controls.map((c, keyc) => {
              return <><div key={'shutter_' + keyc} className="rounded-lg border-2 border-black">
                <label htmlFor="first-name" className="block text-sm font-semibold leading-6 text-gray-900">
                  {c.name}
                </label>
                <div className="mt-2.5">
                  {c.ip}
                </div>
              </div>
                <div key={'shutter_ctls_' + keyc} className="rounded-lg border-2 border-black">
                  <label htmlFor="first-name" className="block text-sm font-semibold leading-6 text-gray-900">
                    {c.updateTime}
                  </label>
                  <div className="mt-2.5 rounded-lg border-2 border-black" >
                    {c.controls.map(cc => cc.name).join(',')}
                    <div className="grid grid-cols-1 gap-x-8 gap-y-6 sm:grid-cols-2">
                      {c.controls.map((cc, ctli) => {
                        const value = cc.value || '-1';
                        return <><div key={`shutter_cctl_ctl_${ctli}`}>
                          Ctrl:{cc.name} <input type="text" value={value} onChange={e => {                            
                            cc.value = e.target.value;
                            updateBlind({
                              ip: c.ip,
                              deg: cc.value,
                              type: cc.ctlType,
                            }).then(res => {
                              setCurText('Updated done ' + new Date().toISOString()+" "  + res.data.toString());
                            }).catch(err => {
                              console.log('Error happened ', err);
                              setCurText('Updated Error ' + new Date().toISOString() + " " + err.message);
                            })
                            setControls([...controls]);
                          }}></input>
                        </div><div></div>
                        </>
                      })}
                    </div>
                  </div>
                </div>
              </>
            })
          }
        </div>

        <div className="grid grid-cols-1 gap-x-8 gap-y-6 sm:grid-cols-2">
          {curText}
        </div>
      </div>


      
    </main>
  );
}
