from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, Q, ProtectedError
from django.utils import timezone
from accounts.models import CustomUser
from accounts.forms import AdminStaffCreateForm
from restaurants.models import Restaurant, Dish, Category
from restaurants.forms import RestaurantForm
from orders.models import Order
from delivery.models import Delivery
from core.permissions import (
    restaurateur_required,
    livreur_required,
    admin_required,
)

def dashboard_dispatch(request):
    """
    Aiguille automatiquement l'utilisateur connecté vers son tableau de bord spécifique
    selon son rôle réel en base de données.
    """
    if not request.user.is_authenticated:
        return redirect('/comptes/connexion/?next=/dashboard/')

    if getattr(request.user, 'must_change_password', False):
        return redirect('accounts:force_password_change')

    user = request.user
    if user.is_platform_admin or user.role == 'admin':
        return redirect('dashboard:admin')
    elif user.is_restaurant or user.role in ['restaurant', 'restaurateur']:
        return redirect('dashboard:restaurant')
    elif user.is_driver or user.role in ['driver', 'livreur']:
        return redirect('dashboard:driver')
    else:
        return redirect('orders:history')


# ==========================================
# 1. ESPACE RESTAURATEUR (Protégé par @restaurateur_required)
# ==========================================

@restaurateur_required
def restaurant_overview(request):
    """Vue d'ensemble pour le restaurateur de l'unique établissement"""
    restaurant = Restaurant.get_solo()
    if not restaurant:
        return redirect('dashboard:restaurant_settings')

    # Métriques du jour
    today = timezone.now().date()
    today_orders = Order.objects.filter(restaurant=restaurant, created_at__date=today)
    total_sales_today = today_orders.filter(payment_status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
    pending_orders_count = Order.objects.filter(restaurant=restaurant, status__in=['payee', 'en_attente', 'validee', 'confirmee', 'en_preparation']).count()
    completed_orders_count = Order.objects.filter(restaurant=restaurant, status='livree').count()

    # Commandes actives pour la cuisine
    active_orders = Order.objects.filter(
        restaurant=restaurant,
        status__in=['payee', 'en_attente', 'validee', 'confirmee', 'en_preparation', 'prete']
    ).prefetch_related('items__dish').order_by('created_at')

    context = {
        'restaurant': restaurant,
        'today_sales': total_sales_today,
        'today_orders_count': today_orders.count(),
        'pending_orders_count': pending_orders_count,
        'completed_orders_count': completed_orders_count,
        'active_orders': active_orders,
    }
    return render(request, 'dashboard/restaurant/overview.html', context)


@restaurateur_required
def restaurant_orders(request):
    """Gestion des commandes pour la cuisine"""
    restaurant = Restaurant.get_solo()
    status_filter = request.GET.get('status')
    
    orders = Order.objects.filter(restaurant=restaurant).prefetch_related('items__dish').order_by('-created_at')
    if status_filter and status_filter != 'tous':
        orders = orders.filter(status=status_filter)

    context = {
        'restaurant': restaurant,
        'orders': orders,
        'current_status': status_filter or 'tous',
    }
    return render(request, 'dashboard/restaurant/orders.html', context)


@restaurateur_required
@require_POST
def restaurant_update_order_status(request, order_id):
    """Changement de statut en cuisine (Valider, Refuser & Rembourser, Préparer, Prêt pour coursier)"""
    restaurant = Restaurant.get_solo()
    order = get_object_or_404(Order, id=order_id, restaurant=restaurant)
    action = request.POST.get('action')
    new_status = request.POST.get('status')

    if action == 'validate' or new_status in ['validee', 'confirmee']:
        target_st = new_status if new_status in ['validee', 'confirmee'] else 'validee'
        order.validate_order(target_status=target_st)
        messages.success(request, f"Commande #{order.order_number} validée avec succès ! Les livreurs et le client ont été notifiés.")
    elif action == 'refuse' or new_status == 'refusee':
        reason = request.POST.get('reason', "Rupture de stock / Ingrédient indisponible en cuisine")
        order.refuse_order(reason=reason)
        messages.warning(request, f"Commande #{order.order_number} refusée. Le client a été automatiquement remboursé.")
    elif new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        messages.success(request, f"Commande #{order.order_number} passée en statut '{order.get_status_display()}'.")
    else:
        messages.error(request, "Statut de commande invalide.")

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'dashboard:restaurant_orders')


