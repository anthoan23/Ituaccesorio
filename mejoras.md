# Mejoras en las validaciones (`app/utils/validators.py`)

> Documento de análisis y remediación. Fecha: 22/11/2026.
> Línea base: **2287 pruebas unitarias en verde** → Estado final: **2385 en verde**.
> `app/utils/validators.py` es la **única fuente de verdad** para validar entradas; los modelos y
> controladores solo la llaman, y **ningún límite va fijado dentro de una función**: todo se pasa
> por parámetro en cada llamada.

---

## Remediación 3: eliminación de wrappers innecesarios

Caso señalado: `validar_numero_entero` era un wrapper de una línea sobre `validar_decimal`.
Se auditaron los 13 validadores y se eliminaron **4 funciones sin regla propia**:

| Función eliminada | Era | Reemplazo |
|---|---|---|
| `validar_numero_entero(valor, nombre, min_valor=0, max_valor=None)` | Wrapper de una línea de `validar_decimal(max_decimales=0)` | `validar_decimal(valor, nombre, max_decimales=0, min_valor=None, max_valor=None)` — mismo mensaje ("debe ser un número entero válido") |
| `validar_celular(valor, min, max, nombre, obligatorio)` | Alias exacto de `validar_numero` (dígitos + longitud, mismos mensajes al 100%) | `validar_numero(valor, 11, 11, "Celular", obligatorio=...)` — la regla real de móviles sigue siendo `validar_celular_venezolano` (prefijos) |
| `validar_codigo_factura(valor, min, max, nombre)` | Mismo charset que el validador genérico (letras+números+guiones, sin espacios) | `validar_texto_numero(valor, 1, 20, "Factura", permitir_espacios=False, caracteres_extra="-")` |
| `validar_limite_credito(valor, nombre)` | "Decimal opcional no negativo" sin límite de decimales, y en `proveedores.py` era casi código muerto (el bloque inline ya rechazaba negativos/no-numéricos con sus propios `ValueError` y doble-normalizaba) | `validar_decimal(valor, "Límite de crédito", max_decimales=2, min_valor=0, obligatorio=False)` — alineado con la BD (`DECIMAL(12,2)`) |

Para soportarlo, `validar_numero` y `validar_decimal` ganaron el parámetro `obligatorio` (patrón
uniforme en todo el módulo), y `validar_decimal` dejó de tener defaults
(`max_decimales=2, min_valor=0` ahora son obligatorios en la firma): **todas las llamadas de la
app ya pasaban esos valores explícitos**, así que nada queda oculto.

**Módulos afectados** (las reglas por módulo quedaron idénticas salvo `limite_credito`):
- `entrega.py`: estado → `validar_decimal(max_decimales=0)`; factura → `validar_texto_numero`.
- `reportes_ventas.py` y `validacion_pagos.py`: factura → `validar_texto_numero`.
- `clientes.py` (×4) y `login.py`: teléfono → `validar_numero(…, obligatorio=…)`.
- `proveedores.py`: límite de crédito → `validar_decimal(max_decimales=2, min_valor=0, obligatorio=False)`.
  Único cambio de regla del lote: ahora se rechazan límites con más de 2 decimales (antes se
  aceptaban y MySQL los redondeaba silenciosamente; la columna es `DECIMAL(12,2)`).
- `app/controllers/ventas.py`: se eliminó un import sin usar (`validar_sin_caracteres_especiales`).
- Tests: se actualizaron los 6 asserts del mensaje de factura
  ("…letras, números y guiones" → "…letras, números (sin espacios) y guiones") y las clases de
  `test_validators.py` de los wrappers eliminados.

**Estado final del módulo — 9 funciones, cada una con regla propia:**
`normalizar_numero_decimal`, `validar_texto`, `validar_texto_numero`, `validar_numero`,
`validar_email`, `validar_contraseña`, `validar_rif`, `validar_celular_venezolano`,
`validar_decimal`. Todo lo demás es parametrizable por llamada.

Además, los helpers privados `_NOMBRES_CARACTERES_EXTRA`, `_describir_caracteres_extra` y
`_unir_con_y` (solo usados por `validar_texto_numero`) se plegaron dentro de esa función como
lógica local del mensaje de error: `validators.py` ya no tiene helpers a nivel de módulo.

