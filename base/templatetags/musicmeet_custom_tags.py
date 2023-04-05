from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    # I had to make this custom tag because the core Django developers refuse to make in-template dictionary access a built-in feature. Grrrr.
    # Those wonky developers at Django, hahaha :)!
    return dictionary.get(key)