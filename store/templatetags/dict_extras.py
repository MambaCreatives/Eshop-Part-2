from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    # Since keys in session data are strings, ensure key is a string.
    return dictionary.get(str(key))