---

## Remediación 2: unificación de la familia de validadores de texto

Además de todo lo anterior, se eliminó la duplicación entre los validadores de texto.
Antes existían **7 funciones** para el mismo concepto (letras con acentos [+ números] [+ espacios]
[+ caracteres extra]):

| Antes (eliminadas) | Reemplazadas por |
|---|---|
| `validar_solo_letras` | `validar_texto(valor, min_len, max_len, nombre_campo, permitir_espacios=True)` |
| `validar_solo_letras_numeros` | `validar_texto_numero(valor, min_len, max_len, nombre_campo, permitir_espacios=True, caracteres_extra="", obligatorio=True)` |
| `validar_sin_caracteres_especiales` | `validar_texto_numero(..., obligatorio=False)` cuando el campo es opcional |
| `validar_nombre_producto` | `validar_texto_numero(..., caracteres_extra="-()")` |
| `validar_direccion_proveedor` | `validar_texto_numero(..., obligatorio=False, caracteres_extra="-.,#()/")` |

Quedaron **solo dos** validadores de texto: `validar_texto` (letras) y `validar_texto_numero`
(letras + números), ambos con todo parametrizable:

- `min_len` y `max_len` **sin defaults** (`min_len=1, max_len=255` eliminados): cada módulo pasa
  explícitamente sus límites — nada de reglas ocultas.
- `permitir_espacios`: para campos de una sola palabra (`Modulos`, colores, capacidades).
- `caracteres_extra`: para conjuntos extra de caracteres por módulo (razones sociales `.-&`,
  productos `-()`, direcciones `-.,#()/`), con mensajes generados automáticamente
  ("…letras, números, acentos, espacios, puntos, guiones y ampersand (&).").
- `obligatorio`: opcionalidad explícita en vez de trampas de `min_len=0`.

**Módulos afectados por esta unificación** (solo cambió el nombre de la función llamada; las reglas
de cada módulo se conservan igual): `clientes.py` (razón social, direcciones), `modulos.py`,
`productos.py` (clase, marca, nombre de producto), `proveedores.py` (nombre, dirección),
`roles.py`, `usuarios.py`, `tradein_empleados.py` (color, capacidad, patrón, búsqueda),
`entrega.py` (dirección), `reportes_ventas.py`, `validacion_pagos.py`, `venta.py` (referencia).
`app/controllers/ventas.py` tenía un import sin usar de `validar_sin_caracteres_especiales` → eliminado.
En `tests/` solo se actualizaron los textos de los mensajes unificados
("no puede contener caracteres especiales" → "solo puede contener letras, números, acentos y espacios",
etc.).

Resultado: `validators.py` pasó de 18 a **13 validadores** y la suite quedó en verde
(los wrappers restantes se depuraron en la Remediación 3, que deja el módulo en 9 funciones).

---

## 1. Qué se encontró (análisis)

### 1.1 Uso real de cada validador (antes de la remediación)

| Validador | Usos externos | Estado |
|---|---|---|
| `validar_numero` | 51 | En uso |
| `validar_texto_numero` | 43 | En uso |
| `validar_sin_caracteres_especiales` | 19 | En uso |
| `validar_texto` | 16 | En uso |
| `validar_decimal` | 10 | En uso |
| `validar_solo_letras` | 9 | En uso |
| `validar_solo_letras_numeros` | 8 | En uso |
| `validar_codigo_factura` | 6 | En uso |
| `validar_email` | 3 archivos | Parcial (duplicado en 2 modelos) |
| `validar_celular_venezolano` | 3 | En uso |
| `validar_numero_entero` | 4 | En uso (pero **roto**, ver bug B3) |
| `validar_contraseña` | 4 | En uso |
| `normalizar_numero_decimal` | 2 | En uso |
| `validar_rif` | 2 archivos | Parcial (duplicado en 2 modelos) |
| `validar_direccion_proveedor` | 1 | En uso |
| `validar_limite_credito` | 1 | En uso |
| `validar_nombre_producto` | 2 | En uso |
| **`validar_celular`** | **0** | **Muerto** (los "6 usos" eran variables locales con ese nombre) |
| **`validar_decimal_positivo`** | **0** | **Muerto** |
| **`validar_cedula_venezolana`** | **0** | **Muerto** (solo la llamaba `validar_campo_comun`) |
| **`validar_sin_espacios`** | **0** | **Muerto** (ídem) |
| **`validar_campo_comun`** | **0** | **Muerto** e incompleto (no soportaba email/telefono/rif/decimal) |

