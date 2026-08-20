# AGENTS.md

Fábrica de aplicaciones Flask (Python 3.12) para "Ituaccesorio", un sistema de gestión de tienda de accesorios. Todo el texto de la interfaz y los comentarios de código están en **español** — sigue esa convención. No existen pruebas unitarias automatizadas (no hay pytest); los únicos assets de prueba son `pruebas/locustfile.py` (prueba de carga) y `bandit` (escaneo de seguridad).

## Ejecución / desarrollo (Docker es el único flujo soportado)

```bash
docker-compose up --build   # construye + inicia (también aplica cambios; hot-reload vía montaje .:/app)
docker-compose up           # inicia contenedores existentes
docker-compose stop
docker-compose down -v      # elimina volúmenes de BD → reinicia ambas BD desde el SQL de seed
```

- El `.env` en la raíz es obligatorio para compose (gitignored; `.env Ejemplo` es la plantilla). `FLASK_DEBUG=1` activa el modo debug.
- `run.py` llama a `create_app()`; en desarrollo se ejecuta `python run.py` dentro del contenedor.
- Escaneo de seguridad: `bandit -r . --exclude ./.venv` (reporte HTML: `bandit -r . --exclude ./.venv -f html -o reporte_seguridad.html`). `nota.txt` tiene más apuntes sueltos del proyecto.

## Arquitectura (no es obvio por los nombres de archivo)

- **Las plantillas viven en `views/` en la raíz, NO en `app/templates`** — `app/__init__.py` define `template_folder=views`. Los estáticos están en `app/static`. Layout base: `views/components/layout/base.html`. Componentes UI reutilizables (modales) en `views/components/ui/`. La mayoría de vistas son planas en `views/`, pero el módulo de ventas usa subdir: `views/ventas/{catalogo,pagos,reportes,validacion}.html`.
- Los controladores son blueprints en `app/controllers/*.py` (un archivo por módulo), cada uno define un `<name>_blueprint`. **Todo blueprint nuevo debe importarse Y registrarse en `app/__init__.py`** — es el único lugar donde se registran (todos con `url_prefix='/'`). Nota: `app/controllers/buscar_controller.py` es un archivo vacío (0 bytes) sin registrar — no es un endpoint real.
- Validadores de entrada reutilizables en `app/utils/validators.py` (`validar_texto`, `validar_numero`, etc.) — úsalos en nuevos controladores en lugar de reimplementar.
- CSS/JS por página: cada vista extiende `base.html` con `{% block head_extra %}` (su CSS) y `{% block scripts %}` (su JS). `base.html` ya carga JS **global en todas las páginas** (`modal.js`, `feedback-modal.js`, `table-tools.js`, `notificaciones.js`, `field-validator.js`, `navbar.js`, con `defer`) — no los dupliques en `navbar.html` ni en las vistas (hubo un bug donde `notificaciones.js` se cargaba dos veces → dos conexiones SSE). Si un script global toca elementos que solo existen en algunas vistas (p. ej. el carrito en `navbar.js`), protege con `if (el)` antes de usarlo.
- Modelos en `app/models/`: `database.py` define la **clase base `conectar`**; los modelos heredan de ella (`class Foo(conectar)`) y obtienen conexiones con `self.conexion1()` (BD principal `ituaccesoriobd`) y `self.conexion2()` (BD secundaria `seguridad`). La config de BD se lee del entorno con `os.getenv` por llamada — no desde `app.config`. No se puede llamar a `conexion1`/`conexion2` sin heredar.
- Dos BD MySQL 8 en compose: `db1` (puerto host 3307) sembrada desde `./bd/ituaccesoriobd.sql`, `db2` (puerto host 3308) sembrada desde `./bd/seguridad.sql`. El SQL de seed solo se ejecuta cuando el volumen se crea por primera vez — después de editar un archivo `.sql` debes hacer `docker-compose down -v && up --build` para aplicarlo. `app/bd/` contiene copias de respaldo fechadas (no usadas por compose).
- La zona horaria del servidor MySQL se fuerza a `-04:00`.

## Autenticación y seguridad (estricta por diseño)

