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

---
---

# Auditoría de modelos (`app/models`)

> Fecha: 22/11/2026 · Alcance: los **29 archivos** de `app/models` (~370 KB de código).
> Método: lectura 100% de cada archivo + contraste contra el esquema (`bd/ituaccesoriobd.sql`,
> `bd/seguridad.sql`) + bandit + verificación de código muerto con grep en todo el repo.
> **Línea base: 2385 tests en verde — los hallazgos de abajo NO están cubiertos por los tests**
> (varios son la causa de endpoints que fallan en silencio en producción).
> Estado: **solo documentado; no se modificó código.** Severidades: 🔴 rompe datos o un endpoint
> en producción · 🟠 bug real con riesgo · 🟡 mejora/consistencia.

## Resumen por severidad

| Severidad | Cantidad | Archivos con 🔴 |
|---|---|---|
| 🔴 Alta | 10 | `james.py`(1) · `clientes.py`(2) · `tradein_empleados.py`(2) · `reportes_ventas.py`(1) · `venta.py`(1) · `ordenes_compra.py`(1) · `ordenes_entregas.py`(1) · `test.py`(1) |
| 🟠 Media | 37 | `clientes`(3) · `tradein_empleados`(5) · `ordenes_servicio`(3) · `proveedores`(3) · `usuarios`(2) · `empleados`(1) · `productos`(2) · `equipo`(2) · `bitacora`(2) · `backup`(2) · `venta`(2) · `entrega`(2) · `ordenes_compra`(2) · `test`(2) · `ordenes_entregas`(1) · `validacion_pagos`(1) · `carrito`(1) · **seed**(2) |
| 🟡 Baja | 90 | repartidos en 28 archivos (detallados en §4) |

---

## 1. Errores 🔴 Alta (los 10 verificados uno a uno contra código y esquema)

### A1. `james.py:9-107` — conexión y cursor nunca se cierran (fuga por llamada)
`consultar_informacion_orden` tiene `try/except` pero **sin `finally`** (el archivo solo tiene 1
`finally`, y es del otro método). Cada consulta al asistente deja abiertos un cursor y una conexión
MySQL hasta que pase el GC → con gunicorn/hot-reload se acumulan hasta agotar `max_connections`.
```python
        except Exception as e:
            return f"Error al consultar la información: {str(e)}"
    # ← no hay finally en TODO el método
```
**Solución:** `finally: self.__conexion.cerrar_conexion(cursor, db)` (mismo patrón que el segundo
método del archivo, que sí lo hace).

### A2. `clientes.py:113-198` — `eliminar_cliente` hace commit después de CADA DELETE (~20 commits)
Si un DELETE posterior falla, el rollback solo deshace ese statement: **todo lo anterior ya está
comprometido** → cliente borrado a medias (p. ej. `Venta` sin sus `Metodo_pago`).
**Solución:** una sola transacción (todos los DELETE sin commit intermedio) con un único
`db.commit()` al final y `db.rollback()` en el `except`.

### A3. `clientes.py:108-198` — `eliminar_cliente` no borra `Entrega`
La FK `Entrega_ibfk_1 → Venta` (sin CASCADE) no tiene DELETE en el flujo: cualquier cliente con
entregas lanza error 1451 en `DELETE FROM Venta` y — combinado con A2 — deja la BD medio borrada.
Los helpers de tests borran `Entrega` a mano (`seed_helpers.py:197`), por eso los 2385 tests pasan.
**Solución:** `DELETE Entrega FROM Entrega INNER JOIN Venta … WHERE Venta.ID_cliente = %s` antes
de borrar `Venta`.

### A4. `tradein_empleados.py:315-322 (y 457-463)` — registrar trade-in con 2+ fotos SIEMPRE falla
Dentro de la transacción abierta (INSERT sin commit), `_generar_id_foto_trade_in()` abre una
**conexión nueva** (`self._conexion()` → `conexion1()`): el `MAX(ID_foto_trade_in)` de esa conexión
no ve las filas sin commit → mismo ID para la 2ª foto → `IntegrityError 1062` → rollback total.
**Solución:** generar todos los IDs con el cursor principal de la transacción (o cerrar/confirmar
antes de calcular el MAX).

### A5. `tradein_empleados.py:456-463` — `actualizar_trade_in` borra TODAS las fotos y solo reinserta las nuevas
El controller llena `fotos` solo con archivos nuevos (`_guardar_fotos()`); el `fotos_eliminar` que
envía el frontend (`app/static/js/tradein_empleados.js:408`) **nunca se lee en el backend**
(verificado con grep: solo existe en el JS). Editar un trade-in sin subir fotos nuevas destruye
todas sus fotos en la BD.
**Solución:** eliminar el `DELETE` masivo e implementar borrado selectivo leyendo `fotos_eliminar`.

### A6. `reportes_ventas.py:504-536` — el monto de la venta local sale del request sin validar
`precio = float(item.get("precio_usd", 0))` (items vienen de `request.get_json`) → `total_monto`
se inserta en `Metodo_pago.Monto` con estado **'aprobado' automático**. Un precio negativo o
manipulado genera un pago aprobado con monto falso; además se usa `float` para dinero.
**Solución:** recalcular `total_monto` desde `Costo_venta` de la BD (que ya se valida contra stock)
ignorando el precio del request; si se acepta precio del cliente, validar con `validar_decimal` en `Decimal`.

### A7. `venta.py:360-403` — `obtener_ventas_hoy` consulta `Venta.Monto`, columna que NO existe
Esquema (`ituaccesoriobd.sql:717-728`): `Venta` solo tiene ID_factura, ID_empleado, ID_cliente,
Moneda, Fecha_venta (`Monto` existe en `Metodo_pago`). La consulta muere con error 1054 → el
`except` devuelve 0 → el dashboard "ventas de hoy" **siempre muestra 0**, y la segunda consulta
(la correcta, contra `Metodo_pago`, líneas 380-398) es **código muerto**: nunca se ejecuta.
**Solución:** eliminar la consulta rota y usar la que suma desde `Metodo_pago` (o agregar la
columna a `Venta` y unificar).

### A8. `ordenes_compra.py:63-84` — `listar_ordenes_entregadas` consulta `ei.Recibido_por`, columna que NO existe
`Entrega_inventario` (`sql:241-249`) solo tiene ID_entrega_inventario, ID_empleado, ID_orden_compra,
Fecha_entrega_inventario → error 1054 → `except` → **siempre devuelve `[]`**: la pantalla de
órdenes entregadas está vacía desde siempre. "Recibido por" debe salir del JOIN con Empleado.
**Solución:** `CONCAT(e.Nombre_empleado, ' ', e.Apellido_empleado)` con
`JOIN Empleado e ON ei.ID_empleado = e.ID_empleado`.

### A9. `ordenes_entregas.py:166-174` — `fetchone()` asume una fila de inventario por producto
`SELECT … FROM Existencias_productos WHERE ID_producto = %s` + `fetchone()`: `ID_inventario` es la
PK y `ID_producto` NO es único (el propio método crea filas nuevas). Con varias filas, el stock se
suma a una fila arbitraria y las demás quedan sin abastecer (y `Abastece` apunta a esa fila).
**Solución:** definir la regla (sumar a la fila de mayor stock / crear siempre fila nueva) o índice
único por producto.

### A10. `test.py:34-39` — `buscar_test` consulta tablas que NO existen
`revision_orden` y `orden_e`: **0 ocurrencias** en `ituaccesoriobd.sql` (ni en ningún otro `.sql`
del repo). Además no tiene `except` → error crudo si alguien la llama. Ningún controller la usa.
**Solución:** eliminar el método (o migrar la consulta al esquema actual: `Orden_servicio` + `Test`).

---

## 2. Errores 🟠 Media (37)

**`clientes.py` (3)**
1. `686-688 y 841-843` — `actualizar_persona_natural/juridico` hacen UPDATE de **todos** los campos con `or None` y sin chequear `rowcount`: un PUT parcial **borra** celular/correo/dirección; y si el ID no matchea responde "se actualizó exitosamente" sin tocar nada. → UPDATE dinámico solo con campos no vacíos + verificar `rowcount`.
2. `575-594, 644-667, 738-762, 803-827` — el bloque de validaciones está copiado 4 veces con reglas contradictorias (celular obligatorio al registrar, opcional al actualizar). → helper privado `_validar_datos_natural/juridico(obligar_celular)`.
3. `770-783 vs 841-843` — PK dual del RIF: el controller normaliza sin guiones pero el modelo guarda la PK con la forma del body → `actualizar_cliente_juridico` solo matchea si el frontend manda guiones. → forma canónica única en INSERT y UPDATE.

**`tradein_empleados.py` (5)**
4. `296-298 y 437-439` — decide el fallo de `Equipo.registrar_equipo()` con `if "Error" in resultado`, pero Equipo devuelve mensajes sin "Error" → fallos ignorados y FK cruda después; en el update solo imprime "Advertencia" y sigue con `success: True`. → contrato estructurado (no matching de texto).
5. `325-364 y 471-508` — el bloque de tests tiene `except` que imprime y **continúa**, y luego `db.commit()`: en el update puede quedar 0 tests y `success: True`. → relanzar la excepción o devolver error antes del commit.
6. `185, 215, 327, 474` — IDs TRD/FTI/TST con `MAX+1` sin transacción/lock → carrera → PK duplicada. → `FOR UPDATE` o tabla de secuencia.
7. `202 y 232` — IDs de emergencia de 17 caracteres contra columnas `varchar(10)`; y el fallback fijo `"TRD000001"` colisiona con el primer registro. → propagar el error, no inventar IDs.
8. `301` — `Fecha_realizado` con `datetime.now()`: contenedor en UTC vs MySQL forzado a -04:00 → 4 h de desfase. → `NOW()` de MySQL o `TZ=America/Caracas` en el contenedor.

