from django.contrib import admin
from .models import (
    Estudiantes, Atrasos, Productos, MovimientosStock,
    Apoderados, EstudianteApoderado, Usuarios, Bitacora,
)

admin.site.register(Estudiantes)
admin.site.register(Atrasos)
admin.site.register(Productos)
admin.site.register(MovimientosStock)
admin.site.register(Apoderados)
admin.site.register(EstudianteApoderado)
admin.site.register(Usuarios)
admin.site.register(Bitacora)
