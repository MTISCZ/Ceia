from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import F, Count, Avg, Q
from django.db import connection
from datetime import date, datetime
from django.shortcuts import render

from .models import (
    Estudiantes, Atrasos, Productos, MovimientosStock,
    Apoderados, EstudianteApoderado, Usuarios,
)
from .serializers import (
    EstudianteSerializer, AtrasoSerializer,
    ProductoSerializer, MovimientoStockSerializer,
    ApoderadoSerializer, EstudianteApoderadoSerializer, UsuarioSerializer,
)


# =====================================================
# VISTA PARA EL FRONTEND
# =====================================================
def frontend(request):
    return render(request, 'index.html')


# =====================================================
# VIEWSETS DE LA API
# =====================================================

@method_decorator(csrf_exempt, name='dispatch')
class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiantes.objects.filter(activo=True)
    serializer_class = EstudianteSerializer
    
    @action(detail=False, methods=['get'])
    def buscar_por_rut(self, request):
        rut = request.query_params.get('rut')
        if rut:
            try:
                estudiante = self.queryset.get(rut=rut)
                serializer = self.get_serializer(estudiante)
                return Response(serializer.data)
            except Estudiantes.DoesNotExist:
                return Response({"error": "Estudiante no encontrado"}, status=404)
        return Response({"error": "Se requiere parámetro 'rut'"}, status=400)
    
    @action(detail=False, methods=['get'])
    def por_curso(self, request):
        curso = request.query_params.get('curso')
        if curso:
            estudiantes = self.queryset.filter(curso=curso)
            serializer = self.get_serializer(estudiantes, many=True)
            return Response(serializer.data)
        return Response({"error": "Se requiere parámetro 'curso'"}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class AtrasoViewSet(viewsets.ModelViewSet):
    queryset = Atrasos.objects.all()
    serializer_class = AtrasoSerializer
    
    @action(detail=False, methods=['post'])
    def registrar(self, request):
        id_estudiante = request.data.get('id_estudiante')
        minutos_atraso = request.data.get('minutos_atraso', 15)
        
        if not id_estudiante:
            return Response({"error": "Se requiere id_estudiante"}, status=400)
        
        hoy = date.today()
        hora_actual = datetime.now().time()
        
        # Verificar si ya tiene atraso hoy
        if Atrasos.objects.filter(id_estudiante_id=id_estudiante, fecha=hoy).exists():
            return Response({"error": "El estudiante ya tiene un atraso registrado hoy"}, status=400)
        
        # Crear atraso
        atraso = Atrasos.objects.create(
            id_estudiante_id=id_estudiante,
            fecha=hoy,
            hora=hora_actual,
            minutos_atraso=minutos_atraso
        )
        
        # Contar atrasos del mes
        atrasos_mes = Atrasos.objects.filter(
            id_estudiante_id=id_estudiante,
            fecha__month=hoy.month,
            justificado=False
        ).count()
        
        # Obtener email del apoderado
        try:
            estudiante = Estudiantes.objects.get(id_estudiante=id_estudiante)
            email_apoderado = estudiante.email_apoderado
        except Estudiantes.DoesNotExist:
            email_apoderado = None
        
        return Response({
            "mensaje": "Atraso registrado correctamente",
            "atraso": AtrasoSerializer(atraso).data,
            "atrasos_mes": atrasos_mes,
            "notificar_apoderado": atrasos_mes >= 4,
            "email_apoderado": email_apoderado if atrasos_mes >= 4 else None
        }, status=201)
    
    @action(detail=False, methods=['get'])
    def reporte_por_curso(self, request):
        """Reporte de atrasos agrupado por curso (compatible con SQLite)"""
        mes_actual = date.today().month
        
        resultados = []
        cursos = Estudiantes.objects.filter(activo=True).values('curso').distinct()
        
        for curso_data in cursos:
            curso_nombre = curso_data['curso']
            estudiantes = Estudiantes.objects.filter(curso=curso_nombre, activo=True)
            total_estudiantes = estudiantes.count()
            
            atrasos = Atrasos.objects.filter(
                id_estudiante__in=estudiantes,
                fecha__month=mes_actual
            )
            total_atrasos = atrasos.count()
            
            promedio = atrasos.aggregate(promedio=Avg('minutos_atraso'))['promedio'] or 0
            
            resultados.append({
                'curso': curso_nombre,
                'total_estudiantes': total_estudiantes,
                'total_atrasos': total_atrasos,
                'promedio_minutos': round(promedio, 0)
            })
        
        return Response(resultados)


@method_decorator(csrf_exempt, name='dispatch')
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Productos.objects.filter(activo=True)
    serializer_class = ProductoSerializer
    
    @action(detail=False, methods=['get'])
    def stock_critico(self, request):
        productos_criticos = self.queryset.filter(stock_actual__lte=F('stock_minimo'))
        serializer = self.get_serializer(productos_criticos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def buscar_por_qr(self, request):
        codigo_qr = request.query_params.get('codigo_qr')
        if codigo_qr:
            try:
                producto = self.queryset.get(codigo_qr=codigo_qr)
                serializer = self.get_serializer(producto)
                return Response(serializer.data)
            except Productos.DoesNotExist:
                return Response({"error": "Producto no encontrado"}, status=404)
        return Response({"error": "Se requiere parámetro 'codigo_qr'"}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class MovimientoStockViewSet(viewsets.ModelViewSet):
    queryset = MovimientosStock.objects.all()
    serializer_class = MovimientoStockSerializer
    
    @action(detail=False, methods=['post'])
    def subir_stock(self, request):
        id_producto = request.data.get('id_producto')
        cantidad = request.data.get('cantidad')
        usuario = request.data.get('usuario_responsable', 'sistema')
        
        if not id_producto or not cantidad:
            return Response({"error": "Se requiere id_producto y cantidad"}, status=400)
        
        try:
            producto = Productos.objects.get(id_producto=id_producto)
            stock_antes = producto.stock_actual
            producto.stock_actual += int(cantidad)
            producto.save()
            
            MovimientosStock.objects.create(
                id_producto_id=id_producto,
                tipo_movimiento='INGRESO',
                cantidad=cantidad,
                stock_antes=stock_antes,
                stock_despues=producto.stock_actual,
                usuario_responsable=usuario
            )
            
            return Response({
                "mensaje": "Stock actualizado correctamente",
                "producto": producto.nombre,
                "stock_anterior": stock_antes,
                "stock_actual": producto.stock_actual
            })
        except Productos.DoesNotExist:
            return Response({"error": "Producto no encontrado"}, status=404)
    
    @action(detail=False, methods=['post'])
    def bajar_stock(self, request):
        id_producto = request.data.get('id_producto')
        cantidad = request.data.get('cantidad')
        usuario = request.data.get('usuario_responsable', 'sistema')
        
        if not id_producto or not cantidad:
            return Response({"error": "Se requiere id_producto y cantidad"}, status=400)
        
        try:
            producto = Productos.objects.get(id_producto=id_producto)
            
            if producto.stock_actual < int(cantidad):
                return Response({
                    "error": f"Stock insuficiente. Stock actual: {producto.stock_actual}"
                }, status=400)
            
            stock_antes = producto.stock_actual
            producto.stock_actual -= int(cantidad)
            producto.save()
            
            MovimientosStock.objects.create(
                id_producto_id=id_producto,
                tipo_movimiento='DESPACHO',
                cantidad=cantidad,
                stock_antes=stock_antes,
                stock_despues=producto.stock_actual,
                usuario_responsable=usuario
            )
            
            return Response({
                "mensaje": "Stock actualizado correctamente",
                "producto": producto.nombre,
                "stock_anterior": stock_antes,
                "stock_actual": producto.stock_actual
            })
        except Productos.DoesNotExist:
            return Response({"error": "Producto no encontrado"}, status=404)

# =====================================================
# MODULO DE APODERADOS (nuevo en EPE 2)
# =====================================================

@method_decorator(csrf_exempt, name='dispatch')
class ApoderadoViewSet(viewsets.ModelViewSet):
    """CRUD de apoderados. Pendiente identificado en EPE 1, implementado en EPE 2."""
    queryset = Apoderados.objects.all()
    serializer_class = ApoderadoSerializer

    @action(detail=False, methods=['get'])
    def buscar_por_rut(self, request):
        rut = request.query_params.get('rut')
        if not rut:
            return Response({"error": "Se requiere parametro 'rut'"}, status=400)
        try:
            apoderado = self.queryset.get(rut=rut)
            return Response(self.get_serializer(apoderado).data)
        except Apoderados.DoesNotExist:
            return Response({"error": "Apoderado no encontrado"}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class EstudianteApoderadoViewSet(viewsets.ModelViewSet):
    """Relacion estudiante-apoderado (muchos a muchos)."""
    queryset = EstudianteApoderado.objects.select_related('id_apoderado', 'id_estudiante')
    serializer_class = EstudianteApoderadoSerializer

    @action(detail=False, methods=['get'])
    def por_estudiante(self, request):
        id_estudiante = request.query_params.get('id_estudiante')
        if not id_estudiante:
            return Response({"error": "Se requiere parametro 'id_estudiante'"}, status=400)
        relaciones = self.queryset.filter(id_estudiante_id=id_estudiante)
        return Response(self.get_serializer(relaciones, many=True).data)


# =====================================================
# AUTENTICACION BASICA (nuevo en EPE 2)
# =====================================================

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    Autenticacion simple contra la tabla Usuarios (independiente del sistema
    de auth de Django). Compara la contrasena recibida contra el hash
    guardado en password_hash usando los hashers estandar de Django.
    No genera sesion de servidor: el frontend guarda el usuario devuelto
    en memoria durante la sesion de navegacion.
    """
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Se requieren 'email' y 'password'"}, status=400)

        try:
            usuario = Usuarios.objects.get(email=email, activo=True)
        except Usuarios.DoesNotExist:
            return Response({"error": "Credenciales invalidas"}, status=401)

        if not check_password(password, usuario.password_hash):
            return Response({"error": "Credenciales invalidas"}, status=401)

        return Response({
            "mensaje": "Sesion iniciada correctamente",
            "usuario": UsuarioSerializer(usuario).data,
        })


@method_decorator(csrf_exempt, name='dispatch')
class CambiarPasswordView(APIView):
    """Utilidad para fijar/actualizar el password_hash de un usuario existente."""
    def post(self, request):
        email = request.data.get('email')
        password_nuevo = request.data.get('password')
        if not email or not password_nuevo:
            return Response({"error": "Se requieren 'email' y 'password'"}, status=400)
        try:
            usuario = Usuarios.objects.get(email=email)
        except Usuarios.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=404)
        usuario.password_hash = make_password(password_nuevo)
        usuario.save()
        return Response({"mensaje": "Contrasena actualizada correctamente"})
