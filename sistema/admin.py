from django.contrib import admin
from .models import WatchedMovie

@admin.register(WatchedMovie)
class WatchedMovieAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'date', 'rating')
    search_fields = ('name', 'year')
    list_filter = ('year', 'genres')