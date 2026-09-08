# CEIA La Pintana — Sistema de Gestión Escolar

Proyecto de la asignatura de Desarrollo Full Stack (IPCHILE), desarrollado para el
socio comunitario **CEIA La Pintana**. Entrega correspondiente a **EPE 2 (Anexo 2)**:
aplicación web funcional que integra frontend, backend y base de datos.

## Integrantes

- [Matias correa]

## Stack técnico

- **Backend:** Django 6 + Django REST Framework
- **Base de datos:** SQLite (desarrollo)
- **Frontend:** HTML5 + CSS3 + JavaScript vanilla (sin frameworks), servido directamente por Django
- **Autenticación:** propia, contra tabla `Usuarios`, con contraseñas hasheadas (`django.contrib.auth.hashers`)

## Estructura del repositorio

```
CEIA_Project/
├── ceia_backend/           # Configuración del proyecto Django (settings, urls, wsgi/asgi)
├── gestion/                # App principal
│   ├── models.py           # 8 modelos: Estudiantes, Apoderados, EstudianteApoderado,
│   │                       #   Atrasos, Productos, MovimientosStock, Usuarios, Bitacora
│   ├── serializers.py      # Serializadores DRF (uno por modelo)
│   ├── views.py            # ViewSets + acciones de negocio (registrar atraso, stock crítico, etc.)
│   ├── admin.py
│   ├── tests.py            # 16 pruebas automatizadas (unitarias + integración E2E)
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py   # Carga datos de ejemplo (cursos, estudiantes, apoderados, atrasos, inventario)
│   ├── static/gestion/
│   │   ├── css/estilos.css    # Todo el CSS del proyecto (separado del HTML)
│   │   └── js/                # Un módulo JS por responsabilidad (api.js, tabs.js, auth.js, etc.)
│   └── templates/
│       └── index.html         # Única plantilla; solo estructura, sin CSS/JS embebido
├── docs/
│   ├── Informe_Avance_Tecnico_EPE2_CEIA.docx   # Informe de avance técnico (Anexo 2)
│   └── evidencias/                              # Capturas de pantalla de la app funcionando
├── requirements.txt
├── manage.py
└── .gitignore
```

## Cómo ejecutar el proyecto

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Aplicar migraciones (crea las tablas en SQLite)
python manage.py migrate

# 4. Cargar datos de ejemplo (cursos, estudiantes, apoderados, atrasos, inventario)
python manage.py seed_data

# 5. Levantar el servidor
python manage.py runserver
```

Abrir **http://127.0.0.1:8000/** en el navegador.

**Usuario de prueba** (creado por `seed_data`):

| Rol      | Email               | Contraseña |
|----------|---------------------|------------|
| director | director@ceia.cl    | clave123   |

## Pruebas automatizadas

```bash
python manage.py test gestion
```

Resultado esperado: `Ran 16 tests ... OK` (16/16 exitosas). Cubre estudiantes, atrasos
(incluyendo la regla de notificación al 4° atraso), inventario, apoderados, login y dos
pruebas de integración de extremo a extremo (frontend → API → base de datos).

## Endpoints principales de la API

| Método | Endpoint | Descripción |
|---|---|---|
| GET  | `/api/estudiantes/` | Listado de estudiantes |
| GET  | `/api/estudiantes/buscar_por_rut/?rut=` | Búsqueda por RUT |
| POST | `/api/atrasos/registrar/` | Registra atraso; valida duplicado y evalúa aviso al 4° atraso del mes |
| GET  | `/api/atrasos/reporte_por_curso/` | Reporte agregado de atrasos por curso |
| GET  | `/api/productos/stock_critico/` | Productos bajo su stock mínimo |
| POST | `/api/movimientos/subir_stock/` / `bajar_stock/` | Ingreso/despacho de inventario |
| GET  | `/api/apoderados/` | Listado de apoderados |
| POST | `/api/login/` | Autenticación contra la tabla `Usuarios` |

## Documentación de la entrega

El informe de avance técnico (`docs/Informe_Avance_Tecnico_EPE2_CEIA.docx`) documenta,
según los pasos del Anexo 2:

1. Desarrollo de componentes (modelos, serializadores, vistas, separación HTML/CSS/JS)
2. Integración Front-End y Back-End
3. Integración con la base de datos
4. Funcionalidades implementadas en esta etapa
5. Evidencias de implementación (capturas de la app funcionando)
6. Pruebas realizadas, errores detectados/corregidos y mejoras pendientes

## Licencia / Contexto académico

Proyecto desarrollado con fines académicos para IPCHILE, en colaboración con el
socio comunitario CEIA La Pintana, en el marco de Vinculación con el Medio (VCM).