@restaurateur_required
@require_POST
def restaurant_validate_order(request, order_id):
    """Validation explicite de la commande par le restaurateur"""
    restaurant = Restaurant.get_solo()
    order = get_object_or_404(Order, id=order_id, restaurant=restaurant)
    order.validate_order()
    messages.success(request, f"Commande #{order.order_number} validée ! Transmise aux livreurs.")
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'dashboard:restaurant_orders')


@restaurateur_required
@require_POST
def restaurant_refuse_order(request, order_id):
    """Refus explicite de la commande par le restaurateur avec remboursement automatique"""
    restaurant = Restaurant.get_solo()
    order = get_object_or_404(Order, id=order_id, restaurant=restaurant)
    reason = request.POST.get('reason', "Rupture d'ingrédient frais en cuisine")
    order.refuse_order(reason=reason)
    messages.warning(request, f"Commande #{order.order_number} refusée. Montant automatiquement remboursé au client.")
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer or 'dashboard:restaurant_orders')


@restaurateur_required
def restaurant_menu(request):
    """Gestion de la carte : plats, boissons (section séparée), entrées, desserts"""
    restaurant = Restaurant.get_solo()
    
    food_dishes = Dish.objects.filter(restaurant=restaurant, product_type__in=['plat', 'entree', 'dessert']).select_related('category').order_by('product_type', 'name')
    drinks = Dish.objects.filter(restaurant=restaurant, product_type='boisson').select_related('category').order_by('name')
    categories = Category.objects.all()

    context = {
        'restaurant': restaurant,
        'food_dishes': food_dishes,
        'drinks': drinks,
        'categories': categories,
    }
    return render(request, 'dashboard/restaurant/menu.html', context)


@restaurateur_required
@require_POST
def restaurant_toggle_dish(request, dish_id):
    """Activer ou désactiver immédiatement un produit en cuisine"""
    restaurant = Restaurant.get_solo()
    dish = get_object_or_404(Dish, id=dish_id, restaurant=restaurant)
    dish.is_available = not dish.is_available
    dish.save()
    status_str = "disponible" if dish.is_available else "en rupture temporaire"
    messages.info(request, f"Le produit '{dish.name}' est maintenant noté comme {status_str}.")
    return redirect('dashboard:restaurant_menu')


@restaurateur_required
@require_POST
def restaurant_add_dish(request):
    """Ajouter un nouveau plat ou une boisson au menu du restaurant"""
    restaurant = Restaurant.get_solo()
    if not restaurant:
        messages.error(request, "Veuillez d'abord initialiser les coordonnées du restaurant.")
        return redirect('dashboard:restaurant_settings')

    name = request.POST.get('name', '').strip()
    product_type = request.POST.get('product_type', 'plat')
    category_id = request.POST.get('category')
    price = request.POST.get('price')
    description = request.POST.get('description', '').strip()
    spice_level = request.POST.get('spice_level', 'doux' if product_type == 'boisson' else 'moyen')
    origin = request.POST.get('origin', 'Littoral (Sawa)')
    sides = request.POST.get('sides', '').strip()
    import os
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
    MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 Mo

    image_file = request.FILES.get('image_file')

    # Validation du champ photo obligatoire lors de la création
    if not image_file and not request.POST.get('image'):
        messages.error(request, "La photo du produit est obligatoire. Veuillez sélectionner une image (JPG, JPEG, PNG, WEBP).")
        return redirect('dashboard:restaurant_menu')

    if image_file:
        ext = os.path.splitext(image_file.name)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            messages.error(request, f"Format d'image '{ext}' non supporté. Les formats acceptés sont JPG, JPEG, PNG et WEBP.")
            return redirect('dashboard:restaurant_menu')
        if image_file.size > MAX_IMAGE_SIZE_BYTES:
            messages.error(request, "La taille du fichier dépasse la limite autorisée de 5 Mo.")
            return redirect('dashboard:restaurant_menu')

    if name and price:
        category = Category.objects.filter(id=category_id).first() if category_id else None
        new_dish = Dish(
            restaurant=restaurant,
            category=category,
            name=name,
            product_type=product_type,
            description=description or name,
            price=int(price),
            spice_level=spice_level,
            authentic_origin=origin,
            sides_included=sides,
            is_available=True
        )
        if image_file:
            new_dish.image_file = image_file
        elif request.POST.get('image'):
            new_dish.image = request.POST.get('image').strip()

        new_dish.save()
        type_label = new_dish.get_product_type_display()
        messages.success(request, f"{type_label} '{name}' ({new_dish.price} FCFA) enregistré avec succès !")
    else:
        messages.error(request, "Veuillez renseigner au moins le nom et le prix en FCFA.")

    return redirect('dashboard:restaurant_menu')


