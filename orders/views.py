from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_POST
from restaurants.models import Dish, Restaurant
from .models import Order, OrderItem, Notification, Invoice
from .pdf_generator import generate_invoice_pdf
from delivery.models import Delivery
from payments.models import PaymentTransaction

def cart_view(request):
    """Affichage détaillé du panier avant validation"""
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = 0
    restaurant = Restaurant.get_solo()

    dish_ids = [int(k) for k in cart.keys() if k.isdigit()]
    dishes = Dish.objects.filter(id__in=dish_ids)
    dishes_dict = {d.id: d for d in dishes}

    for dish_id_str, item in cart.items():
        if not dish_id_str.isdigit():
            continue
        dish = dishes_dict.get(int(dish_id_str))
        if dish:
            qty = item.get('quantity', 1)
            line_subtotal = dish.price * qty
            subtotal += line_subtotal
            cart_items.append({
                'dish': dish,
                'quantity': qty,
                'side': item.get('side', ''),
                'instructions': item.get('instructions', ''),
                'subtotal': line_subtotal,
            })

    base_delivery = restaurant.delivery_fee if restaurant else 1000
    if subtotal < 2000 and cart_items:
        # En arrière-plan : 10% + 1000 FCFA de livraison si commande < 2000 FCFA (sans mentionner les 10% au client)
        delivery_fee = 1000 + int(round(subtotal * 0.10))
    else:
        delivery_fee = base_delivery

    can_checkout = len(cart_items) > 0

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'restaurant': restaurant,
        'delivery_fee': delivery_fee,
        'total_amount': subtotal + delivery_fee if cart_items else 0,
        'can_checkout': can_checkout,
    }
    return render(request, 'orders/cart.html', context)


@require_POST
def add_to_cart(request, dish_id):
    """Ajout d'un plat au panier de session du restaurant unique"""
    dish = get_object_or_404(Dish, id=dish_id, is_available=True)
    cart = request.session.get('cart', {})

    qty = int(request.POST.get('quantity', 1))
    side = request.POST.get('side', '').strip()
    instructions = request.POST.get('instructions', '').strip()

    dish_key = str(dish.id)

    if dish_key in cart:
        cart[dish_key]['quantity'] += qty
        if side:
            cart[dish_key]['side'] = side
        if instructions:
            cart[dish_key]['instructions'] = instructions
    else:
        cart[dish_key] = {
            'quantity': qty,
            'side': side or dish.sides_included,
            'instructions': instructions,
        }

    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, f"{qty}x {dish.name} ajouté(s) à votre panier !")
    
    # Si requête AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart.values() if isinstance(item, dict)),
            'message': f"{dish.name} ajouté !"
        })

    return redirect('orders:cart')


@require_POST
def update_cart(request, dish_id):
    """Modifier la quantité ou supprimer un plat du panier"""
    cart = request.session.get('cart', {})
    dish_key = str(dish_id)
    action = request.POST.get('action')

    if dish_key in cart:
        if action == 'increase':
            cart[dish_key]['quantity'] += 1
        elif action == 'decrease':
            cart[dish_key]['quantity'] -= 1
            if cart[dish_key]['quantity'] <= 0:
                del cart[dish_key]
        elif action == 'remove':
            del cart[dish_key]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('orders:cart')


@require_POST
def clear_cart(request):
    """Vider tout le panier"""
    request.session['cart'] = {}
    request.session.modified = True
    messages.info(request, "Votre panier a été vidé.")
    return redirect('orders:cart')


