from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db.models import Q
from .models import WatchedMovie
import tmdbsimple as tmdb
import csv
from pathlib import Path

tmdb.API_KEY = 'c053250666c459a40b3a858f5bb0fabe'
BASE_DIR = Path(__file__).resolve().parent.parent

# Create your views here.


def index(request):
    return render(request, 'sistema/index.html')

def lista(request):
    return render(request, 'sistema/lista.html')

def detalle(request):
    return render(request, 'sistema/detalle.html')

def about(request):
    return render(request, 'sistema/about.html')

def contacto(request):
    return render(request, 'sistema/contacto.html')

def galeria(request):
    return render(request, 'sistema/galeria.html')

# Listado dinámico de películas desde la DB
def listado_peliculas(request):
    queryset = WatchedMovie.objects.all()

    # Filtros
    search_title = request.GET.get('title', '')
    filter_year = request.GET.get('year', '')
    filter_genre = request.GET.get('genre', '')

    if search_title:
        queryset = queryset.filter(name__icontains=search_title)
    if filter_year:
        queryset = queryset.filter(year=filter_year)
    if filter_genre:
        queryset = queryset.filter(genres__icontains=filter_genre)

    # Ordenamiento
    sort_by = request.GET.get('sort', '')
    if sort_by == 'name':
        queryset = queryset.order_by('name')
    elif sort_by == '-name':
        queryset = queryset.order_by('-name')
    elif sort_by == 'year':
        queryset = queryset.order_by('year')
    elif sort_by == '-year':
        queryset = queryset.order_by('-year')
    elif sort_by == 'rating':
        queryset = queryset.order_by('-rating')
    else:
        queryset = queryset.order_by('name')

    # Convertimos queryset en lista de diccionarios con "vista=True"
    peliculas = []
    for peli in queryset:
        peliculas.append({
            'id': peli.id,
            'name': peli.name,
            'year': peli.year,
            'poster_url': peli.poster_url,
            'overview': peli.overview,
            'vista': True,   # 👈 todas las de tu base son "vistas"
        })

    return render(request, 'sistema/lista.html', {'peliculas': peliculas})


# Detalle de película
def detalle_pelicula(request, pelicula_id):
    pelicula = get_object_or_404(WatchedMovie, id=pelicula_id)
    return render(request, 'sistema/detalle.html', {'pelicula': pelicula})

def todas_peliculas(request):
    peliculas_vistas = obtener_peliculas_vistas()
    solo_vistas = request.GET.get('solo_vistas') == '1'

    search = tmdb.Discover()
    response = search.movie(sort_by='popularity.desc', page=1)
    peliculas = []
    for movie in response['results']:
        vista = movie['title'] in peliculas_vistas
        if solo_vistas and not vista:
            continue
        peliculas.append({
            'id': movie['id'],
            'name': movie['title'],
            'year': movie.get('release_date', '')[:4],
            'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else '',
            'overview': movie.get('overview', ''),
            'vista': vista,
        })

    return render(request, 'sistema/lista.html', {'peliculas': peliculas})


def obtener_peliculas_vistas():
    """Devuelve una lista de títulos de películas que ya viste"""
    archivo_csv = BASE_DIR / 'data' / 'ratings.csv'
    peliculas_vistas = set()
    with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            peliculas_vistas.add(row['Name'])
    return peliculas_vistas