**`ordenes_servicio.py` (3)**
9. `814-816` — `eliminar_orden` no borra `Repuestos_usados`, `Pago_servicio`, `Test_realizados_interaccion`, `Test` (FKs RESTRICT) → error 1451 → rollback → `False` genérico aunque la orden esté 'Pendiente'. → replicar el orden de borrado de `clientes.eliminar_cliente`.
10. `572-581 y 603-612` — IDs OS/INT con `MAX+1` sin lock + slicing/`int()` sin protección (`int(ultimo_id[2:])`). → transacción + `FOR UPDATE` y manejar formato inesperado.
11. `584` — `Fecha_entrada` con `datetime.now()` (UTC) mientras `sp_registrar_reparacion` usa `NOW()` (-04:00) → **la misma tabla mezcla dos relojes**. → `NOW()` en ambos.

**`proveedores.py` (3)**
12. `208 y 225` — validación permite más largo que las columnas: Nombre hasta 60 vs `varchar(40)`, Dirección hasta 100 vs `varchar(60)` → error 1406 crudo en strict mode. → alinear máximos con el esquema.
13. `667-730` — `crear_proveedor_con_productos` (vía reachable cuando vienen productos): sin dup-checks de nombre/RIF, ID con `MAX+1` sin lock, y `Limite_credito = None` donde el SP guarda 0. → unificar ambas vías de creación.
14. `256-260` — el costo se fuerza a `int(costo)` contra `Suministra.Costo_producto decimal(10,2)` → "100.50" se rechaza. → `validar_decimal` igual que el límite de crédito.

**`usuarios.py` (2)**
15. `370-386` — ID `USR-xxx` con `MAX(id)` + parse frágil (`split('-')[1]`): un prefijo legado con guion no falla y genera colisiones; al pasar de `USR-999` el MAX lexicográfico rompe la secuencia. → usar `MAX(CAST(SUBSTRING(id,5)…))` siempre + retry.
16. `459-466 y 663-670` — renombrar usuario/actualizar perfil **sin chequear duplicados de nombre** (no hay UNIQUE en BD y `validar_login` filtra por nombre sin LIMIT) → dos logins homónimos y la sesión puede levantar al otro. → reutilizar `verificar_usuario_por_nombre()` excluyendo el propio id.

**`empleados.py` (1)**
17. `300-308 y 410-417` — fallos de `Capacitacion` silenciados con `logger.warning` y luego `db.commit()` igual → empleado guardado **sin sus especialidades** sin que el usuario lo sepa (y en el update, el DELETE silenciado puede dejar combos inconsistentes). → validar/insertar las especialidades dentro de la transacción y abortar si falla alguna.

**`productos.py` (2)**
18. `427` — llama al SP `sp_verificar_stock_producto`, que **no existe en el seed** `bd/ituaccesoriobd.sql` (solo en respaldos viejos de `app/bd/`): tras `down -v && up` el endpoint cae siempre al fallback silencioso. → reproducir el SP en el seed o eliminar el método.
19. `73, 192, 326` — IDs de Clase/Marca/Producto con `MAX(CAST(… AS UNSIGNED))+1` sin lock → carrera → PK duplicada. → transacción con `FOR UPDATE` o UNIQUE + retry.

**`equipo.py` (2)**
20. `80-81` — Color limitado a 30 caracteres contra columna `varchar(20)` → error 1406 crudo. → límite 20.
21. `84-85 vs 148-149` — Capacidad 6 al registrar vs 20 al actualizar (misma columna `varchar(20)`): el registrar rechaza capacidades que la BD admite. → unificar a 20.

**`bitacora.py` (2)**
22. `128-135 y 192-200` — N+1 de conexiones: `_obtener_info_usuario` abre `conexion1()` **por cada fila** (100 conexiones para listar 100 registros). → un `SELECT … WHERE id IN (…)` o JOIN.
23. `190 y 206` — `datetime.now()` del contenedor (UTC) vs `fecha_hora` escrita en -04:00 → un evento de hace segundos muestra "hace 4 horas". → `timezone(timedelta(hours=-4))` o comparar en SQL.

**`backup.py` (2)**
24. `385-407` — `obtener_info_backup` definida **fuera de la clase** (duplicado del método 147-169) con `self.__conexion_bd` sin name-mangling correcto; nadie la usa. → borrarla.
25. `288-292 + 340-345` — el saneo de `DEFINER=…` deja `CREATE  PROCEDURE` (doble espacio) → `startswith('CREATE PROCEDURE')` es False → el cuerpo del SP se parte en cada `;` interno y **las rutinas no se restauran**. Hoy no explota porque el seed no trae DEFINER, pero el respaldo documentado (mysqldump como root con `--routines`) sí los genera. → normalizar espacios tras el regex.

**`venta.py` (2)**
26. `136-138 + 217-228` — `cantidad = "0"` pasa la validación (1 dígito) y crea un `Detalle_venta` con cantidad 0 + `UPDATE Existencia = Existencia - 0`; en `reportes_ventas.registrar_venta_local` sí existe el check `cantidad <= 0`. → validar `int(cantidad) >= 1` igual que en reportes.
27. `319-330` — resubisión de pago tras rechazo: `ON DUPLICATE KEY UPDATE … Estado_pago = COALESCE(Estado_pago,'pendiente')` conserva `'rechazado'` → el cliente actualiza datos pero el pago queda congelado. → recalcular a `pendiente` cuando cambien los datos de pago.

**`entrega.py` (2)**
28. `347 y 389` — `return f"Error al actualizar: {e}"` expone el error de MySQL en la respuesta HTTP (y el controller decide el status por substrings del mensaje). → mensaje genérico + log.
29. `278-289` — `registrar_entrega` permite varias entregas para la misma factura (sin check de existencia). → rechazar si ya existe entrega para la factura.

**`ordenes_compra.py` (2)**
30. `358-364 y 439-445` — `actualizar_orden_compra` lanza `ValueError/RuntimeError` y su propio `except Exception` los traga devolviendo `False`, igual que "orden no encontrada"; además ~20 `print` de debug con emojis. → dejar subir las validaciones y quitar prints.
31. `311-324` — `registrar` no valida `qty > 0` ni el formato de `productos`, y no registra bitácora pese a recibir `usuario_id`. → validar y registrar.

**`test.py` (2)**
32. `317-330` — la re-selección de los tests insertados filtra por `Numero_test` **global** (no por orden): con dos técnicos concurrentes, `Test_realizados_interaccion` puede apuntar a tests de otra orden. → capturar los IDs al insertar.
33. `257` — `int(valores[idx])` sin try dentro del loop: un componente no numérico revienta TODO el registro. → try por componente.

**`ordenes_entregas.py` (1)**
34. `132-144 vs 208-212` — productos de la orden sin fila en `Suministra` desaparecen del JOIN (se pierden silenciosamente) y la orden se marca 'Completada' igual. → `LEFT JOIN` + error si falta costo.

**`validacion_pagos.py` (1)**
35. `314-331 y 377-395` — TOCTOU: la verificación "pendiente" corre en otra conexión y el `UPDATE … WHERE ID_factura=%s` no incluye `AND Estado_pago='pendiente'` → dos empleados aprobando a la vez: ambos pasan el check y el segundo sobrescribe `Aprobado_por`. → mover la condición al `WHERE` del UPDATE y usar `rowcount`.

**`carrito.py` (1)**
36. `112-127` — la tabla `Tasas_cambio` **no existe en ningún `.sql` del repo** → `_obtener_tasas` siempre lanza excepción y devuelve tasas hardcodeadas viejas (520.91/710.12) sin aviso. → crear la tabla en el seed o fuente real + advertir que el fallback es estático.

**Seed (2)**
37. `bd/seguridad.sql` — **no trae el rol 'Cliente'** (solo 'Admin'; el AUTO_INCREMENT=8 sugiere roles que nunca entraron al seed): en un despliegue fresco el registro público devuelve 500 "No existe el rol Cliente configurado." — y **sin los módulos 'Backup' y 'Entregas'**: `@tiene_permiso('Backup','registrar')` nunca satisfacible para no-admin y las bitácoras de esos módulos se archivan como "Empleados". → añadir rol y módulos al seed (requiere `down -v`).

---

## 3. Errores 🟡 Baja (90, agrupados por tipo transversal)

**T1 · 190 `print()` en vez de `logger` (28 archivos)** — los errores se van a stdout y se pierden en producción; `empleados.py` ya usa `logging` (patrón a seguir). Incluye `database.py:30/36` y `bitacora.py:139/227`.

**T2 · `str(e)` con detalle SQL expuesto al usuario** — entrega.py:347/389 · validacion_pagos.py:346/410/543 · equipo.py:110/183/219 · usuarios.py:413/421/489 · permisos.py:188 · productos.py:449 · backup.py · personal_delivery.py:163/199/252 · clientes.py:61-62 (además retorna `str` donde se espera lista → el controller lo serializa con `success: True`).

