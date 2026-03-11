# PAIN_LOG.md — Auditoría de Incorporación: simple_erp

**Rol del auditor:** Ingeniero nuevo, sin conocimiento previo del proyecto.
**Método:** Seguir únicamente el README.md. Consultar el código solo para confirmar qué falla y por qué.
**Fecha:** 2026-03-10

---

## Puntos de Fricción

### 1. [MISSING_DOC] El README no contiene ninguna instrucción de configuración

El README tiene 11 líneas. Describe _qué es_ el proyecto pero no da ninguna instrucción sobre cómo ejecutarlo. No se menciona clonar el repositorio, instalar dependencias, configurar la base de datos, ejecutar migraciones ni iniciar el servidor. Un ingeniero nuevo se queda mirando el repositorio sin ningún punto de entrada.

**Severidad: BLOQUEANTE — No se puede avanzar más allá del paso 0 sin adivinar.**
**Tiempo estimado perdido:** 30–60 min de orientación antes de intentar siquiera el primer comando.

---

### 2. [IMPLICIT_DEP] La versión de Python nunca se declara

`requirements.txt` lista versiones de paquetes pero no la versión de Python requerida. Django 4.2.x es compatible con Python 3.8–3.11. Un desarrollador con Python 3.12+ puede encontrar incompatibilidades sutiles (por ejemplo, `datetime.utcnow()` está deprecado en versiones internas). Nada en el repositorio declara la versión de runtime esperada.

**Severidad: MEDIA — Funciona por casualidad en algunas versiones, falla silenciosamente en otras.**

---

### 3. [IMPLICIT_DEP] PostgreSQL es requerido pero nunca se menciona

`requirements.txt` incluye `psycopg2==2.9.6`. Este es un adaptador de PostgreSQL. El README nunca menciona PostgreSQL como dependencia. Un ingeniero nuevo que intente `pip install -r requirements.txt` en una máquina sin PostgreSQL instalado recibirá un error del compilador C:

```
Error: pg_config executable not found.
```

Este mensaje de error no dice "instala PostgreSQL." Un desarrollador junior buscará `pg_config` durante 30+ minutos antes de entender la causa raíz.

**Severidad: BLOQUEANTE — `pip install` falla antes de siquiera tocar la aplicación.**

---

### 4. [IMPLICIT_DEP] psycopg2 requiere cabeceras de PostgreSQL a nivel de sistema operativo, no solo una BD corriendo

Aunque el desarrollador instale PostgreSQL, `psycopg2` requiere las cabeceras de desarrollo en tiempo de compilación (`libpq-dev` en Debian/Ubuntu, `postgresql-devel` en RHEL, una instalación completa de PG en macOS/Windows). Este es un paso de instalación separado al de ejecutar un servidor PostgreSQL. No está documentado en ningún lugar.

**Severidad: BLOQUEANTE — pip install falla silenciosamente o con errores crípticos a nivel de C.**

---

### 5. [MISSING_DOC] No hay instrucciones para crear un entorno virtual

No existen instrucciones para crear un entorno virtual de Python (`python -m venv venv` / `source venv/bin/activate`). Un ingeniero nuevo instalará los paquetes de forma global (contaminando su sistema) o estará confundido sobre el aislamiento. Son probables conflictos de dependencias con paquetes del sistema en máquinas de desarrollo.

**Severidad: BAJA — No impide la configuración, pero causa contaminación del entorno y problemas futuros.**

---

### 6. [ENV_GAP] Las credenciales de la base de datos están hardcodeadas en settings.py sin .env.example

`gestor/settings.py` contiene:

```python
'NAME': 'tienda',
'USER': 'postgres',
'PASSWORD': 'my_pass',
'HOST': '127.0.0.1',
'PORT': '5432',
```

