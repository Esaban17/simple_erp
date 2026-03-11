# GOLDEN_PATH.md — Deliverable 2: El Camino Dorado

**Rol:** Equipo de Plataforma.
**Objetivo:** Eliminar cada bloqueante del PAIN_LOG con artefactos reproducibles.
**Fecha:** 2026-03-10

---

## Instrucciones de inicio rápido

### Opción A — Docker (recomendado, sin instalar PostgreSQL manualmente)

```bash
git clone <repo>
cd simple_erp
cp .env.example .env          # edita DB_PASSWORD y DJANGO_SECRET_KEY
docker compose up --build     # levanta PostgreSQL + Django automáticamente
```

Abre http://localhost:8000 — llegará al login.

Para crear el primer usuario administrador:
```bash
docker compose exec web python manage.py createsuperuser
```

### Opción B — Local (sin Docker)

```bash
git clone <repo>
cd simple_erp
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
make setup                    # instala deps + dirs + migrate + superuser
make run
```

---

## Artefactos creados

### 1. `.env.example`
Documenta todas las variables de entorno requeridas con comentarios explicando valores válidos. Incluye variables para Django, PostgreSQL, SMTP y rutas de archivos.

### 2. `Makefile`
Automatiza el ciclo de vida del proyecto en desarrollo local:
- `make setup` → flujo completo de inicio (env → install → dirs → migrate → superuser)
- `make migrate` → ejecuta `makemigrations tienda` **antes** de `migrate`
- `make dirs` → crea `facturas/` y `albaranes/`
- `make help` → muestra todos los comandos disponibles

### 3. `docker-compose.yml`
Levanta el stack completo con un solo comando:
- Servicio `db`: PostgreSQL 15 con healthcheck
- Servicio `web`: construido desde Dockerfile, espera que `db` esté sano
- Monta `./facturas` y `./albaranes` como volúmenes
- Override `DB_HOST: db` para comunicación interna entre contenedores

### 4. `Dockerfile` (requerido por docker-compose)
- Fija Python 3.11
- Instala `libpq-dev` y `gcc` (cabeceras de PostgreSQL para psycopg2)
- Crea los directorios `facturas/` y `albaranes/`

### 5. `.gitignore`
Previene que `.env`, archivos compilados, directorios de salida y el entorno virtual sean confirmados al repositorio.

---

## Archivos de código modificados

| Archivo | Cambio |
|---------|--------|
| `requirements.txt` | Añadido `python-dotenv==1.0.0` |
| `gestor/settings.py` | `load_dotenv()` + `os.environ.get()` para SECRET_KEY, DEBUG, ALLOWED_HOSTS y BD + `STATIC_ROOT` |
| `gestor/views.py` | `sys.executable` en lugar de `"python3"` + rutas de scripts con `Path(__file__).parent` |
| `gestor/lanzar_factura.py` | Rutas dinámicas desde `PROJECT_ROOT` / variables de entorno + `os.makedirs(exist_ok=True)` |
| `gestor/lanzar_albaran.py` | Ídem |

---

## Tabla de cobertura — Pain Point → Artefacto → Estado

| # | Etiqueta | Pain Point | Artefacto que lo fija | Estado |
|---|----------|------------|----------------------|--------|
| 1 | MISSING_DOC | Sin instrucciones de configuración | `Makefile` (`make setup`) + `docker-compose.yml` | **Fijado** |
| 2 | IMPLICIT_DEP | Versión de Python sin declarar | `Dockerfile` (`FROM python:3.11-slim`) | **Fijado** |
| 3 | IMPLICIT_DEP | PostgreSQL no mencionado | `docker-compose.yml` (servicio `db`) | **Fijado** |
| 4 | IMPLICIT_DEP | psycopg2 requiere cabeceras de SO | `Dockerfile` (`apt-get libpq-dev gcc`) | **Fijado** |
| 5 | MISSING_DOC | Sin instrucciones de entorno virtual | `Makefile` (target `install`) | **Fijado** |
| 6 | ENV_GAP | Credenciales DB hardcodeadas | `.env.example` + `settings.py` con `os.environ` | **Fijado** |
| 7 | ENV_GAP | SECRET_KEY hardcodeado | `.env.example` + `settings.py` con `os.environ` | **Fijado** |
| 8 | MISSING_DOC | Sin instrucción de `migrate` | `Makefile` (`make migrate`) + `docker-compose.yml` command | **Fijado** |
| 9 | MISSING_DOC | Sin guía para crear superusuario | `Makefile` (`make superuser`) + instrucciones en GOLDEN_PATH | **Fijado** |
| 10 | BROKEN_CMD | Rutas `/home/ubuntu/` hardcodeadas | `views.py` + `lanzar_*.py` con `PROJECT_ROOT` | **Fijado** |
| 11 | MISSING_DOC | Directorios de salida nunca creados | `Makefile` (`make dirs`) + `Dockerfile` + `os.makedirs` en scripts | **Fijado** |
| 12 | ENV_GAP | Ruta de plantilla ≠ ubicación en repo | `.env.example` (`PLANTILLA_FACTURAS/ALBARANES`) + `lanzar_*.py` | **Fijado** |
| 13 | SILENT_FAIL | Credenciales SMTP de placeholder | `.env.example` documenta todas las variables SMTP | **Parcial** |
| 14 | MISSING_DOC | Sin guía de `collectstatic` | `settings.py` añade `STATIC_ROOT` | **Parcial** |
| 15 | BROKEN_CMD | Carpeta `migrations/` inexistente | `Makefile` corre `makemigrations tienda` antes de `migrate` | **Fijado** |
| 16 | BROKEN_CMD | Subprocess llama `python3` en Windows | `views.py` usa `sys.executable` | **Fijado** |
| 17 | SILENT_FAIL | `None.lower()` crash en vistas | Fuera de alcance (bug de lógica en vistas) | **Fuera de alcance** |
| 18 | MISSING_DOC | Sin `.gitignore` | `.gitignore` creado | **Fijado** |
| 19 | BROKEN_CMD | `STATIC_ROOT` no configurado | `settings.py` añade `STATIC_ROOT` | **Fijado** |
| 20 | SILENT_FAIL | `", ".join()` sobre string en email | Fuera de alcance (bug de lógica en email) | **Fuera de alcance** |
| 21 | MISSING_DOC | Panel admin vacío | Fuera de alcance (feature, no infraestructura) | **Fuera de alcance** |
| 22 | SILENT_FAIL | Condición de carrera en scripts Excel | Fuera de alcance (bug arquitectural) | **Fuera de alcance** |

