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
- Escaneo de seguridad: `bandit -r . --exclude ./.venv` (variante con reporte HTML en `nota.txt`).

## Arquitectura (no es obvio por los nombres de archivo)

- **Las plantillas viven en `views/` en la raíz, NO en `app/templates`** — `app/__init__.py` define `template_folder=views`. Los estáticos están en `app/static`. Layout base: `views/components/layout/base.html`.
- Los controladores son blueprints en `app/controllers/*.py` (un archivo por módulo), cada uno define un `<name>_blueprint`. **Todo blueprint nuevo debe importarse Y registrarse en `app/__init__.py`** — es el único lugar donde se registran (todos con `url_prefix='/'`).
- Modelos en `app/models/`: `database.py` expone `conectar` con `conexion1()` (BD principal `ituaccesoriobd`) y `conexion2()` (BD secundaria `seguridad`). La config de BD se lee del entorno con `os.getenv` por llamada — no desde `app.config`.
- Dos BD MySQL 8 en compose: `db1` (puerto host 3307) sembrada desde `./bd/ituaccesoriobd.sql`, `db2` (puerto host 3308) sembrada desde `./bd/seguridad.sql`. El SQL de seed solo se ejecuta cuando el volumen se crea por primera vez — después de editar un archivo `.sql` debes hacer `docker-compose down -v && up --build` para aplicarlo. `app/bd/` contiene copias de respaldo fechadas (no usadas por compose).
- La zona horaria del servidor MySQL se fuerza a `-04:00`.

## Autenticación y seguridad (estricta por diseño)

- Autenticación JWT vía cookies httponly (`access_token`/`refresh_token`, HS256, `app/utils/jwt_utils.py`). Protege rutas con `@jwt_required`, `@tiene_permiso('<modulo>', '<permiso>')` o `@solo_roles([...])` de `app/utils/decorators.py`. Para rutas AJAX devuelve JSON con estado 401/403, no redirects.
- `ENTORNO_PRUEBA=true` en `.env` es el **modo prueba**: desactiva Talisman (HTTPS+CSP), SeaSurf CSRF, reCAPTCHA y todos los decoradores de autenticación, e inyecta un usuario admin falso. Nunca lo subas activado.
- Talisman aplica una CSP estricta (sin `unsafe-inline` para scripts) definida en `app/__init__.py`. Agregar un nuevo CDN/script/stylesheet externo requiere añadir su origen a la CSP ahí, o será bloqueado.
- El login usa Google reCAPTCHA (omitido en modo prueba); el correo usa Gmail SMTP; las funciones de IA usan Gemini (`app/controllers/james.py`).
- **Subida de fotos desde el celular** (`taller_celular`): usa `@token_fotos_required` (decorador en `app/utils/decorators.py`), que valida una **firma corta sin estado** creada por `crear_firma_fotos()` (`app/utils/jwt_utils.py`): es `HMAC(SECRET_KEY, "id_orden|expira")` truncada a 10 bytes, con expiración de 5 min y ligada a `id_orden`. No se guarda nada en el servidor: la firma se verifica recalculándola (`verificar_firma_fotos`). El endpoint `POST /api/taller_celular/crear-token/<id_orden>` (protegido con `@jwt_required` + `@tiene_permiso('Taller','registrar')`) la emite; viaja en la URL del QR (`?t=...`) y el móvil la reenvía por form `t`.

## Gotcha de notificaciones / SSE

Las notificaciones viajan por un bus en memoria (`app/utils/notificaciones_bus.py`) compartido solo dentro de un proceso. En producción, gunicorn debe correr con **1 worker + threads** (CMD comentado en el Dockerfile) o las notificaciones SSE se rompen — nunca subas el número de workers sin un bus de mensajes externo.

## Respaldo de BD

```bash
docker exec -i ituaccesorio-web-1 mysqldump -u root -p'<pass_root>' --all-databases --routines --triggers > ituaccesoriobd.sql
```
