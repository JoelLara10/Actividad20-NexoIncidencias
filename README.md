# Nexo Incidencias · Actividad 20

Prototipo individual de Lara Rodriguez Joel Alejandro, IDGS 101, Desarrollo Móvil Integral. React Native y Expo SDK 58 con Supabase Auth, PostgreSQL y Storage privado.

## Funciones

- Registro e inicio de sesión; cada usuario ve sus propios reportes.
- Formulario con ubicación, categoría, prioridad y descripción; borrador local.
- Cámara o galería, vista previa, validación de firma JPEG/PNG/WebP y límite de 5 MB.
- Carga real con estados, referencia persistente, SHA256 y reintento del mismo reporte.
- Fotografía remota con URL firmada de 120 segundos, renovación y visor completo.
- Panel de estadísticas, búsqueda, filtros, seguimiento de estado e historial; archivar/restaurar.
- Caché de metadatos por usuario y mensajes ante fallas. No es una cola de carga en segundo plano.

## Abrir en el teléfono

```powershell
cd C:\10moCuatri\Vini\Actividad20-NexoIncidencias
npm install
npx expo start --clear
```

La carpeta entregada ya incluye `.env` local conectado al proyecto real. Usa Expo Go compatible con SDK 58 y escanea este nuevo QR. Teléfono y PC deben estar en la misma red; si falla, prueba `npx expo start --tunnel`. No abras un servidor antiguo de SDK 57. La cámara y sus permisos deben comprobarse en el teléfono.

Al clonar el repositorio, copia `.env.example` a `.env` y completa la URL y la clave **publicable o anon** de Supabase. Nunca uses `service_role` ni `sb_secret_` en `EXPO_PUBLIC_*`. Crear cuenta requiere confirmar el correo antes de iniciar sesión. Las cuentas de QA son exclusivamente locales y sus contraseñas no se publican.

## Servicio y configuración

Proyecto: `kizwbajlravjjhnbpkhm` en la organización `Joel Lara - Actividades Moviles`, plan gratuito al crearse. [Dashboard](https://supabase.com/dashboard/project/kizwbajlravjjhnbpkhm).

Bucket: `incidence-photos`, privado, máximo 5 242 880 bytes; tipos permitidos `image/jpeg`, `image/png`, `image/webp`. Las cuotas y disponibilidad del plan gratuito dependen de Supabase; el proyecto puede pausarse por inactividad.

Para otro proyecto dedicado, ejecuta una sola vez `supabase/migrations/202611070001_private_incidents.sql` desde su editor SQL. La migración define tablas, desencadenadores, permisos RLS y bucket; no debe ejecutarse de nuevo sobre el proyecto ya configurado. No desactives RLS ni conviertas el bucket en público.

## Flujo y endpoints HTTPS

Base: `https://kizwbajlravjjhnbpkhm.supabase.co`.

1. Auth: `POST /auth/v1/signup`, `POST /auth/v1/token?grant_type=password`.
2. Metadatos: `GET/POST/PATCH /rest/v1/incidents`; `GET /rest/v1/incident_events`.
3. Archivo: `POST /storage/v1/object/incidence-photos/{usuario}/{incidencia}/{hash}.png` (también jpg/webp).
4. Acceso temporal: `POST /storage/v1/object/sign/incidence-photos/{ruta}`, `expiresIn: 120`.
5. Descargar: `GET` al enlace firmado devuelto por el servicio.

El SDK procesa las respuestas JSON (`data`, `error`). Solo se marca `ready` tras cargar el archivo; un trigger verifica que el objeto exista. Se conservan en PostgreSQL ID, propietario, texto, estado, categoría, prioridad, path, MIME, bytes, SHA256 y fechas. Las imágenes permanecen en Storage; no se almacena base64 ni el enlace temporal en la tabla.

## Seguridad y límites

RLS limita tablas y objetos al propietario autenticado. Acceso anónimo y otros usuarios se rechazan. Una URL firmada es una autorización temporal: quien la obtenga puede usarla durante su vigencia; no se publica ni se guarda de forma persistente. La sesión móvil usa SecureStore y la web sessionStorage. Los borradores y metadatos recientes usan AsyncStorage sin cifrado adicional; no incluir información sensible. La app revisa bytes; el servidor limita MIME y tamaño, pero no incluye antivirus ni un decodificador de imágenes del lado servidor. El límite mostrado es propio del prototipo, no el máximo comercial de Supabase.

## Pruebas y evidencias

```powershell
npm test
npm run build:web
npx expo export --platform android --output-dir dist-android
```

`evidencias/pruebas-cloud.json`: siete verificaciones reales de carga, integridad, persistencia y acceso. `prueba-interfaz.json`: navegador a 390×844 con servicios reales; el corte de red se provoca bloqueando únicamente la petición de carga. `objetos-cloud.json`: consulta real del inventario remoto. Las imágenes de incidencia utilizadas son sintéticas y están identificadas como tales. Las capturas de almacenamiento y seguridad se generan con datos reales, sin imitar el Dashboard.

`npm run test:live` requiere `.auth/keys.json` local con credenciales administrativas para crear usuarios de prueba; no son dependencias de la app. Estos archivos se excluyen del repositorio. La prueba crea un reporte nuevo en la nube. `tests/browser.cjs` requiere Playwright, Chrome, servidor web local y `.auth/test-users.json`; admite `PLAYWRIGHT_PATH`, `CHROMIUM_PATH`, `NEXO_ROOT`. Nunca publicar esos archivos privados.

Se verificaron flujo web y exportación Android. No se afirma prueba física de cámara ni cierre/reapertura de Expo Go; sí se verificaron recarga web y recuperación con un nuevo inicio de sesión. El texto del borrador persiste; la imagen debe seleccionarse nuevamente si se cierra antes de terminar la carga.

## Documentación oficial

- [Supabase Storage y buckets privados](https://supabase.com/docs/guides/storage/buckets/fundamentals)
- [Control de acceso RLS](https://supabase.com/docs/guides/storage/security/access-control)
- [Descargas y URLs firmadas](https://supabase.com/docs/guides/storage/serving/downloads)
- [Expo ImagePicker](https://docs.expo.dev/versions/latest/sdk/imagepicker/)
- [Condiciones de Supabase](https://supabase.com/terms)

El informe Word contiene portada, configuración, código explicado, capturas, pruebas y mecanismos de seguridad.
