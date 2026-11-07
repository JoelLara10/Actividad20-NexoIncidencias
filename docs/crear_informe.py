from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile,ZIP_DEFLATED
import json
from copy import deepcopy
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.section import WD_SECTION_START
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parent.parent
REF=ROOT/'docs/portada-referencia.docx'
INVENTORY=json.loads((ROOT/'docs/inventario-portada.json').read_text())
assert sha256(REF.read_bytes()).hexdigest()==INVENTORY['sha256']
E=ROOT/'evidencias'
api=json.loads((E/'pruebas-cloud.json').read_text(encoding='utf-8-sig'))
ui=json.loads((E/'prueba-interfaz.json').read_text(encoding='utf-8-sig'))
assert api['status']=='PASS' and ui['status']=='PASS'
D=Document(REF)
def replace_slot(index,text):
 paragraph=D.paragraphs[index]
 if paragraph.runs:
  paragraph.runs[0].text=text
  for run in paragraph.runs[1:]:run.text=''
 else:paragraph.add_run(text)
replace_slot(10,'Actividad 20 Integración de almacenamiento en la nube para archivos multimedia')
replace_slot(12,'Nombre del estudiante:')
replace_slot(25,'7 de noviembre de 2026')
sec=D.add_section(WD_SECTION_START.NEW_PAGE)
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.left_margin=sec.right_margin=sec.top_margin=sec.bottom_margin=Inches(.75)
sec.header.is_linked_to_previous=False;sec.footer.is_linked_to_previous=False
sec.different_first_page_header_footer=False
for name,size in [('Body19',11),('Caption19',9),('Code19',9)]:
 style=D.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
 style.base_style=D.styles['Normal'];style.font.name='Consolas' if name=='Code19' else 'Calibri';style.font.size=Pt(size);style.font.color.rgb=RGBColor(0,0,0)
 style.paragraph_format.space_after=Pt(7);style.paragraph_format.line_spacing=1.08