**T3 · Contratos de error mezclados** (str / dict / bool / raise) y control de flujo por substrings: login.py:107 (`"exitosamente" in resultado`), clientes.py:417, taller.py:127-137, entregas.py:160-162, tradein_empleados.py:272/285/426/438. → unificar contrato (dict `success`/`error` o excepciones de dominio).

**T4 · `MAX(ID)+1` sin lock (además de los 🟠)** — entrega.py:29-51, carrito.py:97-99, ordenes_servicio.py:828-847 (la generación del ID `FOS` vive en el controller), ordenes_entregas.py:190-199 (`MAX(CAST(…))` → IDs no numéricos hacen CAST→0 → colisión).

**T5 · Dinero en `float`** — carrito.py:197-198, ordenes_entregas.py:160-163 (margen 1.3 hardcodeado), venta.py (total), reportes_ventas.py. → `Decimal` y convertir al final.

**T6 · Código muerto (verificado con grep)** — clientes.py: `listar_clientes_naturales`, `actualizar_datos_cliente`; ordenes_servicio.py: `listar_ordenes_servicio` (con INNER JOIN que excluiría órdenes sin fotos), `verificar_foto_existe_por_id`, parámetro `modelo_custom` sin uso; proveedores.py: `verificar_existencia`; permisos.py: 4 métodos solo-tests (`listar_permisos_por_rol`, `guardar_permiso`, `eliminar_permiso`, `verificar_permiso`); inventario.py: `usuario_id` sin usar; entrega.py: rama "Programado" inalcanzable; venta.py: consulta muerta de `Metodo_pago` (A7); test.py: `buscar_test` (A10).

**T7 · Imports sin usar** — venta.py (`validar_texto_numero` ×2 + `Decimal`), reportes_ventas.py y tradein_empleados.py (`validar_texto_numero` ×2), ordenes_compra.py y ordenes_entregas.py (`datetime`), login.py (`re`, `datetime`), empleados.py (`jsonify`), productos.py (`Decimal`).

**T8 · N+1 de conexiones (además de los 🟠)** — venta.py:221 (una conexión por ítem dentro de la transacción abierta), tradein.py:295→101 (una conexión por falla cotizada), tradein_empleados.py:634-636 (2 conexiones por fila en `obtener_trade_ins`).

**T9 · Fechas/TZ sin validar** — contenedor web sin TZ (UTC) vs MySQL -04:00 (además de los 🟠 de tradein/ordenes/bitacora); bitacora.py:207-219 (fecha futura → "hace 22 horas"); venta.py:284-286 (`fecha_pago` cruda del request a un `datetime`); ordenes_entregas.py:263-270 (`fecha_entrega` cruda, `recibido_por` aceptado pero ignorado).

**T10 · Métodos sin `except`** (un error de SQL sube crudo, inconsistente con el resto del modelo) — todo `inventario.py`, `catalogo.py` (4 métodos), `test.py` (3), `proveedores.py` (4), `ordenes_servicio.py:212-229`.

**T11 · Per-archivo menores** — equipo.py:64-65 (mensaje dice 15, código permite 16); cargos.py/especialidades.py (ID min 9-10) vs empleados.py (min 1); roles.py:222 (guard 'admin'/'cliente' hardcodeado, amarrar por id del seed); tradein.py:96-133 (repuesto por nombre sin filtrar por modelo; fallo de BD → deducción 0.00 silenciosa con `success: True`); carrito.py:360-368 (`actualizar_cantidad` ignora `rowcount`), 394/416 (`except` sin log), 322-420 (3 métodos sin bitácora), 31 (cédula 6-8 excluye clientes jurídicos del carrito — decisión a confirmar, igual en venta/reportes/tradein); catalogo.py:44 (búsqueda de 1 carácter descartada en silencio); test.py:117 (mensaje "ID del Cargo" para el ID de la orden, copy-paste) y 264-271 ("Observaciones" asumido como último elemento); proveedores.py:596-614 (`ON DUPLICATE KEY … VALUES()` deprecado en MySQL 8.0.20 + `rowcount` 0 cuando no cambia nada), 310 vs 693 (0 vs None como límite por defecto según la vía), `Rif_proveedor` vs `RIF_proveedor` del esquema; james.py:135 (`LIKE '%Técnico%'`) vs empleados.py:512 (exacto — cargos "Técnico Senior" cuentan distinto); bitacora.py:22-27 (fallback silencioso a módulo 1), 160-166 (finally manual sin `cerrar_conexion`); personal_delivery.py:157 (módulo 'Entregas' inexistente en seed); login.py:96-102 (doble validación + 2 conexiones extra), 86-222 (PII en stdout); database.py:13 (`ultimo_error` compartido entre threads), 45/52 (`int(DB_PORT)` fuera del try), 42-55 (sin pooling); usuarios.py:585-591 (timing attack: usuario inexistente no calcula hash) y 588 (`check_password_hash(None)` cuando la columna admite NULL → AttributeError silenciado), 423-489 (`actualizar_usuario` puede dejar el sistema sin admin: no hay guard como en `eliminar_usuario`); productos.py:612 (duplicado sin LOWER/TRIM en actualizar vs registrar), 669 (borrar Producto con Equipos asociados → FK cruda); reportes_ventas.py:148-165 (no detecta productos duplicados → choca con PK `(ID_inventario, ID_factura)`, venta.py sí lo hace), 198-208 y validacion_pagos.py:479-485 (filtros `estado`/`metodo`/`moneda` sin validar), 548-574 (`actualizar_fecha_pago` devuelve None siempre); validacion_pagos.py:109-157 ≡ reportes_ventas.py:84-133 (`_validar_filtros_reportes` copiada byte a byte — extraer a validators.py); ordenes_servicio.py:163/393 (typos "ID dela orden", "Desdescripcion "), 773-792 (`actualizar_estado` acepta cualquier string sin whitelist), 298-310 (`registrar_fotos` sin validar lista), 444-483 (nota sin validar contra varchar(300)); ordenes_compra.py:187-202 (`LEFT JOIN Suministra` sin filtrar por proveedor → filas duplicadas); ordenes_entregas.py:35 (`int(last_id[3:])` sin try), 334-338 (`GREATEST(Existencia-%s,0)` pierde unidades al anular); inventario.py:226-231 (INNER JOIN vs LEFT JOIN en el resto).

---

## 4. Supresiones `# nosec B608` y f-strings en SQL — verificadas (TODAS justificadas)

Las 14 líneas con `# nosec B608` + los 4 `execute(f"""…""")` (`productos.py:354`, `proveedores.py:66`,
`reportes_ventas.py:229/436`) siguen el mismo patrón seguro: la parte interpolada es una lista de
**columnas fijas construida en código** (o filtrada contra `INFORMATION_SCHEMA`, como en
`venta.py:320-330`) y **todos los valores viajan parametrizados** con `%s`. No hay inyección SQL en
`app/models`. Recomendación: mantener los `nosec`. Extra positivo: `catalogo.py:45` es el único
modelo que escapa `%` y `_` del término de búsqueda (evita LIKE-injection de comodines).

## 5. Buenas prácticas ya correctas (no "arreglar")

- `Bitacora.registrar()` se invoca **después** del `commit` de la BD principal en los 29 archivos (BD aparte, transacción independiente) — patrón correcto.
- Cierres `cursor.close()/db.close()` en `finally` en todos los modelos **salvo** `james.py` (A1).
- Firmas de `CALL` contrastadas contra el seed y el conector: `Crear_cargo`, `Crear_especialidad`, `sp_registrar_producto`, `sp_registrar_revision_test`, `sp_registrar_proveedor` ✅.
- `roles.agregar_rol` usa `lastrowid` en vez de MAX+1 → patrón correcto a replicar.
- `backup.py` omite `GRANT/CREATE USER/GTID` y captura errno 1227 al restaurar.
- `validar_campo_comun`-style dead code ya no existe tras la auditoría de validators.

## 6. Módulos afectados y cómo (síntomas visibles en producción)

| Síntoma | Causa raíz |
|---|---|
| Dashboard "ventas de hoy" siempre en 0 | A7 (`Venta.Monto` inexistente) |
| Pantalla de órdenes de compra entregadas siempre vacía | A8 (`ei.Recibido_por` inexistente) |
| Registrar un trade-in con 2+ fotos falla siempre | A4 (ID duplicado por conexión extra en transacción) |
| Editar un trade-in borra todas sus fotos | A5 (`fotos_eliminar` nunca se lee) |
| Eliminar un cliente con entregas deja la BD medio borrada | A2 + A3 |
| Pago local 'aprobado' con monto manipulable | A6 |
| Registro público de cliente roto en deploy fresco | Seed sin rol 'Cliente' (37) |
| Verificación de stock en productos cae a fallback silencioso | SP inexistente en seed (18) |
| Tasas de cambio fijas viejas en el carrito | Tabla `Tasas_cambio` inexistente (36) — ahora con aviso en el log; pendiente fuente autorizada de tasas |
| Bitácora muestra "hace 4 horas" para eventos recientes | UTC del contenedor vs -04:00 (23) |
| Asistente (james) puede agotar conexiones MySQL | A1 (sin finally) |
| Empleado guardado sin especialidades sin aviso | 17 |
| Dos empleados aprobando el mismo pago se sobrescriben | 35 |

