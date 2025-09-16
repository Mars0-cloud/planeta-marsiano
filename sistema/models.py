from django.db import models

# Create your models here.
 

# Peliculas Vistas
class WatchedMovie(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=255)
    year = models.IntegerField()
    letterboxd_uri = models.URLField()

    # Campos para enriquecer con TMDb
    tmdb_id = models.IntegerField(null=True, blank=True)
    poster_url = models.URLField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)  # tu rating personal
    genres = models.CharField(max_length=255, null=True, blank=True)  # opcional, coma-separated

    def __str__(self):
        return f"{self.name} ({self.year})"