Además, **no existían pruebas** del módulo: `test_validators.py` había sido borrado (solo quedó un
`.pyc` huérfano en `__pycache__`).

### 1.2 Bugs concretos (con ejemplo reproducible)

| # | Severidad | Bug | Ejemplo | Antes | Ahora |
|---|---|---|---|---|---|
| B1 | 🔴 Alta | `validar_texto` no hacía `strip()` y el patrón permite `\s` | `validar_texto("   ", 3, 30, "Nombre")` | **Válido** (nombre de solo espacios entraba a la BD) | Rechazado: "no puede estar vacío" |
| B2 | 🔴 Alta | El regex de `validar_email` aceptaba puntos consecutivos y puntos mal ubicados | `a@b..com`, `.a@b.com`, `a.@b.com` | **Válido** | Rechazado |
| B3 | 🔴 Alta | `validar_decimal` con `max_decimales=0` generaba el patrón inválido `\d{1,0}` → `re.error` en tiempo de ejecución | `validar_numero_entero(0, "Estado")` | **Excepción 500** (la suite lo esquivaba con un fixture que parcheaba la función) | Funciona |
| B4 | 🔴 Alta | `validar_decimal` trataba el entero `0` como vacío (`if not valor`) | estado `0` (Pendiente) en Entrega | **Rechazado** como "vacío" | Válido |
| B5 | 🔴 Alta | Misma entidad con reglas distintas por módulo: **3 regex de email** (clientes, ordenes_servicio, login), **2 de RIF**, **2 de teléfono**, **2 de razón social**; cédula 6-8 vs 6-9 vs 6-15 | `a@b.c` válido en login, inválido en proveedores | Inconsistente | Una sola regla |
| B6 | 🟠 Media | `validar_decimal` no aceptaba negativos aunque tenía `min_valor`, ni el formato `"1.234,56"` que `normalizar_numero_decimal` sí maneja; usaba `float` | `-5` con `min_valor=0` | Mensaje engañoso | "debe ser mayor o igual a 0" |
| B7 | 🟠 Media | `validar_decimal` comparaba contra límites `float` (p. ej. `9999999999.99`) → en el valor exacto del límite fallaba por precisión binaria | `9999999999.99` con `max_valor=9999999999.99` | Falso rechazo en el borde | Comparación con `Decimal(str(max_valor))` |
| B8 | 🟠 Media | `validar_contraseña` hacía `strip()` silencioso: validaba una contraseña distinta a la que se hasheaba | `"  clave123  "` | Aceptada (y guardada con espacios) | Rechazada: "no puede contener espacios" |
| B9 | 🟡 Baja | `re.match(...$)` permite un salto de línea final (`"Juan\n"` pasa el patrón) | — | Ambiguo | Todos los patrones usan `re.fullmatch` + `strip` |
| B10 | 🟡 Baja | Código muerto: `si_positivo` sin uso en `normalizar_numero_decimal`, chequeo de decimales inalcanzable en `validar_decimal`, líneas vacías en `validar_numero_entero` | — | — | Eliminado |
| B11 | 🟡 Baja | API inconsistente: obligatoriedad implícita distinta por función, `validar_email` con límite 50 fijo y sin `nombre_campo` | — | — | Parámetros `obligatorio`, `nombre_campo`, `max_len` documentados |

### 1.3 Duplicados inline eliminados

