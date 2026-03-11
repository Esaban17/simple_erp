# =============================================================
# simple_erp — Makefile de configuración y desarrollo
# =============================================================
# Uso rápido:
#   make setup     — Configuración completa desde cero (desarrollo local)
#   make help      — Ver todos los comandos disponibles
#
# Resuelve PAIN_LOG: #1, #5, #8, #9, #11, #15
# =============================================================

# Configurable: cambia a 'python3' si tu sistema requiere ese nombre
# (Resuelve PAIN_LOG #16 — el primer borrador de IA usó 'python3' aquí,
#  ver GOLDEN_PATH.md sección "What the AI Got Wrong")
PYTHON := python
MANAGE := $(PYTHON) manage.py

.PHONY: help setup env venv install dirs makemigrations migrate superuser superuser-auto run clean

# Muestra ayuda por defecto al ejecutar 'make' sin argumentos
help:
	@echo ""
	@echo "simple_erp — Comandos disponibles"
	@echo "=================================="
	@echo ""
	@echo "  make setup        Configuración completa desde cero"
	@echo "                    (env + install + dirs + migrate + superuser)"
	@echo ""
	@echo "  make env           Copia .env.example a .env (no sobreescribe)"
	@echo "  make install       Instala dependencias Python de requirements.txt"
	@echo "  make dirs          Crea directorios de salida: facturas/ albaranes/"
	@echo "  make migrate       Genera migraciones y aplica al esquema de BD"
	@echo "  make superuser     Crea superusuario automático desde .env (no interactivo)"
	@echo "  make superuser-interactive  Crea superusuario de forma interactiva"
	@echo "  make run           Inicia el servidor de desarrollo en :8000"
	@echo "  make clean         Elimina archivos .pyc y __pycache__"
	@echo ""
	@echo "  Para Docker: docker compose up --build"
	@echo ""

# Target principal — ejecuta todo en el orden correcto, sin interacción
setup: env install dirs migrate superuser
	@echo ""
	@echo "✓ Configuración completa."
	@echo "  Usuario: $$(grep DJANGO_SUPERUSER_USERNAME .env | cut -d= -f2)"
	@echo "  Clave:   $$(grep DJANGO_SUPERUSER_PASSWORD .env | cut -d= -f2)"
	@echo "  Ejecuta 'make run' para iniciar el servidor en http://127.0.0.1:8000"
	@echo ""

# Copia .env.example → .env si no existe ya
env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ .env creado. Edítalo con tus credenciales reales antes de continuar."; \
	else \
		echo "ℹ  .env ya existe, no se sobreescribió."; \
	fi

# Instala dependencias Python
install:
	$(PYTHON) -m pip install --upgrade pip
	pip install -r requirements.txt
	@echo "✓ Dependencias instaladas."

# Crea los directorios de salida para Excel — resuelve PAIN_LOG #11
dirs:
	mkdir -p facturas albaranes
	@echo "✓ Directorios facturas/ y albaranes/ creados."

# Genera el archivo de migración inicial para la app tienda — resuelve PAIN_LOG #15
# (sin este paso, 'migrate' solo crea las tablas internas de Django)
makemigrations:
	$(MANAGE) makemigrations tienda
	@echo "✓ Migraciones generadas."

# Genera migraciones Y las aplica — resuelve PAIN_LOG #8 y #15
migrate:
	$(MANAGE) makemigrations tienda
	$(MANAGE) migrate
	@echo "✓ Base de datos migrada."

# Crea superusuario automáticamente usando variables del .env — resuelve PAIN_LOG #9
# No requiere interacción. Credenciales en: DJANGO_SUPERUSER_USERNAME / PASSWORD
superuser:
	$(MANAGE) create_default_superuser

# Versión interactiva para quienes prefieren ingresar sus propias credenciales
superuser-interactive:
	$(MANAGE) createsuperuser

# Inicia el servidor de desarrollo
run:
	$(MANAGE) runserver

# Limpia archivos compilados de Python
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Archivos compilados eliminados."