@restaurateur_required
@require_POST
def restaurant_edit_dish(request, dish_id):
    """Modifier un produit existant (prix, photo, disponibilité, description, catégorie)"""
    import os
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
    MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 Mo

    restaurant = Restaurant.get_solo()
    dish = get_object_or_404(Dish, id=dish_id, restaurant=restaurant)

    name = request.POST.get('name')
    price = request.POST.get('price')
    description = request.POST.get('description')
    product_type = request.POST.get('product_type')
    category_id = request.POST.get('category')
    sides = request.POST.get('sides')
    is_available = request.POST.get('is_available') == 'on'
    image_file = request.FILES.get('image_file')

    if image_file:
        ext = os.path.splitext(image_file.name)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            messages.error(request, f"Format d'image '{ext}' non supporté. Les formats autorisés sont JPG, JPEG, PNG et WEBP.")
            return redirect('dashboard:restaurant_menu')
        if image_file.size > MAX_IMAGE_SIZE_BYTES:
            messages.error(request, "L'image sélectionnée dépasse la limite autorisée de 5 Mo.")
            return redirect('dashboard:restaurant_menu')
        dish.image_file = image_file

    if name and price:
        dish.name = name
        dish.price = int(price)
        dish.description = description
        if product_type:
            dish.product_type = product_type
        if category_id:
            cat = Category.objects.filter(id=category_id).first()
            if cat:
                dish.category = cat
        if sides is not None:
            dish.sides_included = sides
        dish.is_available = is_available
        dish.save()
        messages.success(request, f"Produit '{dish.name}' mis à jour avec succès.")
    else:
        messages.error(request, "Le nom et le prix sont obligatoires.")

    return redirect('dashboard:restaurant_menu')


@restaurateur_required
@require_POST
def restaurant_delete_dish(request, dish_id):
    """Supprimer un produit de la base de données"""
    restaurant = Restaurant.get_solo()
    dish = get_object_or_404(Dish, id=dish_id, restaurant=restaurant)
    name = dish.name

    try:
        dish.delete()
        messages.success(request, f"Le produit '{name}' a été supprimé de votre carte.")
    except ProtectedError:
        dish.is_available = False
        dish.save()
        messages.warning(request, f"'{name}' figure dans des commandes passées. Il a été désactivé pour préserver l'historique comptable.")

    return redirect('dashboard:restaurant_menu')


@restaurateur_required
def restaurant_settings(request):
    """Gestion des informations de l'unique restaurant (horaires, adresse, contacts, frais de livraison)"""
    restaurant = Restaurant.get_solo()
    
    if request.method == 'POST':
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            resto = form.save(commit=False)
            if not resto.owner:
                resto.owner = request.user
            resto.save()
            messages.success(request, "Informations de l'établissement mises à jour avec succès.")
            return redirect('dashboard:restaurant_settings')
    else:
        form = RestaurantForm(instance=restaurant)

    return render(request, 'dashboard/restaurant/settings.html', {'form': form, 'restaurant': restaurant})


# ==========================================
# 2. ESPACE LIVREUR (Protégé par @livreur_required)
# ==========================================

