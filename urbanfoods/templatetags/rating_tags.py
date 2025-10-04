from django import template

register = template.Library()

@register.filter
def star_rating(value):
    """
    Converts a float rating into a list of star types:
    'full', 'half', 'empty' for rendering stars in template.
    """
    try:
        rating = float(value)
    except (ValueError, TypeError):
        return []

    stars = []
    full_stars = int(rating)
    half_star = (rating - full_stars) >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)

    stars.extend(['full'] * full_stars)
    if half_star:
        stars.append('half')
    stars.extend(['empty'] * empty_stars)

    return stars
