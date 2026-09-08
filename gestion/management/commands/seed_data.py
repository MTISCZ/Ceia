"""
Comando de datos de ejemplo para el proyecto CEIA La Pintana.

Uso:
    python manage.py seed_data            -> agrega datos (no borra lo existente)
    python manage.py seed_data --flush     -> borra todo y vuelve a crear desde cero

Crea, en este orden (respetando las llaves foráneas):
    1. Cursos (como valores del campo Estudiantes.curso)
    2. Estudiantes distribuidos en esos cursos
    3. Apoderados y su relación con los estudiantes (EstudianteApoderado)
    4. Atrasos del mes actual, incluyendo algunos estudiantes con 4+ atrasos
       para poder probar la alerta de notificación al apoderado
    5. Productos de inventario, algunos bajo el stock mínimo (stock crítico)
    6. Movimientos de stock (ingresos) que dejan trazabilidad en MovimientosStock
    7. Un usuario de prueba para el login (director@ceia.cl / clave123)

Pensado para dejar la app en un estado con el que se puedan probar TODAS
las pestañas del prototipo (Estudiantes, Atrasos, Inventario, Apoderados,
Reportes) y para usarlo como evidencia de integración BD <-> API <-> Frontend
en el informe de avance de EPE2.
"""
import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import transaction

from gestion.models import (
    Estudiantes, Apoderados, EstudianteApoderado,
    Atrasos, Productos, MovimientosStock, Usuarios, Bitacora,
)

CURSOS = [
    "1° Básico A", "1° Básico B",
    "5° Básico A",
    "7° Básico A",
    "1° Medio A",
    "2° Medio A",
    "3° Medio A",
    "4° Medio A",
]

NOMBRES = [
    "Camila", "Matías", "Valentina", "Benjamín", "Isidora", "Vicente",
    "Antonia", "Joaquín", "Martina", "Agustín", "Florencia", "Diego",
    "Constanza", "Tomás", "Javiera", "Sebastián", "Fernanda", "Nicolás",
    "Catalina", "Ignacio", "Josefa", "Cristóbal", "Emilia", "Maximiliano",
]

APELLIDOS = [
    "González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", "Contreras",
    "Silva", "Martínez", "Sepúlveda", "Morales", "Rodríguez", "López",
    "Fuentes", "Hernández", "Torres", "Araya", "Flores", "Espinoza", "Reyes",
]


_TILDES = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")


def sin_tildes(texto):
    return texto.translate(_TILDES)


def rut_valido(numero):
    """Genera un RUT chileno con dígito verificador correcto a partir de un número base."""
    suma = 0
    multiplicador = 2
    for digito in reversed(str(numero)):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1
    resto = 11 - (suma % 11)
    if resto == 11:
        dv = "0"
    elif resto == 10:
        dv = "K"
    else:
        dv = str(resto)
    return f"{numero}-{dv}"