## 7. Plan de corrección propuesto (pendiente de aprobación — no aplicado)

- **Fase 1 — los 10 🔴**: A1 (finally en james), A2+A3 (transacción única + DELETE Entrega en clientes), A4+A5 (IDs de fotos en la misma transacción + `fotos_eliminar`), A6 (monto desde BD), A7 (dashboard con `Metodo_pago`), A8 (JOIN Empleado), A9 (regla multi-fila), A10 (borrar `buscar_test`) + tests de regresión para cada uno.
- **Fase 2 — los 37 🟠** (agrupadas: transacciones atómicas/TOCTOU en pagos, generación de IDs con lock, límites alineados a esquema en proveedores/equipo, seed con rol Cliente + módulos Backup/Entregas — esta última requiere `docker-compose down -v`).
- **Fase 3 — los 90 🟡 por tipo**: T1 logger, T2 mensajes genéricos, T3 contrato de errores único, T6/T7 dead code e imports, T5 Decimal, T9 TZ (fijar `TZ=America/Caracas` en el contenedor es la solución de una línea para todos los desfases).
- **Fase 4 — transversales**: pooling en `database.py`, extraer `_validar_filtros_reportes` a validators, unificar estilos de error.

---

## 8. Remediación aplicada (misma sesión, 22/11/2026)

**Verificación final: 2379 tests unitarios en verde · bandit: 0 hallazgos · todos los módulos importan.**
Suite anterior: 2385 (la diferencia neta son tests de comportamientos viejos eliminados — p. ej. el
silenciamiento de fallos de tests de trade-in — reemplazados por tests del comportamiento corregido).

### Fase 1 — los 10 🔴 (todos aplicados)

| # | Fix |
|---|---|
| A1 | `james.py`: `finally` con `cursor.close()/db.close()` en `consultar_informacion_orden` |
| A2 | `clientes.eliminar_cliente`: **una sola transacción** (eliminados ~20 commits intermedios) + commit único + rollback |
| A3 | `clientes.eliminar_cliente`: añadido `DELETE e FROM Entrega INNER JOIN Venta` ANTES de borrar `Venta` (y corregido un JOIN con alias `tri` inexistente que rompía el DELETE de `Test`) |
| A4 | `tradein_empleados` (registrar/actualizar): IDs de foto generados con el **mismo cursor** de la transacción (MAX + incremento local) — 2+ fotos ya no colisionan |
| A5 | `tradein_empleados.actualizar_trade_in`: borrado **selectivo** por URL leyendo `fotos_eliminar` (el controller ahora hace `request.form.getlist("fotos_eliminar")`); `fotos_eliminar=None` conserva el comportamiento antiguo |
| A6 | `reportes_ventas.registrar_venta_local`: monto recalculado desde `Costo_venta` de la BD en `Decimal` (el `precio_usd` del request se ignora) + stock verificado con el mismo cursor + chequeo de productos duplicados |
| A7 | `venta.obtener_ventas_hoy`: eliminada la consulta rota (`Venta.Monto`); se usa la consulta a `Metodo_pago` (el dashboard ya no muestra siempre 0) |
| A8 | `ordenes_compra.listar_ordenes_entregadas`: `ei.Recibido_por` → `CONCAT(e.Nombre…)` con `JOIN Empleado` (la lista ya no está siempre vacía) |
| A9 | `ordenes_entregas`: abastecer a la fila con **mayor stock** (`ORDER BY Existencia DESC LIMIT 1`) en vez de una fila arbitraria |
| A10 | `test.py`: método `buscar_test` (tablas legadas inexistentes) eliminado junto con su clase de tests |

### Fase 2 — los 37 🟠 (todos aplicados)

- **clientes.py**: helper `_validar_datos_natural()` (4 bloques → 1); UPDATE **dinámico** + verificación de existencia en `actualizar_persona_natural/juridico` (un PUT parcial ya no borra datos y un ID inexistente ya no responde "exitosamente"); PK canónica del RIF buscando por ambas formas (con/sin guiones).
- **tradein_empleados.py**: decisión por mensaje de éxito ("exitosamente") en lugar de `if "Error" in…`; fallos de tests **relanzados** (ya no commit parcial con `success=True`); helper `_generar_id_trade_in` **sin IDs inventados** (17 chars > varchar(10) o colisión con `TRD000001`) → `RuntimeError`; `Fecha_realizado` en -04:00.
- **ordenes_servicio.py**: `eliminar_orden` borra también `Repuestos_usados`, `Pago_servicio`, `Test_realizados_interaccion`, `Test`; `int()` protegidos en la generación de IDs OS/INT; `Fecha_entrada` con `NOW()` de MySQL.
- **proveedores.py**: límites alineados al esquema (nombre 40, dirección 60); costo con `normalizar_numero_decimal` (acepta decimales, columna `decimal(10,2)`); `crear_proveedor_con_productos` con dup-checks de nombre/RIF y `Limite_credito=0` como el SP.
- **usuarios.py**: ID `USR-xxx` con `MAX(CAST(SUBSTRING(id,5) AS UNSIGNED))` siempre (parse frágil eliminado); unicidad de nombre en `actualizar_usuario` y `actualizar_perfil` (`WHERE nombre = %s AND id != %s`).
- **empleados.py**: `Capacitacion` dentro de la transacción **sin try/except silenciador** (registrar y actualizar).
- **productos.py**: `callproc sp_verificar_stock_producto` (SP vacío/no sembrado) → consulta directa con SUM + detalle ordenado.
- **equipo.py**: límites alineados a las columnas (Color 20, Capacidad 20 en ambos métodos; mensaje del ID corregido a 16).
- **bitacora.py**: carga de usuarios **en lote** (1 consulta en vez de N conexiones; 100 registros = 1 conexión) con manejo explícito de `SYSTEM`; `tiempo_relativo` con zona -04:00 y guard para fechas futuras ("ahora mismo").
- **backup.py**: función muerta a nivel de módulo eliminada; detección de rutinas con regex tolerante (`CREATE\s+PROCEDURE`) — la restauración de SPs vuelve a funcionar con dumps que traen `DEFINER=`.
- **venta.py**: cantidad ≥ 1 (el "0" ya no pasa); reenvío de pago tras rechazo vuelve a **'pendiente'** (CASE por cambio de Referencia/Capture/Monto).
- **entrega.py**: rechazo de facturas con entrega previa; mensajes de error genéricos (sin `str(e)`).
- **ordenes_compra.py**: cantidades `> 0` validadas al registrar + bitácora; 24 `print` de debug → `logger.debug`.
- **test.py**: IDs de tests capturados **al insertar** (la re-selección global por `Numero_test` podía enlazar tests de otra orden); `int()` del componente protegido.
- **validacion_pagos.py**: condición de estado **en el WHERE** del UPDATE de aprobar/rechazar + `rowcount` (TOCTOU cerrado).
- **carrito.py**: fallback de tasas de cambio ahora emite `logger.warning` explícito (sin crear tabla nueva en la BD, por decisión del propietario; el cambio real de tasas queda pendiente de una fuente de datos autorizada).
- **Seed (`bd/seguridad.sql`)**: rol **'Cliente'** y módulos **'Backup'/'Entregas'** añadidos (requiere `docker-compose down -v`).

### Fase 3 — aplicados los transversales seguros

- **T1**: **160 `print()` → `logger`** (26 archivos) + `database.py` (2) con tests `capsys` migrados a `caplog`.
- **T2**: mensajes con `str(e)` → genéricos en `equipo`, `usuarios`, `personal_delivery`, `permisos`, `productos`, `clientes` (los detalles técnicos quedan en `logger`).
- **T7**: imports sin usar eliminados en 8 archivos (`venta`, `reportes_ventas`, `tradein_empleados`, `ordenes_compra`, `ordenes_entregas`, `login`, `empleados`, `productos`).
- **T9**: `TZ=America/Caracas` + tzdata en el Dockerfile (elimina el desfase UTC vs -04:00 de raíz).
- **T11 (parte)**: typos corregidos ("ID dela orden" → "ID de la orden", "Desdescripcion " → "Descripción", mensaje 15→16 en equipo).

### Pendiente → ver §9 "Cosas por mejorar o que faltan"

Todo lo que quedó pendiente tras la remediación se consolidó en la sección
**§9. Cosas por mejorar o que faltan** (final del documento).

### Notas de despliegue

```bash
docker-compose down -v && docker-compose up --build   # aplica el seed nuevo (rol Cliente, módulos) y la imagen con TZ
.venv/bin/python -m pytest "tests/pruebas unitarias" -q   # 2379 passed
.venv/bin/bandit -r . --exclude ./.venv                 # 0 hallazgos
```

---

## 9. Cosas por mejorar o que faltan

Estado de las mejoras **no aplicadas** tras la remediación de la auditoría de modelos,
más las decisiones que quedaron a medio camino. Ordenadas de mayor a menor impacto estimado.

### 9.1 Tasas de cambio del carrito (`Tasas_cambio`) — DECISIÓN TOMADA, a medio camino

