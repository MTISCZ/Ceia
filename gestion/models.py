from django.db import models

class Estudiantes(models.Model):
    id_estudiante = models.AutoField(primary_key=True)  # INT IDENTITY
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50, blank=True, null=True)
    curso = models.CharField(max_length=20)
    email_apoderado = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Estudiantes'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno}"


class Apoderados(models.Model):
    id_apoderado = models.AutoField(primary_key=True)
    rut = models.CharField(max_length=12, unique=True)
    nombre_completo = models.CharField(max_length=150)
    telefono = models.CharField(max_length=15)
    email = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'Apoderados'
    
    def __str__(self):
        return self.nombre_completo


class EstudianteApoderado(models.Model):
    id_estudiante = models.ForeignKey(Estudiantes, on_delete=models.CASCADE, db_column='id_estudiante')
    id_apoderado = models.ForeignKey(Apoderados, on_delete=models.CASCADE, db_column='id_apoderado')
    es_principal = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'EstudianteApoderado'
        unique_together = ['id_estudiante', 'id_apoderado']


class Atrasos(models.Model):
    id_atraso = models.AutoField(primary_key=True)
    id_estudiante = models.ForeignKey(Estudiantes, on_delete=models.CASCADE, db_column='id_estudiante')
    fecha = models.DateField()
    hora = models.TimeField()
    minutos_atraso = models.IntegerField()
    justificado = models.BooleanField(default=False)
    notificado_apoderado = models.BooleanField(default=False)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    
    class Meta:
        db_table = 'Atrasos'
        unique_together = ['id_estudiante', 'fecha']
    
    def __str__(self):
        return f"Atraso {self.id_atraso}"


class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    codigo_qr = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=200)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    ubicacion = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Productos'
    
    def __str__(self):
        return self.nombre


class MovimientosStock(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='id_producto')
    tipo_movimiento = models.CharField(max_length=20)
    cantidad = models.IntegerField()
    stock_antes = models.IntegerField()
    stock_despues = models.IntegerField()
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    usuario_responsable = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'MovimientosStock'
    
    def __str__(self):
        return f"{self.tipo_movimiento} - {self.id_producto.nombre} x{self.cantidad}"


class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    email = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    nombre_completo = models.CharField(max_length=150)
    rol = models.CharField(max_length=30, default='administrativo')
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'Usuarios'
    
    def __str__(self):
        return self.email


class Bitacora(models.Model):
    id_log = models.AutoField(primary_key=True)
    usuario_email = models.CharField(max_length=100)
    accion = models.CharField(max_length=100)
    tabla_afectada = models.CharField(max_length=50, blank=True, null=True)
    detalles = models.TextField(blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'Bitacora'