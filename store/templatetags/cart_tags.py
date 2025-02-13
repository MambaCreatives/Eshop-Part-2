from django import template
from store.models import Artwork

register = template.Library()

@register.filter
def get_item(dictionary, key):
    key = str(key)
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_artwork(artwork_id):
    try:
        return Artwork.objects.get(id=artwork_id)
    except Artwork.DoesNotExist:
        return None 