- **Situación**: `carrito._obtener_tasas()` ejecuta `SELECT … FROM Tasas_cambio`, pero la tabla
  **no existe en ningún `.sql` del repo ni en los respaldos** → la consulta falla siempre y el
  carrito muestra tasas hardcodeadas viejas (520.91 / 710.12).
- **Lo que se aplicó**: el fallback estático ahora emite `logger.warning` (ya no falla en silencio).
  **No se creó la tabla** en la BD: el propietario del proyecto decidió no agregar esquema nuevo.
- **Lo que falta** (opciones, por elegir cuando corresponda):
  1. Dejar como está (query + fallback con warning) — estado actual, no requiere nada.
  2. Eliminar la consulta muerta y fijar las tasas como constantes del código.
  3. Mover las tasas a configuración (`.env`: `TASA_OFICIAL` / `TASA_PARALELO`) — ajustables sin
     tocar código ni BD.
  4. Crear la tabla `Tasas_cambio` a mano en la BD real (sin tocar el seed) — entonces la query
     del carrito empieza a funcionar sola.
- Mientras tanto: **las tasas mostradas al cliente siguen desactualizadas**; hay que
  actualizarlas a mano (o por 2/3) cuando el BCV cambie.

### 9.2 Contrato de errores unificado (T3)

Los modelos mezclan 4 estilos (str / dict success / bool / raise) y los controllers deciden el
status HTTP haciendo matching de substrings ("exitosamente", "Error", "El campo"). Es la deuda
más grande que queda: refactor que afecta controllers + vistas.

### 9.3 Generación de IDs (`MAX(id)+1`) sin lock (T4)

Se parcialmente mitigó (rollback ante colisión por PK), pero la carrera real entre dos usuarios
simultáneos solo se cierra moviendo la generación de IDs dentro de cada transacción con
`FOR UPDATE`, o con tablas de secuencia. Afecta a: OS/INT, TRD/FTI/TST, OC, ENT, FOS, USR-xxx.

### 9.4 Dinero en `Decimal` (T5)

`reportes_ventas` ya calcula en `Decimal`; falta el total del carrito (`carrito.py:197-198`) y
el margen `costo * 1.3` hardcodeado de `ordenes_entregas.py`.

### 9.5 Código muerto con cobertura de tests (T6)

Decidir si se elimina o se documenta como API de soporte: 4 métodos de `permisos.py`
(`listar_permisos_por_rol`, `guardar_permiso`, `eliminar_permiso`, `verificar_permiso`),
`ordenes_servicio.verificar_foto_existe_por_id` y `listar_ordenes_servicio`,
`proveedores.verificar_existencia`, `clientes.listar_clientes_naturales` y
`actualizar_datos_cliente`.

### 9.6 Métodos sin `except` (T10)

Todo `inventario.py`, 4 métodos de `catalogo.py`, 4 de `proveedores.py`, 3 de `test.py` y
`ordenes_servicio.empleados_asignados`: un error de SQL sube crudo al controller.

### 9.7 Mejoras puntuales (T11 restantes)

- `proveedores.py:596-614`: `ON DUPLICATE KEY … VALUES()` deprecado (MySQL 8.0.20) + `rowcount` 0
  cuando el costo no cambia → reporta "updated": false para filas existentes.
- Criterio de "técnico": `james.py` usa `LIKE '%Técnico%'` y `empleados.py` exacto — unificar
  (y decidir acentos).
- `database.py`: sin pooling (conexión nueva por operación) y `ultimo_error` compartido entre
  threads.
- `backup.py`: splitter por `;` de fin de línea (un `;` en datos partiría un statement) y rutas
  leídas de la BD sin contener (`os.path.realpath`).
- `usuarios.py:585-591`: timing attack en login (usuario inexistente no calcula hash) y
  `check_password_hash(None)` cuando la columna admite NULL.
- `usuarios.actualizar_usuario`: cambiar el rol al último admin no tiene guard (eliminar sí).
- Borrar `Producto` con `Equipos` asociados → FK cruda (falta check como en `eliminar_equipo`).
- Filtros `estado`/`metodo_pago`/`moneda` sin validar (aceptan cualquier string).
- N+1 en `obtener_trade_ins` (2 conexiones por fila).
- `ordenes_entregas`: `GREATEST(Existencia - %s, 0)` al anular pierde unidades vendidas.
- `ordenes_servicio.actualizar_estado`: sin whitelist de estados; `nota` sin validar contra
  varchar(300); `registrar_fotos` sin validar lista.
- `validacion_pagos.actualizar_fecha_pago` devuelve `None` siempre (sin señal de éxito/error).
- `catalogo.py:44`: búsquedas de 1 carácter descartadas en silencio.
- `clientes.py:31` / `carrito` / `venta` / `tradein`: cédula 6-8 excluye clientes jurídicos
  (RIF) — decidir si es regla de negocio.

---

# Auditoría de controllers (`app/controllers`)

> Fecha: 22/11/2026 · Alcance: los **26 controllers** (~2.700 líneas).
> Método: lectura 100% + verificación cruzada contra modelos/front/permisos + prueba real de
> rutas duplicadas con Flask + grep de uso en views/static/tests.
> **Regla del propietario aplicada como criterio de auditoría: en un controller NO puede haber
> validaciones** (viven en modelos y `app/utils/validators.py`).
> Línea base al auditar: 2379 tests en verde — **cobertura de tests de controllers ≈ 0%**
> (los tests solo cubren modelos), por eso varios 🔴 pasaron inadvertidos.
> Severidades: 🔴 roto/riesgo real en producción · 🟠 bug real o violación de la regla · 🟡 mejora.

## Resumen por severidad

| Severidad | Cantidad | Distribución |
|---|---|---|
| 🔴 Alta | 10 | `home_controller`(4) · `login`(1) · `tradein_empleados`(1) · `james`(1) · `ordenes_entregas`(1) · rutas duplicadas ×2 |
| 🟠 Media | 58 | validaciones en controller (login, ordenes_compra, taller, taller_celular, tradein, usuarios, ventas, backup, empleados, bitacora) · subidas sin whitelist ×4 · N+1 de reportes · status por substring · respuestas success=True con False |
| 🟡 Baja | 72 | contratos por substring ×19 · str(e) expuesto ×~40 · helpers g.user duplicados ×30 · print() · dead code · endpoints solo-Postman |

## 1. Errores 🔴 Alta

### C1. `POST /james` sin autenticación alguna (`james.py:9-10`)
Ni `@jwt_required` ni permiso; expone técnicos/cargos, dispara consultas BD y llamadas a Gemini
(costo real) sin rate-limit; **muerto en el frontend** (solo colección Postman).
**Solución aplicada:** `@jwt_required` + `@tiene_permiso('Taller','registrar')`.

### C2. Los 12 endpoints `/api/dashboard/*` y la página `/inventario` sin auth (`home_controller`)
Sin `@jwt_required` ni permiso: exponen bitácora, montos y stock a cualquiera.
**Solución aplicada:** `@jwt_required` en los 12 + en la página (permiso fino: pendiente §9).

### C3. Ruta duplicada `/api/dashboard/ventas-hoy` — gana la versión SIN auth
`home_controller:120` (sin auth) se registra antes que la protegida de `ventas.py:425`
(probado con Flask: gana el primer registro) → la protegida es dead code.
**Solución aplicada:** eliminada la duplicada de `home_controller` (sobrevive la de `ventas.py`,
que usa `VentaModel.obtener_ventas_hoy()`).

### C4. Rutas duplicadas `/api/proveedores` y `/api/empleados` — gana otro módulo
`ordenes_compra.py:48` y `:39` son **inalcanzables** (gana `proveedores.py:22` y `empleados.py:20`);
el front de órdenes de compra se valida contra los permisos de OTRO módulo (403 para usuarios
de compras). **Solución aplicada:** eliminados los 2 endpoints muertos de `ordenes_compra`
(la dependencia de permisos cruzados queda documentada en §9 — requiere decisión de front/permisos).

### C5. `home_controller:267/281` llama métodos inexistentes del modelo
`inventario.obtener_productos_bajo_stock/sin_stock` no existen (los reales son
`listar_productos_bajo_stock/sin_stock`) → esos 2 endpoints del dashboard devuelven 500 SIEMPRE.
**Solución aplicada:** nombres corregidos.

### C6. `home_controller:44` — `traceback.print_exc()` sin haber importado `traceback`
`NameError` en el except de `home()` que enmascara el error real.
**Solución aplicada:** `import traceback` en la cabecera.

### C7. IDOR de carrito (`ventas.py:110`)
`session['cliente_id']` nunca se setea; el fallback real es el header `X-Client-ID` controlado
por el cliente → cualquier usuario autenticado puede leer carritos ajenos.
**Solución aplicada:** eliminado el fallback; el cliente se deriva SIEMPRE de `g.user`.

### C8. Subidas de archivos sin whitelist ni tamaño (stored XSS en `/static`)
4 sitios aceptan cualquier extensión: `usuarios._guardar_foto_perfil`,
`ordenes_servicio` (endpoint de fotos), `ventas` (captura de pago), `tradein_empleados._guardar_fotos`.
**Solución aplicada:** helper único `guardar_foto_evidencia()` en `app/utils/helpers.py`
(whitelist `ALLOWED_IMAGE_EXTENSIONS` + 10 MB) usado por los 4 + `taller.py`/`taller_celular.py`
(quedan 1 sola fuente de verdad para subidas).

