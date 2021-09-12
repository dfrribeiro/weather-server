from django import template
import json

register = template.Library()

@register.filter(name='lookup')
def lookup(value, arg):
    if value:
        obj = json.loads(value)
        return obj.get(arg)
    # else return None

@register.filter(name="values")
def values(value, arg):
    if value: # queryset is not empty
        res = [json.loads(sta.data).get(arg) for sta in value]
        try:
            res = [float(r) for r in res] # convert to float if possible
        except:
            pass
        return res