@livreur_required
def driver_overview(request):
    """Courses disponibles au restaurant pour livraison"""
    available_deliveries = Delivery.objects.filter(
        status='recherche_livreur',
        order__status__in=['confirmee', 'en_preparation', 'prete']
    ).select_related('order__restaurant', 'order__client').order_by('order__created_at')

    active_delivery = Delivery.objects.filter(
        driver=request.user,
        status__in=['assignee', 'arrivee_restaurant', 'recuperee', 'arrivee_client']
    ).select_related('order__restaurant', 'order__client').first()

    context = {
        'available_deliveries': available_deliveries,
        'active_delivery': active_delivery,
    }
    return render(request, 'dashboard/driver/overview.html', context)


@livreur_required
@require_POST
def driver_accept_delivery(request, delivery_id):
    """Un livreur accepte une course disponible"""
    delivery = get_object_or_404(Delivery, id=delivery_id, status='recherche_livreur')
    delivery.driver = request.user
    delivery.driver_phone = request.user.phone
    delivery.status = 'assignee'
    delivery.assigned_at = timezone.now()
    delivery.save()

    messages.success(request, f"Course #{delivery.order.order_number} acceptée ! Rendez-vous au restaurant pour récupérer la commande.")
    return redirect('dashboard:driver_active')


@livreur_required
def driver_active(request):
    """Navigation GPS, étapes de livraison et validation finale par code PIN"""
    active_delivery = Delivery.objects.filter(
        driver=request.user,
        status__in=['assignee', 'arrivee_restaurant', 'recuperee', 'arrivee_client']
    ).select_related('order__restaurant', 'order__client').first()

    return render(request, 'dashboard/driver/active.html', {'delivery': active_delivery})


@livreur_required
@require_POST
def driver_update_status(request, delivery_id):
    """Mise à jour des étapes ou confirmation par code PIN client"""
    delivery = get_object_or_404(Delivery, id=delivery_id, driver=request.user)
    action = request.POST.get('action')

    if action == 'at_restaurant':
        delivery.status = 'arrivee_restaurant'
        delivery.save()
        messages.info(request, "Arrivé au restaurant.")
    elif action == 'picked_up':
        delivery.status = 'recuperee'
        delivery.picked_up_at = timezone.now()
        delivery.save()
        delivery.order.status = 'en_livraison'
        delivery.order.save()
        messages.success(request, "Plat chaud récupéré ! En route vers le client.")
    elif action == 'at_client':
        delivery.status = 'arrivee_client'
        delivery.save()
        messages.info(request, "Arrivé chez le client. Demandez le code secret PIN pour valider la remise.")
    elif action == 'confirm_pin':
        entered_pin = request.POST.get('pin', '').strip()
        if entered_pin == delivery.order.delivery_pin:
            delivery.status = 'livree'
            delivery.delivered_at = timezone.now()
            delivery.save()
            delivery.order.status = 'livree'
            delivery.order.save()
            messages.success(request, f"Livraison validée avec succès ! Gain de {delivery.driver_payout} FCFA crédité à votre compte.")
            return redirect('dashboard:driver_earnings')
        else:
            messages.error(request, "Code PIN incorrect. Veuillez redemander le code secret à 4 chiffres au client.")

    return redirect('dashboard:driver_active')


@livreur_required
@require_POST
def driver_update_gps(request, delivery_id):
    """Mise à jour en temps réel des coordonnées GPS du livreur (simulation ou live GPS)"""
    delivery = get_object_or_404(Delivery, id=delivery_id, driver=request.user)
    try:
        lat = float(request.POST.get('latitude'))
        lng = float(request.POST.get('longitude'))
        delivery.current_latitude = lat
        delivery.current_longitude = lng
        delivery.save(update_fields=['current_latitude', 'current_longitude'])
        return JsonResponse({'success': True, 'lat': lat, 'lng': lng})
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Coordonnées GPS invalides'}, status=400)


