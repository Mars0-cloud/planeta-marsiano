import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from sistema.models import WatchedMovie
import tmdbsimple as tmdb

# Tu API Key de TMDb
tmdb.API_KEY = 'c053250666c459a40b3a858f5bb0fabe'

class Command(BaseCommand):
    help = 'Importa películas desde CSV de Letterboxd y las enriquece con TMDb'

    def handle(self, *args, **kwargs):
        # Obtener la ruta absoluta del proyecto (donde está manage.py)
        BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, '../../..')))

        # Ruta correcta del CSV
        csv_path = os.path.join(BASE_DIR, 'data', 'ratings.csv')

        # Abrir CSV
        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    date_obj = datetime.strptime(row['Date'], '%Y-%m-%d').date()
                    name = row['Name']
                    year = int(row['Year']) if row['Year'] else None
                    letterboxd_uri = row['Letterboxd URI']
                    rating = float(row['Rating']) if row['Rating'] else None

                    # Buscar en TMDb con más detalles
                    search = tmdb.Search()
                    response = search.movie(query=name, year=year)
                    if response['results']:
                        data = response['results'][0]
                        tmdb_id = data['id']
                        poster_url = f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get('poster_path') else ''
                        overview = data.get('overview', '')
                        
                        # Obtener detalles completos de la película para géneros
                        movie_details = tmdb.Movies(tmdb_id)
                        movie_info = movie_details.info()
                        genres = ', '.join([genre['name'] for genre in movie_info.get('genres', [])])
                        
                        # También obtener director si está disponible
                        credits = movie_details.credits()
                        director = ''
                        for crew in credits.get('crew', []):
                            if crew.get('job') == 'Director':
                                director = crew.get('name', '')
                                break
                        
                    else:
                        tmdb_id = None
                        poster_url = ''
                        overview = ''
                        genres = ''
                        director = ''

                    # Crear o actualizar en la DB
                    movie_obj, created = WatchedMovie.objects.update_or_create(
                        name=name,
                        year=year,
                        defaults={
                            'date': date_obj,
                            'letterboxd_uri': letterboxd_uri,
                            'rating': rating,
                            'tmdb_id': tmdb_id,
                            'poster_url': poster_url,
                            'overview': overview,
                            'genres': genres,
                            'director': director if 'director' in [f.name for f in WatchedMovie._meta.fields] else ''
                        }
                    )
                    
                    status = "creada" if created else "actualizada"
                    self.stdout.write(f"Película {status}: {name} ({year}) - Géneros: {genres}")

            self.stdout.write(self.style.SUCCESS('¡Películas importadas y enriquecidas correctamente!'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"No se encontró el archivo CSV en {csv_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error durante la importación: {e}"))