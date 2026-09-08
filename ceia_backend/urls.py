from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from gestion import views

router = DefaultRouter()
router.register(r'estudiantes', views.EstudianteViewSet)
router.register(r'atrasos', views.AtrasoViewSet)
router.register(r'productos', views.ProductoViewSet)
router.register(r'movimientos', views.MovimientoStockViewSet)
router.register(r'apoderados', views.ApoderadoViewSet)
router.register(r'estudiante-apoderado', views.EstudianteApoderadoViewSet)

urlpatterns = [
    path('', views.frontend, name='frontend'),
    path('admin/', admin.site.urls),
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/set-password/', views.CambiarPasswordView.as_view(), name='set-password'),
    path('api/', include(router.urls)),
]
