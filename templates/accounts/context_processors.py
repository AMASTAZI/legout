from restaurants.models import Dish, Restaurant

def cart_context(request):
    """Calcule le panier de session pour l'afficher partout sans rechargement lourd"""
    cart = request.session.get('cart', {})
    total_qty = 0
    subtotal = 0
    items_preview = []

    dish_ids = [int(k) for k in cart.keys() if k.isdigit()]
    dishes_by_id = {d.id: d for d in Dish.objects.filter(id__in=dish_ids)}

    for dish_id_str, item_data in cart.items():
        if not dish_id_str.isdigit():
            continue
        dish_id = int(dish_id_str)
        dish = dishes_by_id.get(dish_id)
        if dish:
            qty = item_data.get('quantity', 1)
            total_qty += qty
            item_subtotal = dish.price * qty
            subtotal += item_subtotal
            items_preview.append({
                'dish': dish,
                'quantity': qty,
                'side': item_data.get('side', ''),
                'instructions': item_data.get('instructions', ''),
                'subtotal': item_subtotal,
            })

    return {
        'cart_item_count': total_qty,
        'cart_subtotal': subtotal,
        'cart_items_preview': items_preview,
    }

def global_settings(request):
    """Données globales de contexte : singleton restaurant et coordonnées"""
    restaurant = Restaurant.get_solo()
    return {
        'app_name': restaurant.name if restaurant else 'Le Goût',
        'app_tagline': restaurant.tagline if restaurant else 'Saveurs Authentiques du Terroir Camerounais',
        'singleton_restaurant': restaurant,
        'support_phone': restaurant.phone if restaurant and restaurant.phone else '+237 690 12 34 56',
        'support_whatsapp': restaurant.phone if restaurant and restaurant.phone else '+237 690 12 34 56',
    }
