from django import template

register = template.Library()

@register.filter
def hash(h, key):
    if key in h:
        return h[key]
    return ""
    
@register.filter
def getlist(d, key):
    return d.getlist(key)
    
@register.filter
def to_int(n):
    if type(n) is list:
        return [int(elem) for elem in n]
    else:
        return int(n)
    
@register.filter    
def str_concat(s1, s2):
    return str(s1) + str(s2)