@login_required(login_url='/comptes/connexion/?next=/commandes/commander/')
def checkout_view(request):
    """
    Validation de commande :
    Demande la connexion à cette étape précise.
    Choix entre livraison à domicile ou retrait sur place (à emporter),
    coordonnées, repère visuel précis et paiement sécurisé.
    """
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Votre panier est vide. Veuillez choisir vos plats savoureux.")
        return redirect('core:home')

    dish_ids = [int(k) for k in cart.keys() if k.isdigit()]
    dishes = Dish.objects.filter(id__in=dish_ids)
    
    if not dishes.exists():
        messages.error(request, "Les plats de votre panier ne sont plus disponibles.")
        request.session['cart'] = {}
        return redirect('core:home')

    restaurant = Restaurant.get_solo()
    subtotal = sum(d.price * cart[str(d.id)]['quantity'] for d in dishes)
    base_delivery = restaurant.delivery_fee if restaurant else 1000
    if subtotal < 2000:
        delivery_fee = 1000 + int(round(subtotal * 0.10))
    else:
        delivery_fee = base_delivery

    if request.method == 'POST':
        delivery_type = request.POST.get('delivery_type', 'delivery')
        payment_method = request.POST.get('payment_method', 'mtn_momo')
        client_notes = request.POST.get('client_notes', '')

        # Si retrait au restaurant, pas de frais de livraison
        actual_fee = 0 if delivery_type == 'pickup' else delivery_fee
        total_amount = subtotal + actual_fee

        delivery_phone = request.POST.get('delivery_phone', request.user.phone or '')
        delivery_city = request.POST.get('delivery_city', restaurant.city if restaurant else 'Douala')
        delivery_neighborhood = request.POST.get('delivery_neighborhood', '')
        delivery_address = request.POST.get('delivery_address', '')
        delivery_landmark = request.POST.get('delivery_landmark', '')

        if delivery_type == 'delivery' and not (delivery_neighborhood and delivery_address and delivery_landmark and delivery_phone):
            messages.error(request, "Veuillez renseigner toutes les informations de livraison et votre repère visuel.")
            return render(request, 'orders/checkout.html', {
                'restaurant': restaurant,
                'dishes': dishes,
                'cart': cart,
                'subtotal': subtotal,
                'delivery_fee': delivery_fee,
                'total_amount': total_amount,
            })

        # Gestion du mode de paiement
        if payment_method == 'wallet':
            if not request.user.can_pay_with_wallet(total_amount):
                messages.error(
                    request,
                    f"Solde portefeuille insuffisant. Solde disponible : {request.user.wallet_balance} FCFA, requis : {total_amount} FCFA."
                )
                return render(request, 'orders/checkout.html', {
                    'restaurant': restaurant,
                    'dishes': dishes,
                    'cart': cart,
                    'subtotal': subtotal,
                    'delivery_fee': delivery_fee,
                    'total_amount': total_amount,
                })
            request.user.debit_wallet(total_amount)
            initial_status = 'payee'
            initial_payment_status = 'paid'
        elif payment_method in ['mtn_momo', 'orange_money', 'cinetpay']:
            initial_status = 'payee'
            initial_payment_status = 'paid'
        else:
            initial_status = 'en_attente'
            initial_payment_status = 'pending'

        # Création de la commande
        order = Order.objects.create(
            client=request.user,
            restaurant=restaurant,
            delivery_type=delivery_type,
            status=initial_status,
            subtotal=subtotal,
            delivery_fee=actual_fee,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status=initial_payment_status,
            delivery_city=delivery_city,
            delivery_neighborhood=delivery_neighborhood if delivery_type == 'delivery' else 'Retrait au restaurant',
            delivery_address=delivery_address if delivery_type == 'delivery' else (restaurant.address if restaurant else 'Restaurant'),
            delivery_landmark=delivery_landmark if delivery_type == 'delivery' else 'Comptoir de retrait',
            delivery_phone=delivery_phone,
            client_notes=client_notes,
        )

        # Création des lignes de commande
        for d in dishes:
            item_data = cart[str(d.id)]
            OrderItem.objects.create(
                order=order,
                dish=d,
                dish_name=d.name,
                unit_price=d.price,
                quantity=item_data['quantity'],
                subtotal=d.price * item_data['quantity'],
                selected_side=item_data.get('side', ''),
                special_instructions=item_data.get('instructions', ''),
            )

        # Si livraison à domicile demandée, création de la mission de livraison
        if delivery_type == 'delivery':
            Delivery.objects.create(
                order=order,
                status='recherche_livreur',
                pickup_address=restaurant.address if restaurant else "Restaurant",
                pickup_latitude=restaurant.latitude if restaurant else 4.051,
                pickup_longitude=restaurant.longitude if restaurant else 9.708,
                dropoff_address=f"{delivery_address}, {delivery_neighborhood} ({delivery_landmark})",
                dropoff_latitude=(restaurant.latitude - 0.008) if restaurant else 4.043,
                dropoff_longitude=(restaurant.longitude + 0.005) if restaurant else 9.713,
                current_latitude=restaurant.latitude if restaurant else 4.051,
                current_longitude=restaurant.longitude if restaurant else 9.708,
                distance_km=3.4,
                estimated_duration_min=35,
                driver_payout=int(actual_fee * 0.75) if actual_fee else 700,
            )

        # Transaction de paiement enregistrée
        PaymentTransaction.objects.create(
            order=order,
            provider=payment_method if payment_method != 'cash_on_delivery' else 'cash',
            phone_number=delivery_phone,
            amount=total_amount,
            status='successful' if payment_method != 'cash_on_delivery' else 'pending',
            reference_code=f"REF-CM-{order.delivery_pin}-AUTH"
        )

        # Nettoyage du panier
        request.session['cart'] = {}
        request.session.modified = True

        mode_str = "en livraison à domicile" if delivery_type == 'delivery' else "à emporter (retrait sur place)"

        # Notifications automatiques
        Notification.objects.create(
            recipient=request.user,
            order=order,
            title="Commande enregistrée",
            message=f"Votre commande #{order.order_number} ({mode_str}) a été enregistrée avec succès. Montant: {order.total_amount} FCFA.",
            notif_type='order_created'
        )
        if restaurant and restaurant.owner:
            Notification.objects.create(
                recipient=restaurant.owner,
                order=order,
                title="Nouvelle commande reçue",
                message=f"Commande #{order.order_number} ({mode_str}) en attente de vérification et validation.",
                notif_type='order_created'
            )

        messages.success(request, f"Votre commande #{order.order_number} ({mode_str}) a été transmise en cuisine !")
        return redirect('orders:tracking', order_number=order.order_number)

    context = {
        'restaurant': restaurant,
        'dishes': dishes,
        'cart': cart,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total_amount': subtotal + delivery_fee,
    }
    return render(request, 'orders/checkout.html', context)


