from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.db.models import Q, Count, Avg, Max, Min
from django.db.models.functions import TruncMonth
from .models import WatchedMovie
from pathlib import Path
from collections import Counter
import tmdbsimple as tmdb
import csv
import json
import datetime

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

def estadisticas(request):
    """Página de estadísticas completas de la biblioteca"""
    
    # Estadísticas básicas
    total_peliculas = WatchedMovie.objects.count()
    
    if total_peliculas == 0:
        # Si no hay películas, retornar valores por defecto
        context = {
            'total_peliculas': 0,
            'mensaje': 'No hay películas en la biblioteca aún.'
        }
        return render(request, 'sistema/estadisticas.html', context)
    
    # Estadísticas de ratings
    ratings_stats = WatchedMovie.objects.aggregate(
        promedio=Avg('rating'),
        maximo=Max('rating'),
        minimo=Min('rating')
    )
    
    # Distribución de ratings
    ratings_distribution = WatchedMovie.objects.values('rating').annotate(
        count=Count('rating')
    ).order_by('-rating')
    
    # Distribución detallada de ratings
    ratings_counts = {
        '5_estrellas': WatchedMovie.objects.filter(rating=5.0).count(),
        '4_5_estrellas': WatchedMovie.objects.filter(rating=4.5).count(),
        '4_estrellas': WatchedMovie.objects.filter(rating=4.0).count(),
        '3_5_estrellas': WatchedMovie.objects.filter(rating=3.5).count(),
        '3_estrellas': WatchedMovie.objects.filter(rating=3.0).count(),
        'menos_3': WatchedMovie.objects.filter(rating__lt=3.0).count(),
    }
    
    # Top géneros
    all_genres = []
    for movie in WatchedMovie.objects.exclude(genres=''):
        movie_genres = [g.strip() for g in movie.genres.split(',') if g.strip()]
        all_genres.extend(movie_genres)
    
    genre_counter = Counter(all_genres)
    top_genres = genre_counter.most_common(10)  # Top 10 géneros
    
    # Géneros específicos (los más comunes en cine)
    genre_counts = {
        'Drama': genre_counter.get('Drama', 0),
        'Comedy': genre_counter.get('Comedy', 0),
        'Action': genre_counter.get('Action', 0),
        'Horror': genre_counter.get('Horror', 0),
        'Thriller': genre_counter.get('Thriller', 0),
        'Romance': genre_counter.get('Romance', 0),
        'Science Fiction': genre_counter.get('Science Fiction', 0),
        'Crime': genre_counter.get('Crime', 0),
        'Adventure': genre_counter.get('Adventure', 0),
        'Animation': genre_counter.get('Animation', 0),
    }
    
    # Estadísticas por décadas
    decades_stats = {}
    for movie in WatchedMovie.objects.all():
        if movie.year:
            decade = (movie.year // 10) * 10
            decade_key = f"{decade}s"
            if decade_key not in decades_stats:
                decades_stats[decade_key] = {'count': 0, 'avg_rating': 0, 'total_rating': 0}
            decades_stats[decade_key]['count'] += 1
            decades_stats[decade_key]['total_rating'] += (movie.rating or 0)
    
    # Calcular promedio por década
    for decade in decades_stats:
        if decades_stats[decade]['count'] > 0:
            decades_stats[decade]['avg_rating'] = round(
                decades_stats[decade]['total_rating'] / decades_stats[decade]['count'], 2
            )
    
    # Ordenar décadas
    decades_stats = dict(sorted(decades_stats.items(), key=lambda x: x[0], reverse=True))
    
    # Películas por año (últimos años con más actividad)
    years_stats = WatchedMovie.objects.values('year').annotate(
        count=Count('year'),
        avg_rating=Avg('rating')
    ).order_by('-count')[:10]
    
    # Mejores y peores películas
    mejores_peliculas = WatchedMovie.objects.filter(
        rating__gte=4.5
    ).order_by('-rating', 'name')[:10]
    
    peores_peliculas = WatchedMovie.objects.filter(
        rating__lte=3.0
    ).order_by('rating', 'name')[:5]
    
    # Películas vistas por mes (últimos 12 meses)
    hace_un_ano = datetime.date.today() - datetime.timedelta(days=365)

    actividad_mensual = (
        WatchedMovie.objects
        .filter(date__gte=hace_un_ano)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Más recientes
    peliculas_recientes = WatchedMovie.objects.order_by('-date')[:5]
    
    # Datos para gráficos (JSON)
    ratings_chart_data = {
        'labels': [f"{item['rating']}" for item in ratings_distribution],
        'data': [item['count'] for item in ratings_distribution]
    }
    
    genres_chart_data = {
        'labels': [genre[0] for genre in top_genres[:8]],  # Top 8 para que quepa bien
        'data': [genre[1] for genre in top_genres[:8]]
    }
    
    decades_chart_data = {
        'labels': list(decades_stats.keys()),
        'counts': [decades_stats[d]['count'] for d in decades_stats.keys()],
        'ratings': [decades_stats[d]['avg_rating'] for d in decades_stats.keys()]
    }
    
    context = {
        'total_peliculas': total_peliculas,
        'ratings_stats': ratings_stats,
        'ratings_counts': ratings_counts,
        'genre_counts': genre_counts,
        'top_genres': top_genres,
        'decades_stats': decades_stats,
        'years_stats': years_stats,
        'mejores_peliculas': mejores_peliculas,
        'peores_peliculas': peores_peliculas,
        'actividad_mensual': actividad_mensual,
        'peliculas_recientes': peliculas_recientes,
        
        # Datos para gráficos
        'ratings_chart_data': json.dumps(ratings_chart_data),
        'genres_chart_data': json.dumps(genres_chart_data),
        'decades_chart_data': json.dumps(decades_chart_data),
        
        # Porcentajes
        'porcentaje_5_estrellas': round((ratings_counts['5_estrellas'] / total_peliculas) * 100, 1),
        'porcentaje_horror': round((genre_counts['Horror'] / total_peliculas) * 100, 1) if total_peliculas > 0 else 0,
        'porcentaje_drama': round((genre_counts['Drama'] / total_peliculas) * 100, 1) if total_peliculas > 0 else 0,
    }
    
    return render(request, 'sistema/estadisticas.html', context)