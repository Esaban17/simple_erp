<p align="center">
  <img src="tienda/static/logo.png" alt="simple_erp logo" width="120">
</p>

<h1 align="center">simple_erp</h1>

<p align="center">
  ERP sencillo para gestión de pedidos y generación automática de documentos Excel (facturas y albaranes).
</p>

<p align="center">
  Python 3.11 · Django 4.2 · PostgreSQL 15 · Docker
</p>

---

## Inicio Rápido

### Opción A — Docker (recomendado, < 5 min)

No necesitas instalar Python ni PostgreSQL en tu máquina.

```bash
git clone <url-del-repo>
cd simple_erp
cp .env.example .env          # edita DB_PASSWORD y DJANGO_SECRET_KEY si lo deseas
docker compose up --build
```

Abre http://localhost:8000 y listo.

![Terminal mostrando docker compose up exitoso](image.png)

### Opción B — Local con Makefile

**Prerequisitos:** Python 3.11+, PostgreSQL instalado y corriendo, base de datos `tienda` creada.

```bash
git clone <url-del-repo>
cd simple_erp
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
make setup                    # instala deps + crea dirs + migra BD + crea superusuario
make run                      # inicia el servidor en http://127.0.0.1:8000
```

---

## Credenciales por defecto

| Usuario | Contraseña |
|---------|------------|
| `admin` | `admin`    |

Configurables en `.env` (variables `DJANGO_SUPERUSER_USERNAME` y `DJANGO_SUPERUSER_PASSWORD`).

---

## Comandos del Makefile

| Comando | Descripción |
|---------|-------------|
| `make setup` | Configuración completa desde cero (env + install + dirs + migrate + superuser) |
| `make run` | Inicia el servidor de desarrollo en `:8000` |
| `make migrate` | Genera migraciones y aplica al esquema de BD |
| `make dirs` | Crea directorios de salida: `facturas/` y `albaranes/` |
| `make superuser` | Crea superusuario automático desde `.env` (no interactivo) |
| `make clean` | Elimina archivos `.pyc` y `__pycache__` |
| `make help` | Muestra todos los comandos disponibles |

---

## Variables de Entorno

Copia `.env.example` a `.env` antes de arrancar. Las variables están organizadas en secciones:

| Sección | Variables clave | Descripción |
|---------|----------------|-------------|
| Django | `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` | Configuración principal de Django |
| PostgreSQL | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Conexión a la base de datos |
| Superusuario | `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD` | Credenciales del admin por defecto |
| SMTP | `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` | Envío de correo con facturas/albaranes |
| Rutas | `PLANTILLA_FACTURAS`, `PLANTILLA_ALBARANES`, `FACTURAS_DIR`, `ALBARANES_DIR` | Plantillas Excel y directorios de salida |

> **Nota Docker:** Dentro de Docker Compose, `DB_HOST` se sobreescribe automáticamente a `db` (nombre del servicio). No necesitas cambiarlo en `.env`.

---

## Estructura del Proyecto

```
simple_erp/
├── gestor/                    # Configuración del proyecto Django
│   ├── settings.py            # Variables de entorno con python-dotenv
│   ├── urls.py                # Rutas principales
│   ├── views.py               # Vistas de generación de Excel (subprocess)
│   ├── lanzar_factura.py      # Script de generación de facturas Excel
│   └── lanzar_albaran.py      # Script de generación de albaranes Excel
├── tienda/                    # App principal (tienda/store)
│   ├── models.py              # Modelos: Clientes, Productos, Pedidos, etc.
│   ├── views.py               # Vistas: pedidos, facturas, albaranes, clientes
│   ├── templates/             # Plantillas HTML
│   ├── static/                # CSS, logo, estilos
│   └── migrations/            # Migraciones de BD (se generan con make migrate)
├── docker-compose.yml         # Stack completo: PostgreSQL 15 + Django
├── Dockerfile                 # Python 3.11 + libpq-dev + gcc
├── Makefile                   # Automatización: setup, run, migrate, etc.
├── .env.example               # Plantilla de variables de entorno
├── requirements.txt           # Dependencias Python
├── 23AKP08PL_PLANTILLA.xlsx   # Plantilla Excel para facturas
└── 23AKP08_PLANTILLA.xlsx     # Plantilla Excel para albaranes
```

---

## Funcionalidades

- **Gestión de clientes** — Alta, edición y listado de clientes con datos fiscales, países, transportistas e incoterms.
- **Gestión de productos** — Catálogo con 3 niveles de precios y peso por unidad.
- **Pedidos** — Creación y seguimiento de pedidos por cliente.
- **Facturas Excel** — Generación automática de facturas en formato `.xlsx` desde plantilla.
- **Albaranes Excel** — Generación automática de albaranes (notas de entrega) en formato `.xlsx`.
- **Envío por correo** — Envío automático de documentos generados vía SMTP (requiere configuración en `.env`).

---

## Problemas Conocidos

| # | Descripción | Estado |
|---|-------------|--------|
| 17 | Navegar directamente a `/pedidos/`, `/facturas/` o `/albaranes/` sin `?id_cliente=` produce error 500 | Pendiente |
| 20 | `", ".join()` sobre un string en `lanzar_factura.py` corrompe el campo `To:` del correo | Pendiente |
| 21 | El panel de administración (`/admin/`) no tiene modelos registrados | Pendiente |
| 22 | Los scripts de factura y albarán comparten archivo temporal — posible condición de carrera | Pendiente |