| Archivo | Duplicado eliminado | Reemplazo |
|---|---|---|
| `app/models/clientes.py` | `_validar_email` (regex propio) | `validar_email()` |
| `app/models/clientes.py` | `_validar_telefono` (`^\d{11}$`) | `validar_celular(…, 11, 11, obligatorio=…)` |
| `app/models/clientes.py` | `_validar_direccion` (solo longitud) | `validar_direccion_proveedor(…, 40)` |
| `app/models/clientes.py` | `patron_rif` ×3 (`eliminar_cliente`, `registrar_cliente_juridico`, `actualizar_cliente_juridico`) | `validar_rif(tipos="JE")` |
| `app/models/clientes.py` | `patron_razon_social` ×2 | `validar_solo_letras_numeros(caracteres_extra=".-&")` |
| `app/models/ordenes_servicio.py` | `_validar_email` y `_validar_rif` | `validar_rif(tipos="JE", obligatorio=True)` / `validar_email` |
| `app/controllers/login.py` | tercer regex de email + regla manual de celular (≥10 dígitos) | `validar_email()` / `validar_celular(11, 11, obligatorio=True)` |

> Nota: algunos validadores citados en esta tabla fueron renombrados/fusionados en las
> Remedaciones 2 y 3 (`validar_celular` → `validar_numero`, `validar_solo_letras_numeros` y
> `validar_direccion_proveedor` → `validar_texto_numero(...)`). La tabla refleja el estado
> histórico de esta remediación; el estado final del módulo está en la sección de Remediación 3.

---

## 2. Qué se solucionó y cómo

### 2.1 `app/utils/validators.py` (reescrito)

- **Todos los patrones con `re.fullmatch`** y valores con `strip()` (B1, B9).
- **`validar_email(valor, nombre_campo="correo", max_len=50, obligatorio=False)`**: parametrizada;
  mantiene los mensajes de ayuda (símbolo @, dominio, punto) y ahora rechaza dominios con etiquetas
  vacías (`b..com`), TLD de menos de 2 letras (`b.c`) y puntos mal ubicados en el usuario (B2).
- **`validar_rif(valor, min_len=8, max_len=15, nombre_campo="RIF", tipos="JEV", obligatorio=False)`**:
  acepta `J-12345678-9` y `J123456789` (guiones opcionales) y minúsculas (normaliza a mayúsculas);
  `tipos="JE"` limita las letras para clientes jurídicos. El mensaje de ejemplo se genera según `tipos`.
- **`validar_celular(valor, min_len=11, max_len=11, nombre_campo, obligatorio=False)`**: rescatada del
  olvido; es el validador genérico de teléfonos (la usa `clientes` y `login`).
  *(Posteriormente fusionada con `validar_numero` — ver Remediación 3.)*
- **`validar_celular_venezolano(…, obligatorio=True)`**: conserva sus mensajes exactos y acepta campos
  opcionales con `obligatorio=False` (la usa `proveedores` con celular opcional).
- **`validar_decimal` reescrita sobre `normalizar_numero_decimal`** (B3, B4, B6, B7): admite coma,
  punto y formatos mixtos; negativos solo si `min_valor < 0`; comparación de límites con `Decimal`;
  mensaje correcto para enteros (`"2.5"` → "debe ser un número entero válido"); sin código muerto.
- **`validar_numero_entero`**: wrapper limpio de `validar_decimal(max_decimales=0)`.
  *(Posteriormente eliminado por innecesario — ver Remediación 3.)*
- **`validar_contraseña`**: valida el valor **sin** `strip` — lo validado es exactamente lo que se
  hashea (B8); los espacios en bordes ahora se rechazan.
- **`validar_solo_letras_numeros(…, caracteres_extra="")`**: nuevo parámetro para conjuntos extra de
  caracteres (p. ej. `".-&"` para razones sociales), con mensaje legible generado automáticamente
  ("…letras, números, espacios, puntos, guiones y ampersand (&)").
  *(Posteriormente fusionada con `validar_texto_numero` — ver Remediación 2.)*
- **Validadores muertos eliminados**: `validar_decimal_positivo`, `validar_cedula_venezolana`,
  `validar_sin_espacios`, `validar_campo_comun`. `validar_cedula_venezolana` se eliminó porque su
  `strip` de guiones validaba una cédula distinta a la que se almacenaría (riesgo de datos
  inconsistentes); la regla de cédula queda explícita en los llamadores como
  `validar_numero(cedula, 6, 8, "Cédula")`, que ya es un validador compartido.
