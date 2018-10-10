from django import template

register = template.Library()

@register.inclusion_tag("pagination.html")
def pagination(current, n, last, aria_label=""):
    current, n, last = int(current), int(n), int(last)
    previous_page = int(max(1, current - 1))
    next_page = int(min(last - 1, current + 1))
    start = max(1, current - n // 2)
    stop = min(last, start + n)
    return {
        "left": list(range(start, current)),
        "current": current,
        "previous_page": previous_page,
        "next_page": next_page,
        "right": list(range(current + 1, stop)),
        "aria_label": aria_label,
    }

    