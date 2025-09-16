from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Divide una cadena por el delimitador especificado"""
    if value:
        return [item.strip() for item in value.split(delimiter)]
    return []

@register.filter
def trim(value):
    """Elimina espacios en blanco al inicio y final"""
    if value:
        return value.strip()
    return value

@register.filter
def star_rating(rating):
    """Convierte un rating numérico en estrellas"""
    try:
        rating = float(rating)
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        return {
            'full': range(full_stars),
            'half': range(half_star),
            'empty': range(empty_stars)
        }
    except (ValueError, TypeError):
        return {'full': range(0), 'half': range(0), 'empty': range(5)}