- `normalizar_numero_decimal`: sin variable muerta (`si_positivo`).

### 2.2 `app/models/clientes.py`

- Eliminados `_validar_email`, `_validar_telefono`, `_validar_direccion`, `patron_rif` (×3) y
  `patron_razon_social` (×2). Los 4 métodos (registrar/actualizar natural, registrar/actualizar
  jurídico) y `eliminar_cliente` ahora llaman a los validadores compartidos.
- **RIF jurídico**: se acepta ahora con o sin guiones y en minúsculas, y **se normaliza a mayúsculas
  antes de guardar** (`rif = self.Rif_cliente.strip().upper()`); igual en `eliminar_cliente`.
- `eliminar_cliente` también normaliza el ID con `.upper()` para búsquedas consistentes.

### 2.3 `app/models/ordenes_servicio.py`

- Eliminados `_validar_email` y `_validar_rif`.
- `crear_orden` normaliza `id_cliente` con `.strip().upper()` y valida RIF con
  `validar_rif(id_cliente_val, tipos="JE", obligatorio=True)` → las búsquedas/inserts usan el ID canónico.

### 2.4 `app/controllers/login.py` (registro de perfil de cliente)

- Celular: se conserva la limpieza de `[\s\-()+ ]` y luego se valida el valor limpio con
  `validar_celular(…, 11, 11, "Celular", obligatorio=True)` (hoy `validar_numero`, ver Remediación 3).
  Antes exigía "mínimo 10 dígitos" en el
  controlador pero el modelo exigía 11 → ahora ambas capas piden lo mismo.
- Correo: `validar_email(correo)` (opcional, igual que antes).

### 2.5 Otros módulos tocados

| Archivo | Cambio | Efecto |
|---|---|---|
| `app/models/empleados.py` | `validar_email(correo, obligatorio=True)` ×2 | Igual de estricto que antes; mensajes idénticos |
| `app/models/proveedores.py` | `validar_email(self.correo)` sin guard (obligatorio=False) | Mismo comportamiento, menos código |
| `app/models/entrega.py` | `validar_numero_entero(self.estado, "Estado", min_valor=None, max_valor=None)` (hoy `validar_decimal(…, max_decimales=0)`, ver Remediación 3) | El rango 0-3 lo decide el modelo con su mensaje legible; el validador solo valida formato. El estado `0` ahora **sí** es válido (bug B4) |
| `app/models/test.py` | Cédula `validar_numero(…, 6, 9, …)` → `6, 8` | Se elimina la regla 6-9 única que quedaba |

### 2.6 Pruebas

- **Nuevo `tests/pruebas unitarias/test_validators.py`** (99 casos en su versión final): cubre los
  9 validadores,
  los bugs corregidos como casos de regresión (solo espacios, `a@b..com`, entero 0, límite exacto
  de `validar_decimal`, `"-5"`, `"1.234,56"`) y la opcionalidad de cada función.
- **`test_entrega.py`**: eliminado el fixture `validador_estado_sin_regex` que parcheaba
  `validar_numero_entero` **para esquivar el bug B3** (su docstring lo documentaba); ahora se
  prueba el camino real. Los casos "estado no entero" esperan el mensaje unificado del validador.
  Añadido `test_estado_cero_pendiente_es_valido` (regresión de B4).
- **`test_ordenes_servicio.py`**: las clases `TestValidarEmail`/`TestValidarRif` ya no prueban
  métodos privados borrados del modelo; prueban los validadores compartidos.
- **`test_clientes.py`**: mensajes actualizados a los del validador compartido; los RIF sin guiones
  y en minúsculas pasaron de "inválidos" a "válidos" (con tests nuevos que verifican la
  normalización a mayúsculas al guardar).
- **`test_venta.py` / `test_tradein_empleados.py`**: mensajes de `validar_decimal` actualizados
  (negativos → "mayor o igual a 0"; más de 2 decimales → mensaje específico).