@livreur_required
def driver_earnings(request):
    """Historique des livraisons terminées et gains"""
    deliveries = Delivery.objects.filter(driver=request.user, status='livree').select_related('order').order_by('-delivered_at')
    total_earned = deliveries.aggregate(total=Sum('driver_payout'))['total'] or 0

    context = {
        'deliveries': deliveries,
        'total_earned': total_earned,
        'deliveries_count': deliveries.count(),
    }
    return render(request, 'dashboard/driver/earnings.html', context)


# ==========================================
# 3. ESPACE ADMINISTRATEUR (Protégé par @admin_required)
# ==========================================

@admin_required
def admin_overview(request):
    """Vue globale de supervision des commandes, statistiques et comptes"""
    total_orders = Order.objects.count()
    total_gmv = Order.objects.filter(payment_status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
    restaurant = Restaurant.get_solo()
    drivers_count = CustomUser.objects.filter(role__in=['driver', 'livreur']).count()
    restaurateurs_count = CustomUser.objects.filter(role__in=['restaurant', 'restaurateur']).count()
    clients_count = CustomUser.objects.filter(role='client').count()

    recent_orders = Order.objects.select_related('client').order_by('-created_at')[:10]

    context = {
        'total_orders': total_orders,
        'total_gmv': total_gmv,
        'restaurant': restaurant,
        'drivers_count': drivers_count,
        'restaurateurs_count': restaurateurs_count,
        'clients_count': clients_count,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/admin/overview.html', context)


@admin_required
def admin_users(request):
    """Gestion des comptes : filtrage, activation/désactivation et suppression"""
    role_filter = request.GET.get('role')
    users = CustomUser.objects.all().order_by('-date_joined')
    if role_filter in ['client', 'restaurant', 'restaurateur', 'driver', 'livreur', 'admin']:
        if role_filter in ['restaurant', 'restaurateur']:
            users = users.filter(role__in=['restaurant', 'restaurateur'])
        elif role_filter in ['driver', 'livreur']:
            users = users.filter(role__in=['driver', 'livreur'])
        else:
            users = users.filter(role=role_filter)

    return render(request, 'dashboard/admin/users.html', {'users': users, 'current_role': role_filter})


@admin_required
def admin_create_staff_user(request):
    """
    Création exclusive des comptes Restaurateur et Livreur par l'Administrateur.
    Définit un mot de passe temporaire et force must_change_password=True.
    """
    if request.method == 'POST':
        form = AdminStaffCreateForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, f"Le compte {new_user.get_role_display()} '{new_user.username}' a été créé avec succès avec un mot de passe temporaire.")
            return redirect('dashboard:admin_users')
        else:
            messages.error(request, "Erreur lors de la création du compte. Vérifiez les champs.")
    else:
        form = AdminStaffCreateForm()

    return render(request, 'dashboard/admin/create_staff.html', {'form': form})


@admin_required
@require_POST
def admin_toggle_user_active(request, user_id):
    """Activer ou désactiver un compte utilisateur"""
    target_user = get_object_or_404(CustomUser, id=user_id)
    if target_user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte administrateur.")
        return redirect('dashboard:admin_users')

    target_user.is_active = not target_user.is_active
    target_user.save()
    status_str = "activé" if target_user.is_active else "désactivé"
    messages.info(request, f"Le compte de {target_user.username} est maintenant {status_str}.")
    return redirect('dashboard:admin_users')


@admin_required
@require_POST
def admin_delete_user(request, user_id):
    """Supprimer définitivement un compte utilisateur"""
    target_user = get_object_or_404(CustomUser, id=user_id)
    if target_user == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte administrateur.")
        return redirect('dashboard:admin_users')

    username = target_user.username
    target_user.delete()
    messages.success(request, f"Le compte '{username}' a été supprimé.")
    return redirect('dashboard:admin_users')


@admin_required
def admin_restaurant_settings(request):
    """Paramétrage de l'établissement unique par l'administrateur"""
    restaurant = Restaurant.get_solo()
    if request.method == 'POST':
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, "Paramètres du restaurant enregistrés avec succès.")
            return redirect('dashboard:admin_restaurant_settings')
    else:
        form = RestaurantForm(instance=restaurant)

    return render(request, 'dashboard/admin/restaurant_settings.html', {'form': form, 'restaurant': restaurant})
