from django import template

register = template.Library()

@register.filter
def addcss(field, css):
    # Filter idea adapted from Ivo van der Wijk
    # (http://vanderwijk.info/blog/adding-css-classes-formfields-in-django-templates/)
    attrs = {}
    definition = css.split(",")
    
    for d in definition:
        if ":" not in d:
            attrs['class'] = d
        else:
            t, v = d.split(":")
            if '|' not in t:
                attrs[t] = v
            else:
                t = t[t.find("|")+1:]
                if 'style' in attrs:
                    attrs['style'] += t + ": " + v + ";"
                else:
                    attrs['style'] = t + ": " + v + ";"
        
    return field.as_widget(attrs=attrs)
    