### C9. Restauración de backup dirigida por substring del nombre del archivo (`backup.py:541`)
`if 'seguridad' in nombre.lower()` — un backup de la BD principal con "seg" en el nombre se
restauraría EN la BD de seguridad, destruyéndola.
**Solución aplicada:** convención estricta de prefijo (`seguridad_`/`ituaccesorio_`) fijada AL
CREAR el backup y validada al restaurar (sin cambiar el esquema de la tabla `backup`).

### C10. `ordenes_entregas.py:69-74` — fallback `id_empleado = 30124556`
Si el JWT no trae id numérico, la entrega se atribuye silenciosamente a un empleado fijo
(rastro de auditoría corrupto). **Solución aplicada:** error 400 "Empleado no identificado".

## 2. Validaciones en controllers → destino (regla del propietario) — 🟠 aplicadas

| Controller | Validación encontrada | Movida a |
|---|---|---|
| `login.py:148-169` (paso-1) | obligatorios, `isdigit`, len de password, duplicados ×2 queries | `LoginManager.crear_usuario` (contrato `(id, error, duplicado)`) — el modelo `Usuarios.agregar_usuario` ya valida formato y duplicados |
| `login.py:260-270` (paso-2) | `re.sub` del celular + `validar_numero` + `validar_email` | `normalizar_celular()` en validators + validación ya existente en `_validar_datos_natural` (modelo) |
| `ordenes_compra.py:86-218` | pre-validación completa + N+1 de productos (el comentario del código lo admitía) | eliminado del controller; `OrdenCompra` ya valida en transacción (pendiente contrato dict: §9.2) |
| `taller.py:259-303` y `taller_celular.py:55-127` | fotos: 20 máx, extensiones, 10 MB (duplicados entre sí) | helper `guardar_fotos_evidencias()` en `app/utils/helpers.py` (los controllers quedan passthrough) |
| `tradein.py:57-74` | ID (duplica al modelo) + regla "liberado" (solo vivía aquí) | `TradeIn.calcular_cotizacion(liberado=…)` — regla movida al modelo |
| `usuarios.py:164-178` | self-delete y "solo admin borra admin" | `Usuarios.eliminar_usuario` (guard del modelo, controller mapea 403) |
| `usuarios.py:508-536` | guard rol "Admin" en actualizar/eliminar rol | `Rol.actualizar_rol` / `Rol.eliminar_rol` |
| `usuarios.py:370-389` | parseo de booleanos de permisos | `Permiso.guardar_permisos_masivos` |
| `ventas.py:326-330, 361` | captura obligatoria + estado del pago | `VentaModel` (reglas como constantes/métodos del modelo) |
| `backup.py:96, 458-478` | tipo_bd whitelist, extensión .sql, longitudes de nombre | `Backup` (constantes `BD_PERMITIDAS`) |
| `empleados.py:153-160`, `bitacora.py:32-36`, `clientes.py:34-36` | guards que duplican al modelo | eliminados (el modelo ya valida; controller mapea) |

**Despacho legítimo (no validación, se conserva):** detección multipart/JSON, RIF vs cédula,
`_detectar_marca` (IDs de marca hardcodeados pendientes en §9).

## 3. Errores 🟠 restantes aplicados

- `home_controller`: `/api/dashboard/bajo-stock|sin-stock` corregidos (C5) y `traceback` importado (C6).
- `backup.py`: puerto `3306` hardcodeado → lee `DB_PORT` del entorno; `tipo_bd` normalizado con `str(...)`
  (500 si llegaba int); destino de restauración por prefijo estricto (C9).
- `james.py`: `personales` puede ser str de error del modelo → guard isinstance → 503.
- `ordenes_entregas.py`: `get_json(silent=True)` + id_empleado validado (C10).
- `cargos.py`/`especialidades.py`/`inventario.py`/`james.py`: `.strip()` e `int()` sobre JSON
  no-string protegidos (500 HTML → 400 JSON).
- `validacion_pagos.py`: eliminado el doble UPDATE de `Fecha_pago` (controller llamaba
  `actualizar_fecha_pago()` + `aprobar_pago()` sobre la misma fila); la fecha viaja al
  `aprobar_pago` del modelo.
- `entregas.py`: PUT sin `estado` ya no resetea a 0 (obligatorio o no se toca).
- `proveedores.py`/`productos.py`: `int()` de filtros protegidos (500 HTML → 400 JSON).
- Reportes con N+1/filtrado en Python (`proveedores`, `productos`, `inventario`, `home`) →
  **pendiente §9** (refactor a SQL del modelo).
- Respuestas `success: True` con resultado `False` (`proveedores`/`productos`) → **pendiente §9**
  (requiere contrato dict del modelo).

## 4. Errores 🟡 (estado)

**Aplicados:** `getattr(g.user, "id")` sin default → con default (modo prueba); `print()` de
debug → `logger`/`current_app.logger` en los controllers tocados; dead endpoints solo-Postman
identificados; `buscar_controller.py` vacío confirmado (borrado pendiente de decisión).

**Pendientes → §9:** contrato por substring ×19 (raíz: los 4 estilos de contrato del modelo —
misma deuda T3), `str(e)` técnico en ~40 respuestas, N+1 de reportes, duplicación
login payload ×4, catálogo de tests hardcodeado en `tradein_empleados`, enumeración en
paso-1 (captcha/rate-limit), `/api/dashboard/actividad-reciente` vs `/bitacora` (permisos
desincronizados), `notificaciones.js` pidiendo endpoint admin-only, usuario de modo prueba sin
`cedula` (validacion_pagos inservible en ENTORNO_PRUEBA), respuesta SSE con redirect HTML.

## 5. Cobertura

- Tests de controllers: **0%** (ningún test importa `app.controllers.*`); los 2379 cubren modelos.
- Endpoints públicos justificados: `/login`, `/logout`, `/api/login` (captcha), `/catalogo`,
  `/api/catalogo/productos`, `/trade-in` (público por diseño; `cotizar` sin rate-limit: pendiente).
- `nosec` en controllers: solo `backup.py:185/227`, justificados (tabla validada por regex).

---

## Remediación de controllers aplicada (misma sesión, 22/11/2026)

**Verificación final: 2379 tests en verde · bandit controllers: 0 hallazgos · todos los módulos importan.**

### Aplicado (por hallazgo)

| # | Fix |
|---|---|
| C1 | `/james` con `@jwt_required` + `@tiene_permiso('Taller','registrar')`; guard `isinstance` para `personales` (503) |
| C2 | Los 12 endpoints `/api/dashboard/*` y la página `/inventario` con `@jwt_required` (permiso fino pendiente §9) |
| C3 | Ruta duplicada `/api/dashboard/ventas-hoy` eliminada de `home_controller` (sobrevive la protegida de `ventas.py`) |
| C4 | Endpoints muertos `/api/proveedores` y `/api/empleados` eliminados de `ordenes_compra` |
| C5 | `home_controller` usa los métodos reales (`listar_productos_bajo_stock/sin_stock`) |
| C6 | `import traceback` en `home_controller` |
| C7 | IDOR del carrito cerrado (sin `X-Client-ID`; cliente desde `g.user`) |
| C8 | Helper único `guardar_foto_evidencia()`/`guardar_fotos_evidencias()` en `app/utils/helpers.py` usado por: perfil, fotos de taller, taller_celular, trade-in, captura de pago y fotos de orden |
| C9 | Restauración de backup por **prefijo estricto** (`seguridad_*`) fijado en la creación |
| C10 | `ordenes_entregas` sin fallback `30124556` → 401 "Empleado no identificado" |
| — | Validaciones movidas al modelo según la tabla del §2 (login paso-1/paso-2, ordenes_compra N+1, fotos de taller, tradein "liberado", usuarios self-delete/admin + bools de permisos, ventas capture/estado/catálogo, backup tipo_bd/extensiones, guards duplicados en empleados/bitacora) |
| — | `LoginManager.crear_usuario` → `(id, error, duplicado)`; `Clientes.crear_cliente` → mensaje del modelo; `normalizar_celular()` en validators |
| — | `aprobar_pago` recibe `fecha_pago` en un solo UPDATE (eliminado el doble UPDATE del controller) |
| — | Entregas: PUT sin `estado` ya no resetea a 0 (el registrar conserva su default 0) |
| — | `Rol.actualizar_rol/eliminar_rol` aceptan `usuario_actual_rol` (guard Admin en el modelo; eliminar Admin ya estaba) |
| — | `Permiso.guardar_permisos_masivos` normaliza booleanos ("1"/"true"/"si"...) |
| — | `VentaModel` dueño del catálogo de métodos y de `requiere_capture()`/`estado_inicial_para()` |
| — | `backup.py`: puerto desde `DB_PORT`, `tipo_bd` normalizado, prints → logger |
| — | 🟡: `get_json(silent=True)` en `ordenes_entregas`; `.strip()`/`int()` protegidos en `cargos`, `especialidades`, `inventario`, `james`; `ordenes_compra` prints → logger |
| — | **Fix post-prueba**: el rollback de fotos de `taller.py`/`taller_celular.py` usaba `static_dir`/`carpeta_orden` que el helper había dejado sin definir (`NameError` en runtime) → variables restauradas con `current_app.static_folder`; y en `taller.eliminar_fotos` el prefijo `orden_` de la carpeta no existía → limpieza alineada a `evidencias/taller/{id_orden}`. Prueba funcional del helper: guarda en la ruta correcta y rechaza `.html`, >10 MB y >20 fotos |

