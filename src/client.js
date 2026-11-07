import 'react-native-url-polyfill/auto';
import {Platform} from 'react-native';
import * as SecureStore from 'expo-secure-store';
import {createClient,processLock} from '@supabase/supabase-js';
import {safeConfig} from './domain.js';
export const PUBLIC_URL=process.env.EXPO_PUBLIC_SUPABASE_URL||'';
export const PUBLIC_KEY=process.env.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY||'';
export const configured=safeConfig(PUBLIC_URL,PUBLIC_KEY);
let pending=Promise.resolve();
const CHUNK=1800;
async function nativeRead(key){const count=Number(await SecureStore.getItemAsync(`${key}.count`));if(!Number.isInteger(count)||count<1||count>30)return null;const chunks=await Promise.all(Array.from({length:count},(_,i)=>SecureStore.getItemAsync(`${key}.${i}`)));return chunks.some(x=>x===null)?null:chunks.join('');}
const storage={
 async getItem(key){await pending.catch(()=>{});return Platform.OS==='web'?globalThis.sessionStorage?.getItem(key)||null:nativeRead(key);},
 setItem(key,value){pending=pending.catch(()=>{}).then(async()=>{if(Platform.OS==='web'){globalThis.sessionStorage?.setItem(key,value);return;}const previous=Number(await SecureStore.getItemAsync(`${key}.count`))||0;const count=Math.ceil(value.length/CHUNK);if(count>30)throw Error('La sesión es demasiado grande para el almacén seguro.');for(let i=0;i<count;i++)await SecureStore.setItemAsync(`${key}.${i}`,value.slice(i*CHUNK,(i+1)*CHUNK));await SecureStore.setItemAsync(`${key}.count`,String(count));for(let i=count;i<previous;i++)await SecureStore.deleteItemAsync(`${key}.${i}`);});return pending;},
 removeItem(key){pending=pending.catch(()=>{}).then(async()=>{if(Platform.OS==='web'){globalThis.sessionStorage?.removeItem(key);return;}const count=Number(await SecureStore.getItemAsync(`${key}.count`))||0;await SecureStore.deleteItemAsync(`${key}.count`);for(let i=0;i<Math.min(count,30);i++)await SecureStore.deleteItemAsync(`${key}.${i}`);});return pending;}
};
async function timedFetch(url,options={}){const controller=new AbortController();const abort=()=>controller.abort();options.signal?.addEventListener('abort',abort,{once:true});if(options.signal?.aborted)controller.abort();const timer=setTimeout(abort,20000);try{return await fetch(url,{...options,signal:controller.signal});}catch(error){if(error.name==='AbortError')throw new Error('Request timed out');throw error;}finally{clearTimeout(timer);options.signal?.removeEventListener('abort',abort);}}
export const supabase=configured?createClient(PUBLIC_URL,PUBLIC_KEY,{global:{fetch:timedFetch},auth:{storage,persistSession:true,autoRefreshToken:true,detectSessionInUrl:false,lock:processLock}}):null;

