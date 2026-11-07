import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
const root=path.resolve(import.meta.dirname,'..');
const url='https://kizwbajlravjjhnbpkhm.supabase.co';
const keys=JSON.parse(await fs.readFile(path.join(root,'.auth/keys.json'),'utf8'));
const pub=keys.keys.find(k=>k.type==='publishable').api_key;
const admin=keys.keys.find(k=>k.name==='service_role').api_key;
const report={executedAt:new Date().toISOString(),projectRef:'kizwbajlravjjhnbpkhm',checks:[]};
async function request(route,{key=pub,token,method='GET',body,type='application/json'}={}){const r=await fetch(url+route,{method,headers:{apikey:key,Authorization:`Bearer ${token||key}`,'Content-Type':type},body:body===undefined?undefined:type==='application/json'?JSON.stringify(body):body});const text=await r.text();let data;try{data=JSON.parse(text)}catch{data=text}return {status:r.status,data};}
async function check(name,fn){await fn();report.checks.push({name,status:'PASS'});console.log('PASS',name);}
let accounts;
try{accounts=JSON.parse(await fs.readFile(path.join(root,'.auth/test-users.json'),'utf8'));}catch{
 accounts=[];for(let i=0;i<2;i++){const email=`nexo.qa.${crypto.randomUUID()}@example.com`,password=crypto.randomBytes(24).toString('base64url')+'Aa1!';const r=await request('/auth/v1/admin/users',{key:admin,method:'POST',body:{email,password,email_confirm:true}});assert.equal(r.status,200,JSON.stringify(r.data));accounts.push({id:r.data.id,email,password});}
 await fs.writeFile(path.join(root,'.auth/test-users.json'),JSON.stringify(accounts,null,2));
}
const tokens=[];for(const account of accounts){const r=await request('/auth/v1/token?grant_type=password',{method:'POST',body:{email:account.email,password:account.password}});assert.equal(r.status,200);tokens.push(r.data.access_token);}
const owner=accounts[0].id,id=crypto.randomUUID(),bytes=await fs.readFile(path.join(root,'evidencias/fotografia-prueba.png'));
const hash=crypto.createHash('sha256').update(bytes).digest('hex'),object=`${owner}/${id}/${hash.slice(0,24)}.png`;
const row={id,owner_id:owner,title:'Luminaria dañada en el pasillo',description:'Fotografía sintética de prueba para verificar el registro y recuperación de evidencias.',location:'Edificio A · Pasillo principal',category:'Electricidad',priority:'high',photo_path:object,photo_mime:'image/png',photo_bytes:bytes.length,photo_sha256:hash,photo_state:'pending'};
try{
 await check('Registrar metadatos sin guardar bytes de imagen en PostgreSQL',async()=>{const r=await request('/rest/v1/incidents',{token:tokens[0],method:'POST',body:row});assert.equal(r.status,201,JSON.stringify(r.data));});
 await check('Cargar PNG real en contenedor privado',async()=>{const r=await request('/storage/v1/object/incidence-photos/'+object,{token:tokens[0],method:'POST',body:bytes,type:'image/png'});assert.equal(r.status,200,JSON.stringify(r.data));const u=await request('/rest/v1/incidents?id=eq.'+id,{token:tokens[0],method:'PATCH',body:{photo_state:'ready'}});assert.equal(u.status,204);});
 await check('Recuperar URL firmada y comprobar integridad SHA256',async()=>{const s=await request('/storage/v1/object/sign/incidence-photos/'+object,{token:tokens[0],method:'POST',body:{expiresIn:120}});assert.equal(s.status,200);const r=await fetch(url+'/storage/v1'+s.data.signedURL);assert.equal(r.status,200);assert.equal(crypto.createHash('sha256').update(Buffer.from(await r.arrayBuffer())).digest('hex'),hash);});
 await check('Acceso anónimo y URL pública rechazados',async()=>{for(const route of ['/storage/v1/object/authenticated/incidence-photos/'+object,'/storage/v1/object/public/incidence-photos/'+object]){const r=await request(route);assert.ok(r.status>=400);}const r=await request('/rest/v1/incidents?select=id');assert.ok(r.status>=400);});
 await check('Otro usuario no puede consultar ni firmar la fotografía',async()=>{const r=await request('/rest/v1/incidents?id=eq.'+id,{token:tokens[1]});assert.deepEqual(r.data,[]);const s=await request('/storage/v1/object/sign/incidence-photos/'+object,{token:tokens[1],method:'POST',body:{expiresIn:120}});assert.ok(s.status>=400);});
 await check('Servidor rechaza PDF por tipo MIME no permitido',async()=>{const r=await request('/storage/v1/object/incidence-photos/'+owner+'/'+crypto.randomUUID()+'/no-permitido.pdf',{token:tokens[0],method:'POST',body:Buffer.from('%PDF-1.4 prueba'),type:'application/pdf'});assert.ok(r.status>=400,JSON.stringify(r));});
 await check('Nuevo inicio de sesión recupera referencia persistida',async()=>{const login=await request('/auth/v1/token?grant_type=password',{method:'POST',body:{email:accounts[0].email,password:accounts[0].password}});const r=await request('/rest/v1/incidents?id=eq.'+id,{token:login.data.access_token});assert.equal(r.data[0].photo_path,object);assert.equal(r.data[0].photo_state,'ready');});
 const bucket=await request('/storage/v1/bucket/incidence-photos',{key:admin});assert.equal(bucket.status,200);
 report.bucket={id:bucket.data.id,public:bucket.data.public,file_size_limit:bucket.data.file_size_limit,allowed_mime_types:bucket.data.allowed_mime_types};
 report.object={id,path:object,bytes:bytes.length,sha256:hash,mime:'image/png'};report.status='PASS';
}catch(e){report.status='FAIL';report.error=e.message;process.exitCode=1;}finally{await fs.writeFile(path.join(root,'evidencias/pruebas-cloud.json'),JSON.stringify(report,null,2));}