def order_tracking(request, order_number):
    """Suivi de commande en temps réel avec timeline et carte interactive"""
    order = get_object_or_404(Order, order_number=order_number)
    
    if request.user.is_authenticated:
        is_authorized = (
            request.user == order.client or
            request.user.role in ['restaurant', 'restaurateur'] or
            (hasattr(order, 'delivery_mission') and order.delivery_mission.driver == request.user) or
            request.user.is_platform_admin
        )
        if not is_authorized:
            messages.error(request, "Vous n'avez pas accès à ce suivi de commande.")
            return redirect('core:home')

    delivery = getattr(order, 'delivery_mission', None)

    context = {
        'order': order,
        'delivery': delivery,
    }
    return render(request, 'orders/tracking.html', context)


def order_status_api(request, order_number):
    """Endpoint API JSON pour le rafraîchissement temps réel sans rechargement de page"""
    order = get_object_or_404(Order, order_number=order_number)
    delivery = getattr(order, 'delivery_mission', None)
    restaurant = order.restaurant or Restaurant.get_solo()

    data = {
        'order_number': order.order_number,
        'status': order.status,
        'status_display': order.get_status_display(),
        'progress_percentage': order.progress_percentage,
        'delivery_type': order.delivery_type,
        'payment_status': order.get_payment_status_display(),
        'driver_assigned': bool(delivery and delivery.driver),
        'driver_name': delivery.driver.get_full_name() if (delivery and delivery.driver) else "Recherche en cours",
        'driver_phone': delivery.driver.phone if (delivery and delivery.driver) else "",
        'driver_lat': delivery.current_latitude if delivery else None,
        'driver_lng': delivery.current_longitude if delivery else None,
        'pickup_lat': delivery.pickup_latitude if delivery else (restaurant.latitude if restaurant else 4.051),
        'pickup_lng': delivery.pickup_longitude if delivery else (restaurant.longitude if restaurant else 9.708),
        'dropoff_lat': delivery.dropoff_latitude if delivery else None,
        'dropoff_lng': delivery.dropoff_longitude if delivery else None,
    }
    return JsonResponse(data)


@login_required
def order_history(request):
    """Historique des commandes du client connecté"""
    orders = Order.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})


@login_required
@require_POST
def cancel_order(request, order_number):
    """Annulation de commande selon les conditions autorisées"""
    order = get_object_or_404(Order, order_number=order_number, client=request.user)
    
    if not order.can_be_cancelled:
        messages.error(request, "Cette commande ne peut plus être annulée car sa préparation est déjà entamée ou elle est en livraison.")
        return redirect('orders:tracking', order_number=order.order_number)

    order.status = 'annulee'
    order.save()

    if hasattr(order, 'delivery_mission'):
        mission = order.delivery_mission
        mission.status = 'echec'
        mission.save()

    messages.info(request, f"La commande #{order.order_number} a bien été annulée.")
    return redirect('orders:tracking', order_number=order.order_number)


@login_required
def invoice_detail_view(request, order_number):
    """Consultation du reçu / facture officiel dans le navigateur"""
    order = get_object_or_404(Order, order_number=order_number)
    is_authorized = (
        request.user == order.client or
        request.user.role in ['restaurant', 'restaurateur', 'admin'] or
        request.user.is_superuser
    )
    if not is_authorized:
        messages.error(request, "Vous n'avez pas accès à ce reçu.")
        return redirect('orders:history')

    restaurant = order.restaurant or Restaurant.get_solo()
    return render(request, 'orders/facture.html', {'order': order, 'restaurant': restaurant})


@login_required
def invoice_pdf_view(request, order_number):
    """Téléchargement du reçu / facture officiel en PDF haute fidélité (ReportLab)"""
    order = get_object_or_404(Order, order_number=order_number)
    is_authorized = (
        request.user == order.client or
        request.user.role in ['restaurant', 'restaurateur', 'admin'] or
        request.user.is_superuser
    )
    if not is_authorized:
        messages.error(request, "Vous n'avez pas accès à ce reçu.")
        return redirect('orders:history')

    pdf_bytes = generate_invoice_pdf(order)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"Facture_{order.order_number}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

