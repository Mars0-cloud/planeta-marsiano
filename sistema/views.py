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

# Listado dinámico de películas desde la DB - VERSIÓN MEJORADA
def listado_peliculas(request):
    queryset = WatchedMovie.objects.all()

    # Filtros
    search_title = request.GET.get('title', '')
    filter_year = request.GET.get('year', '')
    filter_genre = request.GET.get('genre', '')
    filter_rating = request.GET.get('rating', '')
    filter_decade = request.GET.get('decade', '')

    if search_title:
        queryset = queryset.filter(name__icontains=search_title)
    if filter_year:
        queryset = queryset.filter(year=filter_year)
    if filter_genre:
        # Filtro inteligente de géneros
        queryset = queryset.filter(genres__icontains=filter_genre)
    if filter_rating:
        # Filtro por rating mínimo
        queryset = queryset.filter(rating__gte=float(filter_rating))
    if filter_decade:
        # Filtro por década
        decade_start = int(filter_decade)
        decade_end = decade_start + 9
        queryset = queryset.filter(year__gte=decade_start, year__lte=decade_end)

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
    elif sort_by == '-rating':
        queryset = queryset.order_by('rating')
    elif sort_by == 'date':
        queryset = queryset.order_by('-date')
    else:
        queryset = queryset.order_by('-date')  # Por defecto más recientes primero

    # Convertir queryset en lista de diccionarios
    peliculas = []
    for peli in queryset:
        peliculas.append({
            'id': peli.id,
            'name': peli.name,
            'year': peli.year,
            'poster_url': peli.poster_url,
            'overview': peli.overview,
            'rating': peli.rating,
            'genres': peli.genres,
            'date': peli.date,
            'vista': True,   # todas las de tu base son "vistas"
        })

    # Obtener géneros únicos para el filtro dropdown
    all_genres = set()
    for movie in WatchedMovie.objects.exclude(genres=''):
        movie_genres = [g.strip() for g in movie.genres.split(',') if g.strip()]
        all_genres.update(movie_genres)
    genres_list = sorted(list(all_genres))

    # Obtener años únicos para el filtro
    years_list = WatchedMovie.objects.values_list('year', flat=True).distinct().order_by('-year')

    # Obtener décadas únicas
    decades = set()
    for year in years_list:
        if year:
            decades.add((year // 10) * 10)
    decades_list = sorted(list(decades), reverse=True)

    context = {
        'peliculas': peliculas,
        'genres_list': genres_list,
        'years_list': years_list,
        'decades_list': decades_list,
        'total_peliculas': len(peliculas),
        'current_filters': {
            'title': search_title,
            'year': filter_year,
            'genre': filter_genre,
            'rating': filter_rating,
            'decade': filter_decade,
            'sort': sort_by
        }
    }

    return render(request, 'sistema/lista.html', context)

# Nueva función para obtener estadísticas rápidas
def get_quick_stats():
    """Obtiene estadísticas básicas para mostrar en la interfaz"""
    from django.db.models import Avg, Max, Min, Count
    
    stats = WatchedMovie.objects.aggregate(
        total=Count('id'),
        avg_rating=Avg('rating'),
        max_rating=Max('rating'),
        min_rating=Min('rating'),
        latest_year=Max('year'),
        oldest_year=Min('year')
    )
    
    return stats


# Detalle de película
def detalle_pelicula(request, pelicula_id):
    pelicula = get_object_or_404(WatchedMovie, id=pelicula_id)
    return render(request, 'sistema/detalle.html', {'pelicula': pelicula})

def todas_peliculas(request):
    peliculas_vistas = obtener_peliculas_vistas()
    solo_vistas = request.GET.get('solo_vistas') == '1'
    peliculas = []

    for titulo in peliculas_vistas:
        # Llamada a TMDb para obtener info de esta película
        search = tmdb.Search()
        response = search.movie(query=titulo)
        if response['results']:
            movie = response['results'][0]
            peliculas.append({
                'id': movie['id'],
                'name': movie['title'],
                'year': movie.get('release_date', '')[:4],
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else '',
                'overview': movie.get('overview', ''),
                'vista': True,
            })

    return render(request, 'sistema/lista.html', {'peliculas': peliculas})





def obtener_peliculas_vistas():
    """Devuelve una lista de títulos de películas que ya viste"""
    archivo_csv = BASE_DIR / 'data' / 'ratings.csv'
    print(f"Leyendo archivo desde: {archivo_csv}")
    print(f"¿El archivo existe? {archivo_csv.exists()}")
    
    peliculas_vistas = set()
    try:
        with open(archivo_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                peliculas_vistas.add(row['Name'])
        print(f"Total de películas cargadas: {len(peliculas_vistas)}")
        print("Primeras 5 películas:", list(peliculas_vistas)[:5])
    except Exception as e:
        print(f"Error leyendo el archivo: {e}")
    
    return peliculas_vistas