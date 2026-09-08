from rest_framework import serializers
from .models import Estudiantes, Atrasos, Productos, MovimientosStock, Apoderados, EstudianteApoderado, Usuarios

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiantes
        fields = '__all__'


class ApoderadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apoderados
        fields = '__all__'


class EstudianteApoderadoSerializer(serializers.ModelSerializer):
    # Muestra datos legibles del apoderado además del id, útil para listar
    # los apoderados asociados a un estudiante sin una segunda consulta.
    apoderado_nombre = serializers.CharField(source='id_apoderado.nombre_completo', read_only=True)
    apoderado_telefono = serializers.CharField(source='id_apoderado.telefono', read_only=True)
    apoderado_email = serializers.CharField(source='id_apoderado.email', read_only=True)

    class Meta:
        model = EstudianteApoderado
        fields = ['id', 'id_estudiante', 'id_apoderado', 'es_principal',
                   'apoderado_nombre', 'apoderado_telefono', 'apoderado_email']


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        # password_hash nunca se expone en las respuestas de la API
        fields = ['id_usuario', 'email', 'nombre_completo', 'rol', 'activo']

class AtrasoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atrasos
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Productos
        fields = '__all__'

class MovimientoStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientosStock
        fields = '__all__'