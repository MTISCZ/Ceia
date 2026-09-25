from django.test import TestCase
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from .models import Estudiantes, Productos, Usuarios, Apoderados, EstudianteApoderado


class EstudianteAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.estudiante = Estudiantes.objects.create(
            rut='12345678-9', nombre='Carlos',
            apellido_paterno='González', curso='4° Medio A',
            email_apoderado='maria.gonzalez@email.com'
        )

    def test_listar_estudiantes(self):
        response = self.client.get('/api/estudiantes/')
        self.assertEqual(response.status_code, 200)

    def test_buscar_por_rut(self):
        url = '/api/estudiantes/buscar_por_rut/?rut=12345678-9'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nombre'], 'Carlos')


class AtrasoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.estudiante = Estudiantes.objects.create(
            rut='87654321-K', nombre='Ana',
            apellido_paterno='Martínez', curso='4° Medio A',
            email_apoderado='pedro.martinez@email.com'
        )

    def test_registrar_atraso(self):
        data = {'id_estudiante': self.estudiante.id_estudiante,
                'minutos_atraso': 15}
        response = self.client.post('/api/atrasos/registrar/', data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('atrasos_mes', response.data)

    def test_no_permite_atraso_duplicado(self):
        data = {'id_estudiante': self.estudiante.id_estudiante}
        self.client.post('/api/atrasos/registrar/', data)
        response = self.client.post('/api/atrasos/registrar/', data)
        self.assertEqual(response.status_code, 400)


class ProductoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        Productos.objects.create(
            codigo_qr='QR003', nombre='Carpetas',
            stock_actual=32, stock_minimo=10
        )

    def test_stock_critico_vacio(self):
        response = self.client.get('/api/productos/stock_critico/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

class LoginAPITestCase(TestCase):
    """Pruebas del modulo de autenticacion basica (nuevo en EPE 2)."""

    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuarios.objects.create(
            email='director@ceia.cl',
            password_hash=make_password('clave123'),
            nombre_completo='Claudia Zuniga',
            rol='director',
        )

    def test_login_credenciales_correctas(self):
        response = self.client.post('/api/login/', {
            'email': 'director@ceia.cl', 'password': 'clave123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['usuario']['email'], 'director@ceia.cl')
        # el hash nunca debe viajar en la respuesta
        self.assertNotIn('password_hash', response.data['usuario'])

    def test_login_password_incorrecta(self):
        response = self.client.post('/api/login/', {
            'email': 'director@ceia.cl', 'password': 'incorrecta'
        })
        self.assertEqual(response.status_code, 401)

    def test_login_usuario_inexistente(self):
        response = self.client.post('/api/login/', {
            'email': 'no-existe@ceia.cl', 'password': 'clave123'
        })
        self.assertEqual(response.status_code, 401)

    def test_login_usuario_inactivo(self):
        self.usuario.activo = False
        self.usuario.save()
        response = self.client.post('/api/login/', {
            'email': 'director@ceia.cl', 'password': 'clave123'
        })
        self.assertEqual(response.status_code, 401)

    def test_login_campos_faltantes(self):
        response = self.client.post('/api/login/', {'email': 'director@ceia.cl'})
        self.assertEqual(response.status_code, 400)


class ApoderadoAPITestCase(TestCase):
    """Pruebas del modulo de Apoderados (pendiente de EPE 1, resuelto en EPE 2)."""

    def setUp(self):
        self.client = APIClient()
        self.estudiante = Estudiantes.objects.create(
            rut='12345678-9', nombre='Carlos', apellido_paterno='Gonzalez',
            curso='4 Medio A', email_apoderado='maria.gonzalez@email.com'
        )
        self.apoderado = Apoderados.objects.create(
            rut='11222333-4', nombre_completo='Maria Gonzalez',
            telefono='+56911112222', email='maria.gonzalez@email.com'
        )

    def test_listar_apoderados(self):
        response = self.client.get('/api/apoderados/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_buscar_apoderado_por_rut(self):
        response = self.client.get('/api/apoderados/buscar_por_rut/?rut=11222333-4')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['nombre_completo'], 'Maria Gonzalez')

    def test_buscar_apoderado_rut_inexistente(self):
        response = self.client.get('/api/apoderados/buscar_por_rut/?rut=0-0')
        self.assertEqual(response.status_code, 404)

    def test_crear_relacion_estudiante_apoderado(self):
        EstudianteApoderado.objects.create(
            id_estudiante=self.estudiante, id_apoderado=self.apoderado, es_principal=True
        )
        response = self.client.get(
            '/api/estudiante-apoderado/por_estudiante/?id_estudiante=' + str(self.estudiante.id_estudiante)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['apoderado_nombre'], 'Maria Gonzalez')


class ReporteAPITestCase(TestCase):
    """
    Pruebas del reporte de atrasos por curso (EPE 3: antes sin cobertura de
    pruebas). Verifica el resultado agregado y que la version optimizada
    (una query por tabla, sin N+1) siga entregando los mismos datos.
    """

    def setUp(self):
        from datetime import date
        from .models import Atrasos

        self.client = APIClient()
        self.hoy = date.today()

        self.e1 = Estudiantes.objects.create(
            rut='20000000-1', nombre='Sofia', apellido_paterno='Rojas',
            curso='1 Medio A', email_apoderado='a@a.cl'
        )
        self.e2 = Estudiantes.objects.create(
            rut='20000000-2', nombre='Tomas', apellido_paterno='Diaz',
            curso='1 Medio A', email_apoderado='b@b.cl'
        )
        self.e3 = Estudiantes.objects.create(
            rut='20000000-3', nombre='Valentina', apellido_paterno='Soto',
            curso='2 Medio B', email_apoderado='c@c.cl'
        )

        Atrasos.objects.create(id_estudiante=self.e1, fecha=self.hoy, hora='08:10:00', minutos_atraso=10)
        Atrasos.objects.create(id_estudiante=self.e2, fecha=self.hoy, hora='08:20:00', minutos_atraso=20)
        # e3 (2 Medio B) no tiene atrasos este mes -> debe aparecer con 0, no desaparecer del reporte

    def test_reporte_agrupa_por_curso_correctamente(self):
        response = self.client.get('/api/atrasos/reporte_por_curso/')
        self.assertEqual(response.status_code, 200)

        por_curso = {fila['curso']: fila for fila in response.data}

        self.assertEqual(por_curso['1 Medio A']['total_estudiantes'], 2)
        self.assertEqual(por_curso['1 Medio A']['total_atrasos'], 2)
        self.assertEqual(por_curso['1 Medio A']['promedio_minutos'], 15)

        self.assertEqual(por_curso['2 Medio B']['total_estudiantes'], 1)
        self.assertEqual(por_curso['2 Medio B']['total_atrasos'], 0)
        self.assertEqual(por_curso['2 Medio B']['promedio_minutos'], 0)

    def test_reporte_usa_numero_constante_de_queries(self):
        # Regresion: la version original hacia 1 query de conteo + 1 de
        # atrasos POR CADA curso (N+1). Con 2 cursos deberia usar solo 2
        # queries agregadas en total, sin importar cuantos cursos existan.
        with self.assertNumQueries(2):
            self.client.get('/api/atrasos/reporte_por_curso/')


class IntegracionFrontBackDBTestCase(TestCase):
    """
    Pruebas de integracion de extremo a extremo: simulan el flujo que realiza
    la interfaz (index.html) contra la API y verifican que la base de datos
    quede sincronizada con lo que se ve reflejado en la respuesta JSON.
    """

    def setUp(self):
        self.client = APIClient()
        self.estudiante = Estudiantes.objects.create(
            rut='19999999-1', nombre='Diego', apellido_paterno='Fuentes',
            curso='2 Medio C', email_apoderado='paula.fuentes@email.com'
        )
        self.producto = Productos.objects.create(
            codigo_qr='QR-TEST', nombre='Resmas de papel',
            stock_actual=12, stock_minimo=15
        )

    def test_flujo_completo_atraso_y_notificacion(self):
        # Se registran 4 atrasos en distintos dias -> el 4to debe marcar
        # notificar_apoderado = True, igual que exige la logica de negocio.
        from datetime import date, timedelta
        from .models import Atrasos

        base = date.today()
        for i in range(3):
            Atrasos.objects.create(
                id_estudiante=self.estudiante,
                fecha=base - timedelta(days=i + 1),
                hora='08:30:00',
                minutos_atraso=10,
            )

        response = self.client.post('/api/atrasos/registrar/', {
            'id_estudiante': self.estudiante.id_estudiante,
            'minutos_atraso': 20,
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['atrasos_mes'], 4)
        self.assertTrue(response.data['notificar_apoderado'])
        self.assertEqual(response.data['email_apoderado'], 'paula.fuentes@email.com')

        # La base de datos debe reflejar el nuevo total
        self.assertEqual(self.estudiante.atrasos_set.count(), 4)

    def test_flujo_completo_stock_critico_y_reposicion(self):
        # Producto bajo el minimo debe aparecer en stock_critico...
        response = self.client.get('/api/productos/stock_critico/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # ...y al reponer stock por sobre el minimo, debe desaparecer del listado.
        response = self.client.post('/api/movimientos/subir_stock/', {
            'id_producto': self.producto.id_producto,
            'cantidad': 10,
            'usuario_responsable': 'test-integracion',
        })
        self.assertEqual(response.status_code, 200)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock_actual, 22)

        response = self.client.get('/api/productos/stock_critico/')
        self.assertEqual(len(response.data), 0)