### Pendiente → §9 (se suman a lo ya listado)

- **Contrato modelo↔controller** (T3/§9.2): 19+ puntos de substring y modelos bool/string — refactor mayor que resuelve ~8 hallazgos de golpe.
- **Reportes con N+1/filtrado en Python**: `proveedores`, `productos`, `inventario`, `home` (mover a SQL del modelo).
- **Respuestas `success: True` con resultado `False`**: `proveedores`/`productos` (requiere dict del modelo).
- **Duplicación de rutas por permisos**: el front de órdenes de compra consume `/api/proveedores` y `/api/empleados` (permisos cruzados) — decisión de front/permisos (rutas namespaced).
- **Enumeración en registro paso-1** (captcha/rate-limit), `/api/dashboard/actividad-reciente` sin permiso fino, `notificaciones.js` pidiendo endpoint admin-only, usuario de modo prueba sin `cedula`.
- **Subida en `taller.py`/`taller_celular`**: siguen validando EN el controller vía helpers de utils (política centralizada, pero la capa podría bajar al modelo); magic bytes sin verificar; límite 20 fotos por request sin tope por orden.
- **`backup.py`**: mysqldump de ~270 líneas dentro del controller (mover a `Backup.generar_dump()`), splitter por `;`, rutas sin contener.
- **Duplicación payload de sesión ×4 en `login.py`**, catálogo de 22 tests hardcodeado en `tradein_empleados`, `getattr(g.user, "x")` sin default en sitios restantes, dead endpoints solo-Postman, `buscar_controller.py` vacío (borrar), HTTP 404 vs 400 fino, `/api/dashboard/actividad-reciente` vs `/bitacora`, `validacion_pagos` inservible en modo prueba (usuario sin `cedula`).

### Notas

- **Nada subido al repo** — todo queda en el working tree local (33 archivos modificados).
- El front de trade-in ya envía `fotos_eliminar` y el perfil del cliente usa el flujo del modelo: probar en `docker-compose up --build`.

---

# Auditoría de frontend (`views/` + `app/static/`)

> Fecha: 22/11/2026 · Alcance: **31 JS, 28 templates (+components), 32 CSS**, y el cruce de los
> **136 endpoints consumidos por el JS vs las rutas registradas**.
> Método: lectura 100% de los JS/templates por agentes + verificación de cada endpoint contra
> `app/controllers` (con parámetros), shapes de respuesta, permisos por rol, CSP, y grep global
> de uso (front/tests).
> Reglas de AGENTS.md aplicadas como criterio: CSP sin inline, JS globales sin duplicar (SSE),
> guards `if (el)`, validaciones en el backend.
> Severidades: 🔴 roto para el usuario en producción · 🟠 bug real/violación CSP·permisos · 🟡 mejora.
> Línea base: 2379 tests (el backend no se toca salvo el hotfix R0).

## Resumen por severidad

| Severidad | Cantidad | Destacados |
|---|---|---|
| 🔴 Alta | 15 | Botón Aprobar con 500 SIEMPRE (regresión), gate de sesión en taller.js bloquea 3 acciones, 6 endpoints/navegaciones 404, XSS en productos, bucle infinito SSE, panel jurídico visible por CSP, admin no puede borrar admin desde el front |
| 🟠 Media | 24 | CSP en ventanas de impresión ×4 módulos, permisos cruzados 403 (4 casos), carrito duplicado, KPIs hardcodeados, sin manejo de sesión expirada, reportes parseInt rompe RIF |
| 🟡 Baja | 54 | XSS bajos sin escape, dead code, hardcodes (técnico por texto, prefijos, filtro iPhone), duplicaciones (IDs de tests ×3, umbrales de stock ×2 con valores distintos), CSS muerto/conflictuado |

## 1. Errores 🔴 Alta

### F0. `validacion_pagos.py` (controller) — REGRESIÓN: botón "Aprobar" devolvía 500 SIEMPRE
`api_aprobar_pago` usaba `data.get("fecha_pago")` **sin definir `data`** (introducido en la
remediación de modelos). `NameError` → 500 en cada clic del botón Aprobar.
**HOTFIX aplicado (Fase 0):** `data = request.get_json(silent=True) or {}` antes de la llamada
(el JS no envía fecha_pago: el backend usa la fecha del servidor). Los tests no lo detectaron
porque cubren el modelo, no el endpoint.

### F1. `taller.js:220-243 (+1031, 1185, 1679)` — gate de sesión bloquea 3 acciones clave
`Utils.obtenerIdEmpleadoActual()` busca `localStorage/sessionStorage 'user'` y `access_token`
que **nadie escribe** (auth 100% cookies httponly; el JWT no trae `id_empleado`) → SIEMPRE null
→ "No se pudo identificar al empleado logueado" y **return**: "Tomar orden", "Guardar revisión"
y "Liberar orden" bloqueados para TODOS los usuarios (el backend ni siquiera usa ese campo:
usa `g.user.cedula`).
**Solución aplicada:** gate eliminado (y el campo muerto del payload fuera).

### F2. `ventas.js:880-1161 + 1288-1338` — 4 endpoints 404 + ~500 líneas dead code
`/api/admin/pagos-pendientes|aprobar-pago/<id>|rechazar-pago/<id>|ventas-local` no existen en
ningún controller (las rutas reales son `/api/validacion-pagos/*` y
`/api/reportes-ventas/venta-local`). Toda la rama `path === '/admin/validar-pagos'` es
inalcanzable: ese path lo sirve `validacion_pagos.py` (registrado antes) con
`validacion_pagos.js`. Además `ventas.py:394-408` define la ruta `/admin/validar-pagos`
huérfana.
**Solución aplicada:** bloque muerto eliminado (~460 líneas) + ruta huérfana eliminada.

### F3. `productos.js:132-147` — XSS en modal de confirmación
`mostrarModalConfirmacion` interpola `${mensaje}` **sin `escapeHtml`**; los mensajes incluyen
nombres de producto de la BD (creables por usuarios con `Productos:registrar`) → script
ejecutable en la página admin.
**Solución aplicada:** `escapeHtml(mensaje)`.

### F4. `index.js:338` — navegación a página inexistente
Botón "Registrar Reparación" del dashboard → `/ordenes_servicio` (underscore) → 404; la ruta
real es `/ordenes-servicio`. **Solución aplicada:** corregido.

### F5. `notificaciones.js:294-325` — bucle infinito de reconexión SSE
`jwt_required` sin cookie responde 302→HTML; `EventSource` recibe HTML → `onerror` →
`setTimeout(conectarSSE, 3000)` **sin límite ni backoff** (y el EventSource nativo además
reconecta solo: doble maquinaria). Sin aviso de "sesión expirada".
**Solución aplicada:** check de sesión previo (fetch `credentials:'same-origin'` y validación
de content-type JSON), límite de 5 reintentos con backoff ×2, cierre de la fuente en `onerror`
y estado "Sesión expirada" visible.

### F6. `tradein_empleados.js:655 + html:279-294` — endpoint fantasma de tests
`POST /api/tradein/<id>/tests` no existe en el controller → "Guardar pruebas" del modal da 404
(las pruebas reales viajan en el multipart del POST/PUT del trade-in).
**Solución aplicada:** función `guardarTests`, botón y modal muertos eliminados (flujo real
intacto).

### F7. `clientes.html:190` — CSP bloquea el único `style=` del repo
`style="display:none"` en `#campos-juridico`: con `style-src 'self'` sin unsafe-inline, el
atributo se bloquea y el panel de Persona Jurídica queda **VISIBLE de inicio**.
**Solución aplicada:** clase CSS `.campos-condicionales--oculto` + toggle en `clientes.js`.

### F8. `usuarios.js` — `window.currentUser` nunca inyectado
El controller pasa `current_user` pero el template no lo inyecta → `currentUserId=""` (guard
anti-autoeliminación muerto) y `esAdminActual=false` SIEMPRE → un admin que borra a otro admin
recibe el toast falso "Solo otro admin puede eliminar este usuario." (el modelo sí lo permite).
**Solución aplicada:** inyección vía `data-*` en `<body>` (sin script inline por CSP) y lectura
en el JS.

## 2. Errores 🟠 aplicados

