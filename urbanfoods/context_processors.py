def store_type(request):
    """Context processor to make store_type available to all templates"""
    return {
        'store_type': request.session.get('store_type', 'food')
    }