for name,size in [('Title',23),('Heading 1',18),('Heading 2',13)]:
 style=D.styles[name];style.font.name='Calibri';style.font.size=Pt(size);style.font.color.rgb=RGBColor(0,0,0)
 style.paragraph_format.space_before=Pt(10);style.paragraph_format.space_after=Pt(8)
 for border in list(style.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
header=sec.header.paragraphs[0];header.text='DESARROLLO MÓVIL INTEGRAL   /   NEXO INCIDENCIAS';header.style=D.styles['Caption19']
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT;footer.style=D.styles['Caption19'];footer.add_run('Actividad 20  |  ')
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
def p(text,style='Body19'):return D.add_paragraph(text,style)
def h(text):return D.add_heading(text,1)
def sub(text):return D.add_heading(text,2)
def page(text):par=h(text);par.paragraph_format.page_break_before=True
bullet_count=0
def bullet(text):
 par=p('•  '+text);par.paragraph_format.left_indent=Inches(.12)
def code(text):return p(text,'Code19')
def table(headers,rows,widths):
 t=D.add_table(rows=1,cols=len(headers));t.autofit=False
 for col,width in zip(t.columns,widths):col.width=Inches(width)
 for cell,text in zip(t.rows[0].cells,headers):
  cell.text=text
  for run in cell.paragraphs[0].runs:run.bold=True
  shading=OxmlElement('w:shd');shading.set(qn('w:fill'),'E8ECE6');cell._tc.get_or_add_tcPr().append(shading)
 repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
 for row in rows:
  for cell,text in zip(t.add_row().cells,row):cell.text=str(text)
 for row in t.rows:
  row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
  for cell,width in zip(row.cells,widths):
   cell.width=Inches(width)
   for paragraph in cell.paragraphs:
    paragraph.style=D.styles['Body19'];paragraph.paragraph_format.space_after=Pt(5)
    for run in paragraph.runs:run.font.size=Pt(10)
 return t

def pair(left,right,width=2.85):
 t=D.add_table(rows=1,cols=2);t.autofit=False
 for cell,(title,file,caption) in zip(t.rows[0].cells,[left,right]):
  cell.width=Inches(3.5)
  cell.paragraphs[0].style=D.styles['Body19'];cell.paragraphs[0].add_run(title).bold=True
  image=cell.add_paragraph();image.paragraph_format.space_after=Pt(6)
  image.add_run().add_picture(str(E/file),width=Inches(width))
  cell.add_paragraph(caption,'Caption19')

p('Almacenamiento privado de fotografías de incidencias','Title')
p('Actividad 20  Nexo Incidencias')
p('Lara Rodriguez Joel Alejandro\nIDGS 101  |  10º cuatrimestre\nDesarrollo Móvil Integral\nDocente R. Vinicio Camacho\n7 de noviembre de 2026')
h('Propósito y resultado')
p('Desarrollé Nexo Incidencias para registrar problemas en instalaciones y adjuntar una fotografía que permita reconocerlos. La aplicación utiliza React Native y Expo SDK 58, con Supabase para autenticar al usuario, almacenar archivos privados y conservar los datos de cada reporte. La imagen permanece en Storage; la base de datos guarda su referencia y los metadatos que la relacionan con la incidencia.')
p('Se comprobó el flujo con el servicio real: seleccionar un PNG, visualizarlo, cargarlo, recuperar una URL temporal y mostrarlo nuevamente después de recargar la aplicación web. Las pruebas también verificaron el rechazo de accesos anónimos y de otro usuario. Las fotografías utilizadas son ejemplos sintéticos identificados en las capturas. La cámara y el cierre y reapertura en un teléfono físico quedan pendientes de comprobar.')
sub('Funciones adicionales')
for text in ['Registro e inicio de sesión, reportes separados por propietario y sesión móvil en SecureStore.','Ubicación escrita, seis categorías, cuatro prioridades, estados Abierta, En atención y Resuelta.','Panel de estadísticas, buscador, filtros, archivo y restauración de reportes.','Borrador de texto, caché de metadatos por usuario e historial de cambios en la nube.','Indicadores de carga por fase, reintento de la misma incidencia y visor de imagen completa.']:
 bullet(text)
sub('Entregables y ubicación')
p('Proyecto: C:\\10moCuatri\\Vini\\Actividad20-NexoIncidencias\nRepositorio: https://github.com/JoelLara10/Actividad20-NexoIncidencias\nEl código de selección y carga está en src/api.js; las pantallas están en src/IncidentForm.js y src/IncidentDetail.js. Las reglas se entregan en supabase/migrations. Los resultados y capturas están en evidencias.')

page('Preparación del servicio de almacenamiento')
p('Seleccioné Supabase Storage por su integración con autenticación y reglas RLS. Se creó una organización dedicada y un proyecto gratuito. El plan no garantiza disponibilidad permanente y puede aplicar pausas o cuotas; no se habilitaron recursos pagados.')
table(['Elemento','Configuración implementada'],[
('Servicio y proyecto','Supabase Storage · Nexo Incidencias · kizwbajlravjjhnbpkhm'),
('Espacio de almacenamiento','Bucket incidence-photos · privado · región us-east-1'),
('Formatos permitidos','JPEG, PNG y WebP; application/pdf y SVG no permitidos'),
('Tamaño máximo de la app y bucket','5 242 880 bytes por fotografía, equivalente a 5 MiB'),
('Mecanismo de carga','SDK JavaScript con ArrayBuffer, petición HTTPS autenticada mediante JWT'),
('Condiciones de acceso','Usuario autenticado y primera carpeta de ruta igual a auth.uid()'),
('Visualización','URL firmada de 120 segundos; se solicita nuevamente al abrir el reporte')],[1.85,5.15])
sub('Configuración realizada')
for text in ['Crear organización y proyecto mediante la sesión autorizada del propietario.','Aplicar la migración SQL: tablas incidents e incident_events, índices, triggers y políticas por propietario.','Crear el bucket privado con tipos MIME y tamaño restringidos en el servidor.','Configurar solo la URL y la clave pública en el archivo local .env, excluido de Git.','Comprobar carga real, integridad SHA256, acceso autorizado y rechazo de accesos externos.']:
 bullet(text)
sub('Recursos y condiciones de uso')
p('Las imágenes de prueba fueron generadas para esta actividad y no contienen fotografías personales. El uso del servicio está sujeto a las condiciones y cuotas de Supabase. La entrega identifica al proveedor y enlaza su documentación. No se incorporan claves administrativas al código móvil ni al repositorio.')

page('Implementación y procesamiento de respuestas')
sub('Flujo de la aplicación')
p('Iniciar sesión → escribir incidencia → seleccionar galería o cámara → validar formato y tamaño → mostrar vista previa → guardar metadatos pendientes → subir fotografía al bucket privado → confirmar estado listo → solicitar URL temporal → visualizar imagen remota.')
sub('Selección validación y transferencia')
code("const result = await ImagePicker.launchImageLibraryAsync({\n  mediaTypes: ['images'], allowsEditing: true, quality: .82, exif: false\n});\nconst { bytes, mime } = await inspectPhoto(result.assets[0]);\nconst { error } = await supabase.storage.from('incidence-photos')\n  .upload(path, bytes, { contentType: mime, upsert: true });")
p('La selección puede cancelarse sin borrar el formulario. La cámara solicita permiso al tocar el botón. La app lee la fotografía como ArrayBuffer y valida firmas de JPEG, PNG o WebP, además del tamaño. Calcula SHA256 para identificar los bytes. La ruta combina UUID del usuario, UUID de la incidencia y parte del hash. Se conserva el UUID para reintentar sin duplicar el reporte.')
sub('Interpretación de JSON')
p('El cliente Supabase convierte las respuestas JSON en objetos data y error. Las consultas de incidents entregan arreglos con título, ubicación, categoría, prioridad y estado. El inicio de sesión devuelve sesión y usuario. Storage devuelve la ruta del objeto; createSignedUrl devuelve data.signedUrl. Cada error se transforma en un mensaje visible. La fotografía se recibe como contenido binario; no forma parte del JSON de la incidencia.')
code("const { data, error } = await supabase.storage\n  .from('incidence-photos').createSignedUrl(photo_path, 120);\nif (error) throw error;\n// Image usa data.signedUrl como URI remota")
sub('Coordinación de archivo y reporte')
p('La fila se registra primero con photo_state pending. Tras cargar el objeto se actualiza a ready; un trigger verifica que exista en storage.objects. Ante un error se mantiene el formulario y la transferencia se puede retomar. No existe una transacción atómica entre Storage y PostgreSQL: un corte puede dejar una referencia pendiente o un archivo ya cargado. Reintentar con el mismo ID y ruta permite completar el flujo; no hay cola automática en segundo plano.')

page('Endpoints y datos que conserva la base de datos')
p('Todas las peticiones remotas utilizan la base HTTPS https://kizwbajlravjjhnbpkhm.supabase.co y una clave pública de proyecto. Las operaciones privadas incorporan el JWT del usuario autenticado.')
table(['Método y ruta','Finalidad y datos'],[
('POST /auth/v1/signup','Correo y contraseña para registrar una cuenta; confirmación del correo.'),
('POST /auth/v1/token?grant_type=password','Iniciar sesión y obtener JWT de usuario.'),
('GET POST PATCH /rest/v1/incidents','Consultar, reservar o actualizar metadatos según RLS.'),
('GET /rest/v1/incident_events','Obtener el historial de la incidencia propia.'),
('POST /storage/v1/object/incidence-photos/{ruta}','Transferir ArrayBuffer con MIME y autorización del usuario.'),
('POST /storage/v1/object/sign/incidence-photos/{ruta}','Solicitar JSON con enlace temporal; expiresIn 120.'),
('GET al enlace temporal','Descargar los bytes y mostrarlos con Image.')],[3.25,3.75])
sub('Relación entre fotografía e incidencia')
table(['Datos persistentes','Uso'],[
('id y owner_id','Identificar el reporte y su propietario autenticado.'),
('title description location category priority status','Describir el problema y su atención.'),
('photo_path y photo_state','Localizar el archivo y conocer si está pendiente, falló o está listo.'),
('photo_mime photo_bytes photo_sha256','Describir el archivo y verificar integridad.'),
('created_at updated_at archived','Ordenar, rastrear cambios y archivar sin borrar la evidencia.')],[3.2,3.8])
p('La tabla no guarda bytes, base64, contraseñas ni URLs firmadas. incident_events conserva ID del reporte, propietario, mensaje y fecha. Los borradores y los últimos cien metadatos se guardan localmente por usuario; la fotografía pendiente no se conserva al cerrar el proceso y debe seleccionarse otra vez.')

page('Evidencias de selección y carga')
p('Capturas de la aplicación real exportada a web, probada a 390 × 844 píxeles. Los servicios de autenticación, base de datos y almacenamiento son el proyecto Supabase real. El archivo de incidencia mostrado es una imagen sintética de prueba.')
pair(('Fotografía seleccionada','03-seleccion.png','Vista previa local, formato y tamaño antes de transferir.'),('Carga completada','05-carga-exitosa.png','Confirmación después de almacenar y relacionar la fotografía.'))

page('Evidencia de almacenamiento remoto')
p('La siguiente captura muestra el resultado de una consulta real a storage.objects y storage.buckets mediante la API de administración autorizada. Identifica ruta, contenedor, tamaño, MIME y public false. Es una presentación de la consulta, no una captura del Dashboard. El JSON original se incluye en evidencias/objetos-cloud.json.')
D.add_picture(str(E/'07-almacenamiento-cloud.png'),width=Inches(6.9))
p('La prueba de descarga recuperó 20 853 bytes. El SHA256 del archivo recuperado coincide con el de la imagen seleccionada: '+api['object']['sha256']+'.','Caption19')
sub('Comprobación en el panel del servicio')
p('Abrir https://supabase.com/dashboard/project/kizwbajlravjjhnbpkhm/storage/buckets y seleccionar incidence-photos. Los archivos están organizados por UUID de usuario y reporte. Mantener el contenedor privado; para visualizarlos desde la app se solicita una URL temporal con la sesión correspondiente.')

page('Recuperación y comportamiento sin conexión')
pair(('Fotografía recuperada','06-recuperada.png','Después de recargar la aplicación se consultan la referencia y la imagen remota.'),('Error de transferencia','04-error-conexion.png','Corte de red controlado durante la carga; mensaje visible y datos conservados.'))
p('El corte se produjo bloqueando la petición de carga en el navegador de pruebas. No se fingió una respuesta exitosa. Al retirar el bloqueo, el mismo formulario completó una carga real. Además se inició una nueva sesión mediante la API y se verificó que la referencia y el estado listo persistían en PostgreSQL. La prueba física de cierre y reapertura en Expo Go debe completarse en el teléfono del alumno.','Caption19')

page('Pruebas documentadas y justificación')
table(['Caso y justificación','Procedimiento y resultado'],[
('P1 Selección y carga válida\nConfirma el flujo principal.','Elegir PNG de 20 853 bytes, completar campos y subir. Resultado: archivo real almacenado, estado ready y URL temporal con imagen visible. Aprobado.'),
('P2 Recuperación persistente\nDescarta depender solo de la vista previa local.','Recargar la web y abrir el reporte; además iniciar sesión nuevamente mediante API. Resultado: misma referencia en la nube y fotografía recuperada. Aprobado en web; pendiente repetir en teléfono.'),
('P3 Formato no permitido\nEvita usar Storage para archivos ajenos al objetivo.','Pruebas de bytes con PDF y SVG renombrados; envío directo de application/pdf al bucket. Resultado: app rechaza la firma y servidor rechaza el MIME. Aprobado.'),
('P4 Pérdida de conexión\nVerifica que no se anuncie éxito inexistente.','Bloquear solo POST de carga en el navegador. Resultado: error visible, datos conservados y reintento real exitoso al restablecer la petición. Aprobado.'),
('P5 Acceso privado\nComprueba aislamiento entre usuarios.','Consultar sin autorización, usar URL pública y solicitar firma desde otra cuenta. Resultado: acceso denegado; la consulta de otra cuenta no devuelve la fila. Aprobado.'),
('P6 Límites y validación\nEvita transferencias innecesarias.','Casos unitarios de vacío, tamaño superior a 5 MiB y campos inválidos. Resultado: rechazo antes de transferir. Aprobado.')],[2.5,4.5])
p('Resultados: siete grupos de pruebas unitarias aprobados, siete comprobaciones contra Supabase aprobadas y cinco verificaciones del flujo de interfaz sin errores JavaScript. Se exportaron las plataformas web y Android. La exportación Android es el paquete JavaScript y recursos, no un APK instalado ni una prueba física.')
p('Los registros reproducibles se encuentran en pruebas-cloud.json y prueba-interfaz.json. La evidencia de la desconexión está identificada como fallo simulado; las cargas y descargas posteriores utilizaron el servicio real.')

page('Mecanismos de seguridad')
for title,text in [
('Autenticación y autorización','Supabase Auth entrega JWT por usuario. RLS compara owner_id con auth.uid() en tablas y exige que la carpeta inicial del objeto corresponda al mismo usuario. No hay acceso anónimo a los reportes.'),
('Transferencia y claves','HTTPS en todas las consultas remotas. El cliente contiene únicamente URL y clave publicable. service_role, claves secretas y contraseña de base de datos se excluyen del código, del documento y de Git.'),
('Privacidad de archivos','Bucket privado y enlaces firmados de 120 segundos. Estos enlaces son credenciales temporales: quien los posea puede usarlos durante su vigencia; no se publican ni se guardan en la tabla. Se solicitan nuevamente al abrir la imagen.'),
('Validación de archivos','Tipos JPEG, PNG y WebP y límite 5 MiB. La app revisa firma binaria; el servicio restringe MIME y tamaño. No incluye antivirus ni análisis de contenido en servidor; los límites MIME no sustituyen una inspección profunda de archivos.'),
('Sesión y datos locales','En móvil la sesión se guarda en SecureStore, con fragmentos para manejar su tamaño; en web se usa sessionStorage. Los metadatos y borradores locales usan AsyncStorage sin cifrado adicional. Evitar texto sensible y rostros en las evidencias.'),
('Errores y disponibilidad','Tiempo máximo de consulta de veinte segundos, indicadores por fase y mensajes visibles. Las consultas guardadas pueden verse como metadatos de caché; una fotografía remota requiere conectividad. El reintento conserva el identificador de incidencia.')]:
 sub(title);p(text)

page('Guía de ejecución y fuentes')
sub('Abrir el prototipo')
code('cd C:\\10moCuatri\\Vini\\Actividad20-NexoIncidencias\nnpm install\nnpx expo start --clear')
p('La copia local ya tiene .env con datos públicos de conexión. En otra computadora se debe copiar .env.example y completar la URL y clave publicable del proyecto. Usar Expo Go compatible con SDK 58 y escanear el QR nuevo; cerrar servidores antiguos de SDK 57. Si la red local impide conectar, utilizar npx expo start --tunnel. Crear una cuenta propia y confirmar el correo. Las credenciales de las cuentas de prueba permanecen solo en archivos locales privados.')
sub('Demostración sugerida')
for text in ['Iniciar sesión y mostrar el panel; crear un reporte con todos sus campos.','Elegir una fotografía desde galería o cámara y mostrar la vista previa.','Registrar la incidencia y explicar las cuatro fases de la carga.','Abrir el reporte, mostrar la imagen remota y cambiar su estado.','Cerrar y volver a abrir Expo Go en el teléfono para completar esa comprobación física.','Presentar el archivo en el bucket privado y las evidencias de error y acceso denegado.']:
 bullet(text)
sub('Verificaciones de código')
code('npm test\nnpm run build:web\nnpx expo export --platform android --output-dir dist-android')
p('Las pruebas cloud y de navegador están incluidas como scripts; requieren las credenciales de QA guardadas fuera de Git. No es necesario usar una clave administrativa para ejecutar la aplicación.')
sub('Documentación oficial consultada')
for label,url in [('Almacenamiento y buckets privados','https://supabase.com/docs/guides/storage/buckets/fundamentals'),('Políticas RLS para objetos','https://supabase.com/docs/guides/storage/security/access-control'),('Descargas y enlaces temporales','https://supabase.com/docs/guides/storage/serving/downloads'),('Selección de imágenes y cámara','https://docs.expo.dev/versions/latest/sdk/imagepicker/'),('Cuotas y planes','https://supabase.com/docs/guides/platform/billing-on-supabase'),('Condiciones del servicio','https://supabase.com/terms')]:
 p(label+'  '+url,'Caption19')
D.core_properties.title='Actividad 20 Almacenamiento privado de fotografías Nexo Incidencias'
D.core_properties.author='Lara Rodriguez Joel Alejandro'
D.core_properties.subject='Prototipo móvil documentación pruebas y evidencias'
out=ROOT/'Actividad20-Informe-NexoIncidencias.docx';D.save(out)
editable={'[Content_Types].xml','word/document.xml','word/styles.xml','word/_rels/document.xml.rels','docProps/core.xml','docProps/app.xml'}
with ZipFile(out) as z:parts={name:z.read(name) for name in z.namelist()}
with ZipFile(REF) as z:
 for name in z.namelist():
  if name not in editable:parts[name]=z.read(name)
with ZipFile(out,'w',ZIP_DEFLATED) as z:
 for name,data in parts.items():z.writestr(name,data)
with ZipFile(out) as z:
 for entry in INVENTORY['parts']:
  if entry['part'] not in editable:assert sha256(z.read(entry['part'])).hexdigest()==entry['sha256']
print('Informe creado con portada institucional preservada.')