**Resumen:** 16 fijados · 2 parciales · 4 fuera de alcance

---

## What the AI Got Wrong

### Error 1: `docker-compose.yml` usó `DB_HOST: 127.0.0.1` para el contenedor web

**Borrador inicial generado:**
```yaml
web:
  env_file:
    - .env
  # (sin override de DB_HOST)
```

El `.env.example` define `DB_HOST=127.0.0.1` para desarrollo local. Cuando docker-compose carga ese `.env`, el contenedor `web` intentaba conectarse a `127.0.0.1` — que dentro del contenedor apunta al propio contenedor, no al servicio `db`. Resultado: `connection refused` al arrancar.

**Corrección manual:** Añadir un bloque `environment` en el servicio `web` que sobreescriba la variable después de cargar el `env_file`:
```yaml
web:
  env_file:
    - .env
  environment:
    DB_HOST: db    # override: en Docker el host es el nombre del servicio
```

**Lección:** Un AI no distingue automáticamente entre configuración de red de host y configuración de red de contenedor. Los `env_file` en docker-compose se cargan primero y los `environment` los sobreescriben — este orden de precedencia debe aplicarse manualmente.

---

### Error 2: El `Makefile` inicial usó `python3` en el target `run`

**Borrador inicial generado:**
```makefile
run:
    python3 manage.py runserver
```

Esto repite exactamente el bug #16 del PAIN_LOG: en Windows, `python3` no existe en el PATH por defecto. El Makefile que supuestamente debía resolver los problemas de configuración tenía el mismo defecto que el código original.

**Corrección manual:** Usar una variable configurable al inicio del Makefile:
```makefile
PYTHON := python
MANAGE := $(PYTHON) manage.py
```

Esto permite que cualquier desarrollador cambie el nombre del ejecutable una sola vez sin modificar cada target individualmente.

---

### Error 3: `.env.example` inicial omitió las variables de rutas de archivos

**Borrador inicial generado:** el `.env.example` solo incluía variables Django, DB y SMTP.

Al revisar `lanzar_factura.py` y `lanzar_albaran.py` se descubrió que los scripts necesitaban variables para las rutas de plantillas y directorios de salida:
- `PLANTILLA_FACTURAS`
- `PLANTILLA_ALBARANES`
- `FACTURAS_DIR`
- `ALBARANES_DIR`

Sin estas variables, los scripts modificados en el código habrían fallado con `FileNotFoundError` al no encontrar la plantilla en la ubicación por defecto calculada desde `PROJECT_ROOT`, especialmente cuando el archivo se ejecuta desde un working directory diferente.

**Corrección manual:** Revisar todos los archivos Python del proyecto buscando uso de rutas antes de finalizar el `.env.example`.

---

## Estructura final de archivos

```
simple_erp/
├── .env.example          ← NUEVO: documenta todas las variables
├── .gitignore            ← NUEVO: protege .env y outputs
├── Makefile              ← NUEVO: make setup | make run | make migrate
├── Dockerfile            ← NUEVO: Python 3.11 + libpq-dev
├── docker-compose.yml    ← NUEVO: db (postgres) + web (django)
├── GOLDEN_PATH.md        ← NUEVO: este archivo
├── PAIN_LOG.md           ← existente (Deliverable 1)
├── requirements.txt      ← MODIFICADO: +python-dotenv
├── gestor/
│   ├── settings.py       ← MODIFICADO: os.environ + STATIC_ROOT
│   ├── views.py          ← MODIFICADO: sys.executable + rutas dinámicas
│   ├── lanzar_factura.py ← MODIFICADO: PROJECT_ROOT + os.makedirs
│   └── lanzar_albaran.py ← MODIFICADO: PROJECT_ROOT + os.makedirs
└── 23AKP08PL_PLANTILLA.xlsx  ← existente (plantilla de facturas)
```