- **`test_test.py`**: límite de cédula 9 → 8 dígitos.
- Nota: la prueba de integración `test_tradein_empleados_integracion.py` ya esperaba el mensaje
  nuevo ("debe ser mayor o igual a 0") para `valor_pagado: -5`; con el fix, esa prueba que
  estaba rota a nivel de unidad ahora es coherente.

---

## 3. Módulos afectados y cómo los afecta

| Módulo | Impacto |
|---|---|
| **Clientes (natural y jurídico)** | Nombres "solo espacios" ya no se aceptan; correo con `a@b..com` ya no se acepta; RIF se acepta sin guiones/minúsculas y **se guarda en mayúsculas**; dirección restringida al mismo conjunto de caracteres que proveedores (`- . , # ( ) /`) — antes aceptaba cualquier carácter; teléfono exige exactamente 11 dígitos (igual que antes). Mensajes de error nuevos (mismos textos que el resto del sistema). |
| **Órdenes de servicio** | RIF de cliente jurídico validado con la regla compartida (J/E, guiones opcionales, se normaliza a mayúsculas antes de buscar/guardar); mensajes nuevos. |
| **Entregas** | El estado `0` (Pendiente) ya no se rechaza; el rango 0-3 sigue validado por el modelo. Sin más cambios de reglas. |
| **Login / perfil de cliente** | El celular del registro exige exactamente 11 dígitos (antes bastaban 10 y luego fallaba en el modelo); mensajes nuevos. |
| **Empleados / Usuarios** | Sin cambios de reglas; contraseñas con espacios en los extremos ahora se rechazan (antes pasaban el validador y se guardaban con espacios). |
| **Proveedores** | Sin cambios de reglas de charset; `limite_credito` ahora rechaza más de 2 decimales (Remediación 3, alineado con `DECIMAL(12,2)`). |
| **Venta / Pagos / Reportes / Trade-in** | `validar_decimal` acepta ahora `"1.234,56"` y mensajes más claros para negativos/decimales; el valor límite exacto (`9999999999.99`) ya no es rechazado por error de precisión. |
| **Test (módulo test.py)** | Cédula de empleado valida 6-8 dígitos (antes 6-9). |
| **Frontend (views/JS)** | No hay cambios de endpoints ni de claves JSON; solo cambian los **textos** de los mensajes de error, que se muestran tal cual. |

---

## 4. Decisiones de negocio aplicadas (defaults acordados)

1. **Cédula de delivery** (`personal_delivery.py`, `entrega.py`): se mantiene 6-15 dígitos
   (permite cédulas/pasaportes extranjeros). Documentada como regla consciente.
2. **RIF en órdenes de servicio y clientes jurídicos**: solo J/E (`tipos="JE"`); no se habilitó V.
3. **Teléfono de clientes**: 11 dígitos genéricos (`validar_numero`; antes `validar_celular`,
   eliminado en la Remediación 3), no exige prefijo móvil
   venezolano (podría ser un teléfono de línea); los empleados/proveedores sí usan la regla de
   prefijos móviles (`validar_celular_venezolano`).
4. **Cédula de usuarios/empleados**: 6-8 dígitos con `validar_numero` (se eliminó la función muerta
   que duplicaba la regla con `strip` de guiones).

## 5. Cómo verificar

```bash
docker-compose up --build          # entorno de desarrollo
.venv/bin/python -m pytest "tests/pruebas unitarias" -q   # 2385 passed
bandit -r . --exclude ./.venv      # escaneo de seguridad
```
Para las pruebas de integración (BD reales): levantar `docker-compose.test.yml` según AGENTS.md.

## 6. Pendientes recomendados (no aplicados)

- Extraer las validaciones de fecha (`reportes_ventas.py`) y de cédulas de `clientes.py`
  (`isdigit`/`len` con mensajes propios) si se quiere uniformidad total de mensajes.
- Añadir validación del dígito verificador del RIF (módulo 11) si el negocio lo requiere.
- Cobertura de `field-validator.js` (cliente) alineando sus reglas con los mensajes nuevos si el
  front hace validaciones espejo.
- Si algún módulo necesita en el futuro un conjunto de caracteres nuevo, NO crear otro validador:
  usar `validar_texto_numero(..., caracteres_extra="...")`.
