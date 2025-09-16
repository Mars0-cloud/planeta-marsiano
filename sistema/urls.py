from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contacto/', views.contacto, name='contacto'),
    path('galeria/', views.galeria, name='galeria'),

    # Películas
    path('movies/', views.listado_peliculas, name='listado_peliculas'),
    path('movies/<int:pelicula_id>/', views.detalle_pelicula, name='detalle_pelicula'),
    path('todas/', views.todas_peliculas, name='todas_peliculas'),

]