No existe un `.env.example`, no se menciona el uso de variables de entorno y no hay ninguna guía que indique que estos valores deben coincidir con una base de datos creada localmente. Un ingeniero nuevo debe:
1. Adivinar que PostgreSQL es necesario (ver #3)
2. Crear manualmente una base de datos llamada `tienda`
3. Usar las credenciales `postgres`/`my_pass` (inseguro) o editar `settings.py` directamente

**Severidad: BLOQUEANTE — La app no puede conectarse a la base de datos sin que estos valores hardcodeados coincidan exactamente, o sin modificar el código fuente.**

---

### 7. [ENV_GAP] El SECRET_KEY de Django está hardcodeado como un string de marcador de posición

`gestor/settings.py` contiene:

```python
SECRET_KEY = 'super_secret_key'
```

No hay ninguna guía sobre que esto debe cambiarse, no existe `.env.example` y no hay ninguna herramienta como `django-environ` implementada. En desarrollo el riesgo es bajo, pero no transmite ningún patrón de configuración basado en variables de entorno.

**Severidad: BAJA en desarrollo, CRÍTICA en cualquier despliegue similar a producción.**

---

### 8. [MISSING_DOC] No hay instrucción para ejecutar las migraciones de base de datos

Tras conectarse a PostgreSQL, el desarrollador debe ejecutar `python manage.py migrate` para crear las 13 tablas de la aplicación. Este comando no se menciona en ningún lugar. Sin él, cualquier página que acceda a la base de datos fallará con:

```
django.db.utils.ProgrammingError: relation "tienda_clientes" does not exist
```

**Severidad: BLOQUEANTE — Todas las vistas que acceden a datos fallan sin las migraciones.**

---

### 9. [MISSING_DOC] No hay instrucción para crear un superusuario ni explicación sobre el sistema de login

La app redirige a los usuarios no autenticados a `/login`. El README no ofrece ninguna guía sobre cómo crear un usuario administrador (`python manage.py createsuperuser`) ni sobre credenciales por defecto. Un ingeniero nuevo que logre ejecutar la app llegará a una pantalla de login sin forma de entrar.

**Severidad: BLOQUEANTE — No se puede acceder a ninguna funcionalidad de la aplicación.**

---

### 10. [BROKEN_CMD] Los scripts de generación de Excel usan rutas Linux hardcodeadas que fallan en cualquier otra máquina

`gestor/lanzar_factura.py` y `gestor/lanzar_albaran.py` contienen rutas absolutas hardcodeadas:

```python
workbook = load_workbook('/home/ubuntu/gestor/23AKP08PL_PLANTILLA.xlsx')
path = '/home/ubuntu/gestor/facturas/'
```

Estas rutas son específicas del servidor Ubuntu del desarrollador original. En cualquier otra máquina (sistema operativo diferente, nombre de usuario diferente, estructura de directorios diferente), estos scripts lanzarán:

```
FileNotFoundError: [Errno 2] No such file or directory: '/home/ubuntu/gestor/23AKP08PL_PLANTILLA.xlsx'
```

**Severidad: BLOQUEANTE — La generación de facturas y albaranes está completamente rota en cualquier máquina que no sea el servidor original.**

---

### 11. [MISSING_DOC] Los directorios de salida (facturas/, albaranes/) nunca se crean

Los scripts intentan guardar los archivos Excel generados en `/home/ubuntu/gestor/facturas/` y `/home/ubuntu/gestor/albaranes/`. Estos directorios no se crean en ningún paso de configuración, no se mencionan en el README y no están incluidos en el repositorio. Aunque se resolviera el problema de las rutas (#10), la operación de guardado fallaría con un `FileNotFoundError`.

**Severidad: BLOQUEANTE — La generación de Excel falla en el último paso de escritura incluso después de corregir el problema de rutas.**

---

### 12. [ENV_GAP] Las rutas de las plantillas Excel en los scripts no coinciden con la ubicación real de las plantillas en el repositorio

Las plantillas Excel (`23AKP08PL_PLANTILLA.xlsx`, `23AKP08_PLANTILLA.xlsx`) están confirmadas en la raíz del repositorio. Los scripts las referencian en `/home/ubuntu/gestor/`. No existe ninguna documentación que mapee "plantillas en el repositorio" con "dónde las esperan los scripts." Un desarrollador debe descubrir esta discrepancia leyendo el código fuente.

**Severidad: BLOQUEANTE (compuesto con #10) — Incluso mover las plantillas al lugar correcto requiere leer código fuente al que nunca se apuntó.**

---

### 13. [SILENT_FAIL] El envío de correo usa credenciales de marcador de posición y falla sin retroalimentación visible

`gestor/lanzar_factura.py` contiene:

```python
sender_email = "my_email@example.com"
receiver_email = "your_email@example.com"
smtp_server = "smtp.example.com"
smtp_password = "super_secret_smtp_password"
```

Cuando se activa la generación de Excel, el script intenta enviar un correo vía SMTP usando estas credenciales falsas. La llamada SMTP expirará o lanzará un error de conexión. El script no envuelve esto en un try/except, por lo que dependiendo de la llamada subprocess de Django, este fallo puede propagarse como un error 500 en la UI — sin ningún mensaje accionable que apunte a la configuración de correo.

**Severidad: MEDIA — Funcionalidad rota silenciosa o ruidosamente. No existe .env.example que guíe la configuración real.**

---

### 14. [MISSING_DOC] No se menciona la recolección de archivos estáticos para despliegues sin modo debug

El proyecto sirve CSS e imágenes desde `tienda/static/`. En modo DEBUG (que está hardcodeado a `True`), Django sirve los archivos estáticos automáticamente. Sin embargo, el README no indica que `python manage.py collectstatic` sea necesario para ningún escenario de despliegue. Un desarrollador que intente replicar un entorno de staging encontrará estilos ausentes sin explicación.

**Severidad: BAJA en desarrollo local puro, MEDIA una vez que se intenta cualquier despliegue en servidor.**

---

### 15. [BROKEN_CMD] La carpeta de migraciones no existe — `migrate` no crea las tablas de la aplicación

La aplicación `tienda` define 13 modelos en `tienda/models.py` (Clientes, Pedidos, Facturas, etc.) pero **no existe el directorio `tienda/migrations/`**. Al ejecutar `python manage.py migrate`, Django solo aplicará sus propias migraciones internas (auth, sessions, admin, etc.). Las 13 tablas de la aplicación nunca se crearán. Cualquier vista que acceda a la base de datos fallará con:

```
django.db.utils.ProgrammingError: relation "tienda_clientes" does not exist
```

El desarrollador debe ejecutar primero `python manage.py makemigrations tienda` para generar el archivo de migración inicial, y luego `python manage.py migrate`. Ninguno de estos dos pasos está documentado.

**Severidad: BLOQUEANTE — `migrate` por sí solo no es suficiente. Sin `makemigrations` previo, la app no tiene tablas.**

---

### 16. [BROKEN_CMD] `subprocess` llama a `python3` — falla en Windows donde el ejecutable es `python`

En `gestor/views.py`, ambas vistas de generación de Excel usan:

```python
subprocess.check_call([
    "python3",
    "/home/ubuntu/gestor/gestor/lanzar_factura.py",
    ...
])
```

En Windows, `python3` típicamente no existe en el PATH — el ejecutable es `python`. La llamada al subprocess fallará con:

```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

No hay ninguna mención al sistema operativo requerido en la documentación.

**Severidad: BLOQUEANTE en Windows — la generación de Excel es completamente inoperativa en entornos Windows.**

---

### 17. [SILENT_FAIL] Navegar directamente a `/pedidos/`, `/facturas/` o `/albaranes/` produce un error 500

Las tres vistas esperan recibir un parámetro GET `?id_cliente=`. Al cargar la vista por primera vez, hacen:

```python
id_cliente = request.GET.get("id_cliente")   # retorna None si no hay parámetro
request.session["id_cliente"] = id_cliente
...
if id_cliente.lower() == "todos":            # AttributeError: 'NoneType'
```

Si un usuario navega directamente a `/pedidos/` sin `?id_cliente=todos`, la vista crashea con un error 500 no descriptivo. El README no documenta el formato de URL esperado ni que el parámetro es obligatorio.

**Severidad: BLOQUEANTE — tres de las vistas principales no son accesibles por URL directa.**

---

### 18. [MISSING_DOC] No existe `.gitignore` — las credenciales hardcodeadas están confirmadas en el historial de git

No existe ningún archivo `.gitignore` en el repositorio. Esto significa que `gestor/settings.py` con la contraseña de PostgreSQL y el `SECRET_KEY` de Django ha sido confirmado directamente en el historial de git. Cualquier persona que clone el repositorio obtiene credenciales que podrían ser reales en producción, sin advertencia alguna.

**Severidad: MEDIA (seguridad) — las credenciales son de ejemplo, pero el patrón establece hábitos peligrosos y no hay barrera para credenciales reales en el futuro.**

---

### 19. [BROKEN_CMD] `STATIC_ROOT` no está configurado — `collectstatic` falla si se intenta ejecutar

`gestor/settings.py` define `STATIC_URL` y `STATICFILES_DIRS` pero omite `STATIC_ROOT`. Si un desarrollador intenta ejecutar `python manage.py collectstatic` (paso mencionado como necesario en el punto #14), Django lanzará:

```
django.core.exceptions.ImproperlyConfigured: You're using the staticfiles app
without having set the STATIC_ROOT setting to a filesystem path.
```

El comando que debería existir para despliegues está roto antes de poder ejecutarse.

**Severidad: MEDIA — el comando de despliegue de estáticos falla por configuración incompleta.**

---

### 20. [SILENT_FAIL] `lanzar_factura.py` usa `", ".join()` sobre un string en lugar de una lista — corrompe el campo `To:` del correo

En `gestor/lanzar_factura.py`, el método `send_email()` contiene:

```python
receiver_email = "your_email@example.com"   # string, no lista
msg["To"] = ", ".join(receiver_email)        # itera caracteres individuales
```

`", ".join()` sobre un string itera sus caracteres, produciendo:

```
y, o, u, r, _, e, m, a, i, l, @, e, x, a, m, p, l, e, ...
```

El campo `To:` del correo queda completamente malformado. El envío falla silenciosamente o con un error de protocolo SMTP. Este bug no existe en `lanzar_albaran.py` donde `receiver_email` se usa directamente sin `join()`.

**Severidad: MEDIA — bug de lógica en el código de email que produce un fallo silencioso adicional al ya documentado en el punto #13.**

---

### 21. [MISSING_DOC] El panel de administración de Django está vacío — ningún modelo de la app está registrado

`tienda/admin.py` contiene únicamente:

```python
from django.contrib import admin
# Register your models here.
```

Si un desarrollador accede a `/admin/` después de crear un superusuario, verá solo los modelos internos de Django (Usuarios y Grupos). No hay forma de gestionar clientes, pedidos, facturas ni ningún dato de la aplicación desde el admin. Esto no está documentado y puede llevar a perder tiempo buscando los datos en un panel que parece funcionar pero no muestra nada.

**Severidad: BAJA — la interfaz principal de la app es funcional, pero la ausencia es confusa para un nuevo desarrollador.**

---

### 22. [SILENT_FAIL] `lanzar_factura.py` usa el directorio `albaranes/` como carpeta temporal para facturas — error de copy-paste

En `gestor/lanzar_factura.py`, el bloque `__main__` contiene:

```python
RUTA_ORIGINAL = r"/home/ubuntu/gestor/23AKP08PL_PLANTILLA.xlsx"
RUTA = r"/home/ubuntu/gestor/albaranes/albaran_prov.xlsx"   # ← directorio incorrecto para una factura
shutil.copy(RUTA_ORIGINAL, RUTA)
```

El script de **facturas** copia la plantilla al directorio de **albaranes** como archivo temporal, y luego lo renombra a `/facturas/`. Ambos scripts comparten la misma ruta de archivo temporal (`albaranes/albaran_prov.xlsx`). Si se generan una factura y un albarán simultáneamente, el segundo proceso sobreescribe el archivo temporal del primero, corrompiendo el resultado — condición de carrera sin manejo de errores.

**Severidad: MEDIA — riesgo de corrupción de datos bajo carga concurrente, además de lógica confusa para quien mantiene el código.**

---

## Resumen de Severidad

| # | Etiqueta | Descripción | Severidad |
|---|----------|-------------|-----------|
| 1 | MISSING_DOC | Sin instrucciones de configuración en el README | BLOQUEANTE |
| 2 | IMPLICIT_DEP | Versión de Python sin declarar | MEDIA |
| 3 | IMPLICIT_DEP | PostgreSQL no mencionado como dependencia | BLOQUEANTE |
| 4 | IMPLICIT_DEP | psycopg2 necesita cabeceras a nivel de SO | BLOQUEANTE |
| 5 | MISSING_DOC | Sin instrucciones de entorno virtual | BAJA |
| 6 | ENV_GAP | Credenciales de BD hardcodeadas, sin .env.example | BLOQUEANTE |
| 7 | ENV_GAP | SECRET_KEY hardcodeado, sin patrón de .env | BAJA (dev) / CRÍTICA (prod) |
| 8 | MISSING_DOC | Sin instrucción de `migrate` | BLOQUEANTE |
| 9 | MISSING_DOC | Sin guía para crear superusuario | BLOQUEANTE |
| 10 | BROKEN_CMD | Rutas `/home/ubuntu/` hardcodeadas en los scripts | BLOQUEANTE |
| 11 | MISSING_DOC | Directorios de salida nunca creados | BLOQUEANTE |
| 12 | ENV_GAP | Ruta de plantillas en scripts ≠ ubicación real en el repositorio | BLOQUEANTE |
| 13 | SILENT_FAIL | Credenciales SMTP de marcador de posición, sin error visible | MEDIA |
| 14 | MISSING_DOC | Sin guía de `collectstatic` | BAJA |
| 15 | BROKEN_CMD | Sin carpeta `migrations/` — `makemigrations` requerido antes de `migrate` | BLOQUEANTE |
| 16 | BROKEN_CMD | Subprocess llama a `python3` — falla en Windows | BLOQUEANTE (Windows) |
| 17 | SILENT_FAIL | Navegación directa a vistas principales crashea con 500 (`None.lower()`) | BLOQUEANTE |
| 18 | MISSING_DOC | Sin `.gitignore` — credenciales confirmadas en historial de git | MEDIA (seguridad) |
| 19 | BROKEN_CMD | `STATIC_ROOT` no configurado — `collectstatic` falla | MEDIA |
| 20 | SILENT_FAIL | `", ".join()` sobre string corrompe el campo `To:` del correo | MEDIA |
| 21 | MISSING_DOC | Panel admin vacío — ningún modelo registrado | BAJA |
| 22 | SILENT_FAIL | Script de facturas usa carpeta de albaranes como temporal — condición de carrera | MEDIA |

**Total de puntos de fricción encontrados:** 22

**Primer bloqueante completo:** Punto #1 — El README no provee ninguna instrucción de configuración. Un ingeniero nuevo no puede tomar ninguna acción significativa sin leer el código fuente.

**Hasta dónde se llega antes del primer bloqueo total:** Paso 0. No hay ningún paso que intentar.

**Tiempo estimado perdido para un empleado nuevo:**
- 30–60 min intentando inferir la configuración desde el README y la estructura de archivos
- 45–90 min depurando el error `pg_config not found` (puntos #3 y #4)
- 30 min creando la base de datos PostgreSQL con las credenciales correctas (#6)
- 30 min descubriendo que `migrate` no basta y que falta `makemigrations` (#15)
- 15 min creando un superusuario para superar la pantalla de login (#9)
- 30–60 min depurando el error 500 al navegar directamente a pedidos/facturas/albaranes (#17)
- 60+ min depurando `FileNotFoundError` en la generación de Excel (#10, #11, #12, #16)

**Tiempo total estimado perdido: 4–6 horas** antes de que un ingeniero nuevo pueda realizar cualquier flujo de trabajo completo. En Windows o sin experiencia en Django/PostgreSQL, el tiempo puede exceder un día completo de trabajo.