class Command(BaseCommand):
    help = "Carga cursos, estudiantes, apoderados, atrasos, inventario y un usuario de prueba."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true",
            help="Borra todos los datos de negocio antes de crear los nuevos.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Borrando datos existentes...")
            MovimientosStock.objects.all().delete()
            Atrasos.objects.all().delete()
            EstudianteApoderado.objects.all().delete()
            Productos.objects.all().delete()
            Estudiantes.objects.all().delete()
            Apoderados.objects.all().delete()
            Bitacora.objects.all().delete()

        rut_base = 10000000
        estudiantes_creados = []
        apoderados_creados = []

        # 1 y 2: cursos + estudiantes -----------------------------------
        for curso in CURSOS:
            n_estudiantes = random.randint(4, 6)
            for _ in range(n_estudiantes):
                rut_base += random.randint(3, 11)
                rut_est = rut_valido(rut_base)
                if Estudiantes.objects.filter(rut=rut_est).exists():
                    continue

                nombre = random.choice(NOMBRES)
                ap_pat = random.choice(APELLIDOS)
                ap_mat = random.choice(APELLIDOS)

                rut_base += random.randint(3, 11)
                rut_apod = rut_valido(rut_base)
                email_apoderado = f"{sin_tildes(nombre).lower()}.{sin_tildes(ap_pat).lower()}@correo.cl"

                apoderado, _ = Apoderados.objects.get_or_create(
                    rut=rut_apod,
                    defaults=dict(
                        nombre_completo=f"{random.choice(NOMBRES)} {ap_pat}",
                        telefono=f"+569{random.randint(10000000, 99999999)}",
                        email=email_apoderado,
                        parentesco=random.choice(["Madre", "Padre", "Tutor/a", "Abuela", "Abuelo"]),
                    ),
                )
                apoderados_creados.append(apoderado)

                estudiante = Estudiantes.objects.create(
                    rut=rut_est,
                    nombre=nombre,
                    apellido_paterno=ap_pat,
                    apellido_materno=ap_mat,
                    curso=curso,
                    email_apoderado=email_apoderado,
                    telefono=f"+569{random.randint(10000000, 99999999)}",
                    activo=True,
                )
                estudiantes_creados.append(estudiante)

                # 3: relación estudiante-apoderado
                EstudianteApoderado.objects.get_or_create(
                    id_estudiante=estudiante, id_apoderado=apoderado,
                    defaults={"es_principal": True},
                )

        self.stdout.write(self.style.SUCCESS(
            f"Creados {len(estudiantes_creados)} estudiantes en {len(CURSOS)} cursos."
        ))
        self.stdout.write(self.style.SUCCESS(
            f"Creados {len(apoderados_creados)} apoderados."
        ))

        # 4: atrasos del mes actual ---------------------------------------
        hoy = date.today()
        total_atrasos = 0
        # Un grupo de estudiantes con muchos atrasos (para gatillar alerta al 4°)
        estudiantes_con_atrasos = random.sample(
            estudiantes_creados, k=max(1, len(estudiantes_creados) // 2)
        )
        for i, estudiante in enumerate(estudiantes_con_atrasos):
            # Un tercio de ellos queda con 4 o 5 atrasos para probar la alerta
            n_atrasos = random.randint(4, 5) if i % 3 == 0 else random.randint(1, 3)
            dias_usados = set()
            for _ in range(n_atrasos):
                intentos = 0
                while intentos < 10:
                    dia_offset = random.randint(0, min(27, hoy.day - 1) or 1)
                    fecha_atraso = hoy - timedelta(days=dia_offset)
                    if fecha_atraso.month == hoy.month and fecha_atraso not in dias_usados:
                        dias_usados.add(fecha_atraso)
                        break
                    intentos += 1
                else:
                    continue
                Atrasos.objects.get_or_create(
                    id_estudiante=estudiante,
                    fecha=fecha_atraso,
                    defaults=dict(
                        hora=f"{random.randint(8, 9):02d}:{random.randint(0, 59):02d}:00",
                        minutos_atraso=random.choice([5, 10, 15, 20, 30]),
                        justificado=random.random() < 0.2,
                    ),
                )
                total_atrasos += 1

        self.stdout.write(self.style.SUCCESS(f"Creados {total_atrasos} registros de atraso."))

        # 5 y 6: inventario -------------------------------------------------
        productos_data = [
            ("QR-CUAD-001", "Cuadernos universitarios", 45, 20, "Bodega A - Estante 1"),
            ("QR-LAP-002", "Lápices grafito caja x12", 8, 15, "Bodega A - Estante 2"),
            ("QR-CARP-003", "Carpetas plásticas", 60, 25, "Bodega A - Estante 1"),
            ("QR-COLA-004", "Colaciones de emergencia", 12, 20, "Bodega B - Refrigerado"),
            ("QR-UTIL-005", "Kits de útiles escolares", 5, 10, "Bodega A - Estante 3"),
            ("QR-HIG-006", "Kits de higiene personal", 30, 15, "Bodega B - Estante 1"),
            ("QR-RESM-007", "Resmas de papel carta", 18, 20, "Bodega A - Estante 4"),
            ("QR-BOT-008", "Botellas de agua reutilizables", 22, 10, "Bodega B - Estante 2"),
        ]
        productos_creados = []
        for codigo, nombre, stock_actual, stock_minimo, ubicacion in productos_data:
            producto, created = Productos.objects.get_or_create(
                codigo_qr=codigo,
                defaults=dict(
                    nombre=nombre, stock_actual=stock_actual,
                    stock_minimo=stock_minimo, ubicacion=ubicacion, activo=True,
                ),
            )
            productos_creados.append(producto)
            if created:
                MovimientosStock.objects.create(
                    id_producto=producto, tipo_movimiento="INGRESO",
                    cantidad=stock_actual, stock_antes=0, stock_despues=stock_actual,
                    usuario_responsable="seed_data",
                )

        self.stdout.write(self.style.SUCCESS(f"Creados/actualizados {len(productos_creados)} productos."))

        # 7: usuario de prueba -----------------------------------------------
        usuario, created = Usuarios.objects.get_or_create(
            email="director@ceia.cl",
            defaults=dict(
                password_hash=make_password("clave123"),
                nombre_completo="Dirección CEIA La Pintana",
                rol="director",
                activo=True,
            ),
        )
        if created:
            self.stdout.write(self.style.SUCCESS(
                "Usuario de prueba creado -> email: director@ceia.cl / clave: clave123"
            ))
        else:
            self.stdout.write("Usuario director@ceia.cl ya existía, no se modificó.")

        Bitacora.objects.create(
            usuario_email="sistema",
            accion="SEED_DATA",
            tabla_afectada="Estudiantes/Apoderados/Atrasos/Productos",
            detalles=f"Carga de datos de ejemplo: {len(estudiantes_creados)} estudiantes, "
                     f"{len(apoderados_creados)} apoderados, {total_atrasos} atrasos, "
                     f"{len(productos_creados)} productos.",
        )

        self.stdout.write(self.style.SUCCESS("Datos de ejemplo cargados correctamente."))
