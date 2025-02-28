"use client";
import Image from "next/image";

import { useEffect, useState , Fragment} from 'react'

import { ShutterObj, getBlinds, updateBlind, sendliftUpDownCommands } from '../components/api';
export default function Home() {

  const [controls, setControls] = useState<ShutterObj[]>([]);
  const [curText, setCurText] = useState('');

  const [curLiftDir, setCurLiftDir] = useState<'c' | 'C' | 's'>('s');
  const [curLiftTime, setCurLiftTime] = useState(30000);
  const [errorStr, setErrorStr] = useState('');
  useEffect(() => {
    getBlinds().then(b => {
      console.log(b.data);
      setControls(Object.values(b.data));
    }).catch((err:any) => {
      console.log('get blind error', err);
    })
  }, []);

  async function sendCommand(dir: 'c' | 'C' | 's') {
    setErrorStr('');
    sendliftUpDownCommands({
      dir,
      time: curLiftTime,
      device: 0,
    }).then(res => {
      if (res.data.message) {
        setErrorStr(new Date().toISOString() + ' ' + res.data.message);
      }
    })
  }
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div>
        <table>
          <tr>
            <td><button className="btn btn-primary" onClick={() => {
              if (curLiftTime > 0) {
                sendCommand('c');
              } else {
                setErrorStr('time must > 0')
              }
            }}>{'<='}</button></td>
            <td><button className="btn btn-primary" onClick={() => {
              if (curLiftTime > 0) {                
                sendCommand('C');
              } else {
                setErrorStr('time must > 0')
              }
            }}>{ '=>'}</button></td>
            <td><button className="btn btn-primary" onClick={() => {              
              sendCommand('s');
            }}>Stop</button></td>
            <td><input className="form-control" value={curLiftTime.toString()} onChange={e => {
              if (!e) {
                setCurLiftTime(0);
              }
              const v = parseInt(e.target.value);
              if (isNaN(v) || v < 0) {
                setErrorStr('bad int '+ e.target.value);
                return;
              }
              setCurLiftTime(v);
            }} ></input></td>
          </tr>
          <tr><td colSpan={3}>{ errorStr}</td></tr>
        </table>
      </div>
      <div className="">
        <div className="grid grid-cols-1 gap-x-8 gap-y-6 sm:grid-cols-2">
      {
            controls.map((c, keyc) => {
              return <Fragment key={'RootFram_'+keyc}><div key={'shutter_' + keyc} className="rounded-lg border-2 border-black">
                <label htmlFor="first-name" className="block text-sm font-semibold leading-6 text-gray-900" key='kk111lbl'>
                  {c.name}
                </label>
                <div className="mt-2.5" key='kk111'>
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
                        const value = cc.value || '';
                        return <Fragment key={`shutter_cctl_r${keyc}_ctl_${ctli}`} ><div key={`shutter_cctl_${keyc}_ctl_${ctli}`}>
                          Ctrl:{cc.name} <input type="text" value={value} onChange={e => {                            
                            cc.value = e.target.value;
                            updateBlind({
                              ip: c.ip,
                              id: cc.name,
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
                        </Fragment>
                      })}
                    </div>
                  </div>
                </div>
              </Fragment>
            })
          }
        </div>

        <div key='InfoText' className="grid grid-cols-1 gap-x-8 gap-y-6 sm:grid-cols-2">
          {curText}
        </div>
      </div>


      
    </main>
  );
}
