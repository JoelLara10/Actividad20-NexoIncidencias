import {Platform} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import {File} from 'expo-file-system';
import * as Crypto from 'expo-crypto';
import {supabase} from './client.js';
import {BUCKET,photoPath,validateIncident,validatePhoto,friendlyError} from './domain.js';
export const newId=()=>Crypto.randomUUID();
export async function pickPhoto(camera=false){
 if(camera){const permission=await ImagePicker.requestCameraPermissionsAsync();if(!permission.granted)throw Error('Permite el acceso a la cámara para tomar una foto, o usa la galería.');}
 else if(Platform.OS!=='web'){const permission=await ImagePicker.requestMediaLibraryPermissionsAsync();if(!permission.granted)throw Error('No se autorizó la galería. Puedes cambiar el permiso en los ajustes del dispositivo.');}
 const options={mediaTypes:['images'],allowsEditing:true,quality:.82,exif:false,base64:false};
 const result=camera?await ImagePicker.launchCameraAsync(options):await ImagePicker.launchImageLibraryAsync(options);
 return result.canceled?null:result.assets?.[0]||null;
}
export async function readPhoto(asset){
 if(Platform.OS==='web'){if(asset.file?.arrayBuffer)return asset.file.arrayBuffer();const response=await fetch(asset.uri);if(!response.ok)throw Error('No pudimos leer la imagen seleccionada.');return response.arrayBuffer();}
 return new File(asset.uri).arrayBuffer();
}
export async function inspectPhoto(asset){if((asset.fileSize||asset.file?.size||0)>5*1024*1024)throw Error('La fotografía supera 5 MB. Elige una imagen más pequeña.');const bytes=await readPhoto(asset);return {...validatePhoto(bytes),bytes};}
export async function publishIncident({id,userId,form,asset,onStage}){
 if(!supabase)throw Error('Configura la conexión a Supabase.');
 onStage('validating');const fields=validateIncident(form);const {bytes,mime,size,extension}=await inspectPhoto(asset);
 const hash=await Crypto.digest(Crypto.CryptoDigestAlgorithm.SHA256,bytes);const sha256=Array.from(new Uint8Array(hash),b=>b.toString(16).padStart(2,'0')).join('');
 const path=photoPath(userId,id,sha256,extension);
 onStage('metadata');
 // Reservar la referencia permite reintentar el mismo reporte sin duplicarlo.
 const {data:existing,error:checkError}=await supabase.from('incidents').select('id,status,photo_state').eq('id',id).maybeSingle();if(checkError)throw checkError;
 if(existing?.photo_state!=='ready'){
  const payload={id,owner_id:userId,...fields,photo_path:path,photo_state:'pending',photo_mime:mime,photo_bytes:size,photo_sha256:sha256};
  const {error}=await supabase.from('incidents').upsert(payload,{onConflict:'id'});if(error)throw error;
  onStage('uploading');
  const {error:uploadError}=await supabase.storage.from(BUCKET).upload(path,bytes,{contentType:mime,cacheControl:'0',upsert:true});
  if(uploadError){await supabase.from('incidents').update({photo_state:'failed'}).eq('id',id);throw uploadError;}
  onStage('confirming');const {error:readyError}=await supabase.from('incidents').update({photo_state:'ready'}).eq('id',id);if(readyError)throw readyError;
 }
 const {data,error}=await supabase.from('incidents').select('*').eq('id',id).single();if(error)throw error;onStage('done');return data;
}
export async function listIncidents(){const {data,error}=await supabase.from('incidents').select('*').order('created_at',{ascending:false}).limit(100);if(error)throw error;return data;}
export async function signedPhoto(path){const {data,error}=await supabase.storage.from(BUCKET).createSignedUrl(path,120);if(error)throw error;return data.signedUrl;}
export async function changeStatus(id,status){const {data,error}=await supabase.from('incidents').update({status}).eq('id',id).select().single();if(error)throw error;return data;}
export async function archiveIncident(id,archived){const {error}=await supabase.from('incidents').update({archived}).eq('id',id);if(error)throw error;}
export async function getEvents(id){const {data,error}=await supabase.from('incident_events').select('*').eq('incident_id',id).order('created_at',{ascending:false});if(error)throw error;return data;}
export {friendlyError};

