export const BUCKET='incidence-photos';
export const MAX_BYTES=5*1024*1024;
export const ALLOWED_MIME=['image/jpeg','image/png','image/webp'];
export const CATEGORIES=['Electricidad','Agua y sanitarios','Infraestructura','Limpieza','Seguridad','Otro'];
export const PRIORITIES={low:{label:'Baja',color:'#527C69'},medium:{label:'Media',color:'#A67D32'},high:{label:'Alta',color:'#B65B3C'},critical:{label:'Crítica',color:'#A33D4C'}};
export const STATUSES={open:{label:'Abierta',color:'#B2782E'},in_progress:{label:'En atención',color:'#416F91'},resolved:{label:'Resuelta',color:'#487F65'}};
export function validateIncident(input){
 const title=String(input.title||'').trim(),description=String(input.description||'').trim(),location=String(input.location||'').trim();
 if(title.length<5||title.length>100)throw new Error('El título debe tener de 5 a 100 caracteres.');
 if(description.length<10||description.length>1200)throw new Error('Describe el problema con al menos 10 y hasta 1200 caracteres.');
 if(location.length<2||location.length>120)throw new Error('Indica una ubicación de 2 a 120 caracteres.');
 if(!CATEGORIES.includes(input.category))throw new Error('Selecciona una categoría válida.');
 if(!Object.hasOwn(PRIORITIES,input.priority))throw new Error('Selecciona una prioridad válida.');
 return {title,description,location,category:input.category,priority:input.priority};
}
export function detectMime(bytes){
 const b=bytes instanceof Uint8Array?bytes:new Uint8Array(bytes);
 if(b.length>=12&&b[0]===255&&b[1]===216&&b[2]===255)return 'image/jpeg';
 if(b.length>=12&&[137,80,78,71,13,10,26,10].every((v,i)=>b[i]===v))return 'image/png';
 if(b.length>=12&&String.fromCharCode(...b.slice(0,4))==='RIFF'&&String.fromCharCode(...b.slice(8,12))==='WEBP')return 'image/webp';
 return null;
}
export function validatePhoto(bytes){
 const data=bytes instanceof Uint8Array?bytes:new Uint8Array(bytes);
 if(!data.byteLength)throw new Error('La imagen está vacía. Selecciona otra fotografía.');
 if(data.byteLength>MAX_BYTES)throw new Error('La fotografía supera 5 MB. Elige una imagen más pequeña.');
 const mime=detectMime(data);if(!mime)throw new Error('Formato no permitido. Solo se aceptan fotografías JPEG, PNG o WebP.');
 return {mime,size:data.byteLength,extension:{'image/jpeg':'jpg','image/png':'png','image/webp':'webp'}[mime]};
}
export function photoPath(userId,incidentId,hash,extension){
 const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
 if(!uuid.test(userId)||!uuid.test(incidentId)||!/^[0-9a-f]{64}$/i.test(hash)||!['jpg','png','webp'].includes(extension))throw new Error('La referencia de la fotografía no es válida.');
 return `${userId}/${incidentId}/${hash.slice(0,24)}.${extension}`;
}
export const formatBytes=n=>n>=1024*1024?`${(n/(1024*1024)).toFixed(1)} MB`:`${Math.round(n/1024)} KB`;
export const dateTime=value=>new Date(value).toLocaleString('es-MX',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'});
export function safeConfig(url,key){
 try{const u=new URL(url);if(u.protocol!=='https:'||!u.hostname.endsWith('.supabase.co')||u.username||u.password||u.pathname!=='/')return false;
 if(key.startsWith('sb_secret_'))return false;if(key.startsWith('sb_publishable_')&&key.length>25)return true;
 const payload=JSON.parse(globalThis.atob(key.split('.')[1].replace(/-/g,'+').replace(/_/g,'/')));return payload.role==='anon';
 }catch{return false;}
}
export function friendlyError(error){
 const message=String(error?.message||error||'Error desconocido');
 if(/Invalid login credentials/i.test(message))return 'Correo o contraseña incorrectos.';
 if(/Email not confirmed/i.test(message))return 'Confirma tu correo antes de iniciar sesión.';
 if(/User already registered/i.test(message))return 'Este correo ya está registrado. Inicia sesión.';
 if(/row.level|row-level|violates.*policy|unauthorized|403|permission denied/i.test(message))return 'No tienes autorización para esta operación. Revisa la sesión y las reglas de acceso.';
 if(/bucket not found|does not exist|relation.*not/i.test(message))return 'Falta configurar la base de datos o el contenedor. Ejecuta la migración del proyecto.';
 if(/network|failed to fetch|fetch failed|timed?\s?out|connection/i.test(message))return 'Se perdió la conexión. Conservamos el formulario; revisa tu red y vuelve a intentar.';
 return message.slice(0,220);
}