- Autenticación JWT vía cookies httponly (`access_token`/`refresh_token`, HS256, `app/utils/jwt_utils.py`). Protege rutas con `@jwt_required`, `@tiene_permiso('<modulo>', '<permiso>')` o `@solo_roles([...])` de `app/utils/decorators.py`. Para rutas AJAX devuelve JSON con estado 401/403, no redirects. `rol_id == 1` o `rol_nombre == 'admin'` bypassa todos los chequeos de permisos.
- **`g.user` es un `dict` en producción** (vienen del payload JWT, los decoradores acceden con `.get()`) **pero un `SimpleNamespace` en modo prueba** (lo inyecta `before_request` en `app/__init__.py`). Los templates usan acceso por atributo (`g.user.rol_id`); los decoradores usan `.get()`. En modo prueba los decoradores se short-circuitan antes de tocar `g.user`, así que no hay conflicto — pero ten en cuenta la dualidad al añadir decoradores o lógica que inspeccione `g.user` en ambos modos.
- `ENTORNO_PRUEBA=true` en `.env` es el **modo prueba**: desactiva Talisman (HTTPS+CSP), SeaSurf CSRF, reCAPTCHA y todos los decoradores de autenticación, e inyecta un usuario admin falso. Nunca lo subas activado.
- Talisman aplica una CSP estricta definida en `app/__init__.py`. Reglas concretas que rompen cosas si se ignoran:
  - **Sin `unsafe-inline` para scripts ni para estilos.** Un `<script>` inline o un atributo `style="..."` en cualquier vista queda bloqueado en consola y NO se ejecuta/aplica.
  - **Scripts inline**: el único permitido es el cargador de tema en `views/components/layout/base.html` (whitelisted por un hash SHA-256 en `script-src` y `script-src-elem`). Si editas el contenido de ese `<script>`, recalcula el hash (base64 del texto exacto entre `<script>` y `</script>`) y actualízalo en la CSP, o el navegador lo bloqueará y el tema no se aplicará antes del primer render (parpadeo/FOUC).
  - **Estilos inline**: usa clases CSS, nunca `style="..."`. Para hints de formulario ya existe `.field-hint` en `app/static/css/theme.css` (no reintroduzcas `style=` en `.field-hint`).
  - Agregar un CDN/script/stylesheet externo nuevo requiere añadir su origen a la directiva correspondiente (`script-src`/`script-src-elem`/`style-src`/`img-src`/...) ahí, o será bloqueado.
- El login usa Google reCAPTCHA (omitido en modo prueba); el correo usa Gmail SMTP. Las funciones de IA usan Gemini (`app/services/james.py`, modelo `gemini-2.5-flash`; el controller es `app/controllers/james.py`). Requiere `GEMINI_API_KEY` en `.env` (no aparece en `.env Ejemplo`): `IAService()` se instancia al importar el blueprint, así que sin esa variable la app ni arranca.
- **Subida de fotos desde el celular** (`taller_celular`): usa `@token_fotos_required` (decorador en `app/utils/decorators.py`), que valida una **firma corta sin estado** creada por `crear_firma_fotos()` (`app/utils/jwt_utils.py`): es `HMAC(SECRET_KEY, "id_orden|expira")` truncada a 10 bytes, con expiración de 5 min y ligada a `id_orden`. No se guarda nada en el servidor: la firma se verifica recalculándola (`verificar_firma_fotos`). El endpoint `POST /api/taller_celular/crear-token/<id_orden>` (protegido con `@jwt_required` + `@tiene_permiso('Taller','registrar')`) la emite; viaja en la URL del QR (`?t=...`) y el móvil la reenvía por form `t`. Las fotos se guardan en `app/static/img/evidencias/taller/<id_orden>/` (en BD se guarda la URL relativa `/static/img/...`), con un máximo de 20 fotos de 10 MB cada una.

## Gotcha de notificaciones / SSE

Las notificaciones viajan por un bus en memoria (`app/utils/notificaciones_bus.py`) compartido solo dentro de un proceso. En producción, gunicorn debe correr con **1 worker + threads** (CMD comentado en el Dockerfile) o las notificaciones SSE se rompen — nunca subas el número de workers sin un bus de mensajes externo.

## Respaldo de BD

```bash
docker exec -i ituaccesorio-web-1 mysqldump -u root -p'<pass_root>' --all-databases --routines --triggers > ituaccesoriobd.sql
```
