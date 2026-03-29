from django import template


register = template.Library()

@register.filter(name='range')
def filter_range(num):
    # Trả về một dãy số từ 0 đến num-1
    return range(int(num))