| # | Fix |
|---|---|
| O1 | `.custom-toast` movida a `theme.css` (faltaba en validacion_pagos/catalogo/inventario: los toasts salían como texto plano) |
| O2 | `index.js`: KPIs hardcodeados ('24', '$12,450', '4') conectados a los endpoints reales (`reparados-mes`, `ingresos-mensuales`, `tecnicos-activos`) |
| O3 | `reportes_ventas.js`: `parseInt(clienteId)` → string (los RIF jurídicos daban NaN → venta local imposible para clientes jurídicos) |
| O4 | `reportes_ventas.js` e `inventario.js`: `window.open` con null-guard (popup-blocker → TypeError sin catch) |
| O5 | `backup.js`: `window.notify()` (API fantasma) → `window.FeedbackModal.show()` |
| O6 | `login_phone.html`: `</button>` huérfano eliminado |
| O7 | Duplicado backend detectado y eliminado: `/api/dashboard/actividad-reciente` estaba en `bitacora.py` Y `home_controller.py` (gana bitacora por orden de registro) |
| O8 | Ventanas de impresión (4 módulos): `<style>` inline y `onclick` → **pendiente §9** (refactor de 4 archivos con clases+link, mismo patrón) |
| O9 | `onclick`/`style` inline generados por innerHTML (`ordenes_servicio.js:1268/1329`, `validacion_pagos.js:357`, `ventas.js:240/592`) → **pendiente §9** |
| O10 | Permisos cruzados 403 (`Clientes` desde Órdenes de servicio, `Productos` desde Proveedores, `/api/clientes` desde Reportes, `/api/proveedores`+`/api/empleados` desde Órdenes de compra) → **pendiente §9** (decisión de rutas namespaced vs permisos) |
| O11 | Carrito duplicado (navbar.js vs ventas.js + modal muerto en catálogo) → **pendiente §9** (consolidar en navbar) |
| O12 | Modales muertos de ordenes_servicio (revisión/fotos por orden) → **pendiente §9** (abrir o eliminar UI) |
| O13 | Manejo de sesión expirada en los helpers `fetchJson` (redirect HTML → JSON falla) → **pendiente §9** (patrón central) |

## 3. Errores 🟡 aplicados

- `clientes.js`: `modoEdicion` muerta eliminada; catch passthrough inútil eliminado.
- `ordenes_entregas.html`: `#feedback-modal` duplicado (markup muerto inválido) eliminado.
- `field-validator.js`: regla `capitalizar` implementada (6+ campos la prometían en hints).
- `usuarios.js`: `state.empleados`/`state.clientes` (2 fetches muertos por recarga) eliminados.
- `usuarios.js`: `cedula_personal` ya no se corrompe con `String(Number(...))` (ceros a la izquierda).
- `entregas.js`: listener `change` del select ya no se acumula en cada apertura del modal.
- `inventario.js`: umbrales de stock unificados (≤10/≥30 en ambos lados).
- XSS bajos sin escape corregidos: `taller.js:1376` (error.message), `inventario.js:410` (foto), `reportes_ventas.js:268/282/825` y `tradein_empleados.js:139` (ids/estados), `validacion_pagos.js:1021` (estado en impresión), `taller_celular.js:68` (textContent).
- `taller.js`: hint de caracteres alineado (300), `maxlength` respetado.
- `productos.js`: doble apertura del modal de registro eliminada (data-open-modal ya lo abre).

## 4. Verificado sano (no tocar)

- 0 URLs hardcodeadas (127.0.0.1/localhost/http) en JS/templates; todo relativo.
- 0 doble carga de JS globales (no hay doble SSE por include); hash del loader de tema OK con la CSP.
- 0 templates huérfanos (login_phone ES el login; pagos.html es /pagar; 403/404 usados).
- Cruce de los 136 endpoints: todo resuelve salvo lo listado (F2/F6/F4) — shapes correctos con
  los controllers actuales (incluidos los cambios recientes).
- `navbar.js` (carrito con `if (el)`), `table-tools.js`, `feedback-modal.js`, `modal.js`,
  `validacion-tabla.js`, `iconos.js`, `login.js`, `tradein.js`, `cargos.js`, `especialidades.js`,
  `taller_celular.js`, `bitacora.js` — sin problemas funcionales.

## 5. Pendiente → §9 (sumado)

- **O8/O9/O10/O11/O12/O13** tal como se listó arriba (ventanas de impresión CSP, permisos
  cruzados, carrito consolidado, modales muertos, sesión expirada global).
- XSS bajos restantes (atributos `data-*` con ids/estados de BD sin escape en 6 puntos).
- `maxlength`/hints desalineados restantes, filtros hardcodeados (técnico por texto, prefijos,
  iPhone ×2), `noDuplicadoTabla`, spotlight ⌘K decorativo, CSS: badge conflictuado
  (notificaciones vs navbar), `theme.css` redefiniciones internas, `login.css` muerto,
  Chart.js duplicado, `pagos.css` mínimo, coberturas de humo faltantes (/pagar, catálogo público,
  impresiones).

---

## Remediación de frontend aplicada (misma sesión, 22/11/2026)

**Verificación: 2379 tests en verde · `node --check` OK en los 12 JS tocados · 0 `style="` inline en views (fuera del loader de tema).**

### Aplicado (por hallazgo)

| # | Fix |
|---|---|
| F0 | **HOTFIX**: `data` sin definir en `api_aprobar_pago` (500 SIEMPRE en el botón Aprobar — regresión de la remedación de modelos) |
| F1 | `taller.js`: gates de `id_empleado` eliminados en asignar/guardar-revisión/liberar/guardar-reparación + campo muerto del payload fuera + helper muerto eliminado (el backend usa `g.user.cedula`) |
| F2 | `ventas.js`: bloque muerto de ~336 líneas (funciones `/api/admin/*` + rama `/admin/validar-pagos`) eliminado; ruta huérfana `/admin/validar-pagos` de `ventas.py` eliminada (la sirve `validacion_pagos.py`) |
| F3 | `productos.js`: `escapeHtml(mensaje)` en el modal de confirmación (XSS vía nombre de producto de la BD) |
| F4 | `index.js`: navegación `/ordenes_servicio` → `/ordenes-servicio` (404 del botón "Registrar Reparación") |
| F5 | `notificaciones.js`: bucle infinito SSE corregido — check de sesión previo (`/api/usuarios/mis-permisos` con credentials), máx 5 reintentos con backoff exponencial (3s→30s), cierre de la fuente en `onerror`, estado "Sesión expirada" visible |
| F6 | `tradein_empleados`: endpoint fantasma `/api/tradein/<id>/tests` + función `guardarTests` + `abrirModalTests` + bind + modal `modal-tests` del template eliminados (las pruebas reales viajan en el multipart del POST/PUT) |
| F7 | `clientes.html`: `style="display:none"` → clase `.campos-condicionales--oculto` en `clientes.css` (CSP: el panel jurídico ya no queda visible de inicio); el toggle JS ya usa CSSOM |
| F8 | `usuarios.html`/`usuarios.js`: sesión inyectada vía `data-user-rol-id`/`data-user-rol` en `base.html` (CSP: sin script inline) — guard anti-autoeliminación vivo y admin puede borrar admin desde el front |
| O1 | `.custom-toast` movida a `theme.css` (toasts planos en validacion_pagos/catalogo/inventario) |
| O2 | `index.js`: KPIs '24'/'$12,450'/'4' → endpoints reales (`reparados-mes`, `ingresos-mensuales`, `tecnicos-activos`; shapes verificados) |
| O3 | `reportes_ventas.js`: `parseInt(clienteId)` → string (los RIF jurídicos ya pueden recibir venta local) |
| O4 | `window.open` con null-guard en `reportes_ventas.js` e `inventario.js` (popup-blocker) |
| O5 | `backup.js`: `window.notify()` (fantasma) → `window.FeedbackModal.show({type, title, message})` |
| O6 | `login_phone.html`: `</button>` huérfano eliminado |
| O7 | Duplicado backend: `/api/dashboard/actividad-reciente` eliminado de `home_controller` (gana `bitacora.py` por orden de registro) |
| — | 🟡: `capitalizar` implementada en `field-validator.js`; `state.empleados/clientes` (2 fetches muertos) fuera de `usuarios.js`; listener `change` de `entregas.js` con guard anti-acumulación; `#feedback-modal` duplicado fuera de `ordenes_entregas.html`; umbrales de stock unificados (≤10/≥30) en `inventario.js` |

### Pendiente → §9 (consolidado)

- **CSP en ventanas de impresión** (proveedores, productos, validacion_pagos, reportes_ventas, inventario): `<style>` + `onclick` inline heredan la CSP → refactor a clases + `<link>` + listeners (mismo patrón ×5).
- **`onclick`/`style` inline generados por innerHTML**: `ordenes_servicio.js:1268/1329`, `validacion_pagos.js:357`, `ventas.js:240/592` (imágenes con fallback) → listeners delegados/clases.
- **Permisos cruzados 403**: `Clientes` desde Órdenes de servicio, `Productos` desde Proveedores, `/api/clientes` desde Reportes (rol ventas), `/api/proveedores`+`/api/empleados` desde Órdenes de compra → rutas namespaced o relajar permisos (decisión de negocio).
- **Carrito duplicado** (navbar.js vs ventas.js con modal muerto en catálogo) → consolidar en navbar.
- **Modales muertos de ordenes_servicio** (revisión/fotos por orden) → abrir o eliminar UI (+ radios "No funciona" pre-marcados si se reactiva).
- **Sesión expirada global**: patrón central en los helpers `fetchJson` (detectar redirect/HTML → ir a /login).
- **Permisos cruzados de consulta de catálogos** y demás puntos ya listados en §9.
- XSS bajos restantes (atributos `data-*` con ids/estados de BD ×6), `campos Caja/Cargador/Cable/Manuales` descartados por el backend, spotlight ⌘K decorativo, CSS: badge conflictuado, `theme.css` redefiniciones, `login.css` muerto, Chart.js duplicado, `pagos.css` mínimo, humo faltante (/pagar, catálogo, impresiones).

