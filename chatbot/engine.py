import re
from restaurants.models import Dish, Restaurant
from orders.models import Order

def process_chat_message(message_text, user=None):
    """
    Moteur de dialogue culinaire pour le conseiller virtuel 'Le Gout'.
    Répond avec pertinence culturelle, s'appuie EXCLUSIVEMENT sur les données réelles en base
    et propose des liens dynamiques fiables.
    """
    text = message_text.lower().strip()
    
    # 1. Vérification d'un numéro de commande (ex: RG-260927-4812)
    order_match = re.search(r'rg-\d{6}-\d{4}', text)
    if order_match:
        order_num = order_match.group(0).upper()
        order = Order.objects.filter(order_number=order_num).select_related('restaurant').first()
        if order:
            return {
                'reply': (
                    f"Akié ! J'ai bien retrouvé ta commande <strong>#{order.order_number}</strong> chez <em>{order.restaurant.name}</em>.<br>"
                    f"Statut actuel : <strong>{order.get_status_display()}</strong>.<br>"
                    f"Montant total : <strong>{order.total_amount} FCFA</strong> ({order.get_payment_method_display()}).<br>"
                    f"Adresse de livraison : {order.delivery_neighborhood} ({order.delivery_landmark})."
                ),
                'link': f"/commandes/suivi/{order.order_number}/",
                'link_text': f"Voir le suivi en direct de la commande #{order.order_number}"
            }
        else:
            return {
                'reply': f"Mon cher, je ne trouve pas la commande #{order_num} dans nos marmites. Vérifie bien les chiffres s'il te plaît !",
            }

    # 2. Demande de suivi générique si l'utilisateur est connecté
    if any(k in text for k in ['ou est ma commande', 'ou en est ma commande', 'suivre ma commande', 'statut commande', 'ma commande']):
        if user and user.is_authenticated:
            last_order = Order.objects.filter(client=user).select_related('restaurant').order_by('-created_at').first()
            if last_order:
                return {
                    'reply': (
                        f"Voici ta dernière commande en cours <strong>#{last_order.order_number}</strong> passée chez <em>{last_order.restaurant.name}</em>.<br>"
                        f"Elle est actuellement : <strong>{last_order.get_status_display()}</strong>.<br>"
                        f"Code secret à donner au livreur : <span class='font-mono font-bold text-[#A83B19]'>{last_order.delivery_pin}</span>."
                    ),
                    'link': f"/commandes/suivi/{last_order.order_number}/",
                    'link_text': "Suivre ma commande sur la carte GPS"
                }
            else:
                return {
                    'reply': "Tu n'as pas encore passé de commande aujourd'hui mon cher. Regarde nos menus, les marmites bouillonnent !",
                    'link': "/restaurants/",
                    'link_text': "Parcourir la liste des restaurants"
                }

    # 3. Demandes de plats spécifiques (interrogation 100% dynamique de la base)
    if 'ndol' in text or 'ndole' in text:
        dishes = Dish.objects.filter(name__icontains='ndol', is_available=True).select_related('restaurant')[:3]
        if dishes:
            cards = [f"• <strong>{d.name}</strong> ({d.price} FCFA) chez <em>{d.restaurant.name}</em> ({d.restaurant.neighborhood}, {d.restaurant.city})" for d in dishes]
            first_resto = dishes[0].restaurant
            return {
                'reply': (
                    "Ah le Ndolè national ! C'est la fierté du terroir Sawa et de tout le Cameroun.<br>"
                    "Nos chefs le préparent avec des feuilles fraîches bien lavées au sel gemme et une pâte d'arachide mijotée onctueuse.<br><br>"
                    + "<br>".join(cards) + "<br><br>Tu veux le déguster avec des miondo ou du plantain mûr frit ?"
                ),
                'link': f"/restaurants/{first_resto.slug}/",
                'link_text': f"Voir le menu chez {first_resto.name}"
            }
        else:
            return {
                'reply': (
                    "Ah le Ndolè national ! C'est la fierté du terroir Sawa et de tout le Cameroun.<br>"
                    "Aucun restaurant n'a encore enregistré de Ndolè sur la carte pour l'instant. "
                    "Consulte régulièrement nos établissements pour découvrir les arrivages de la marée !"
                ),
                'link': "/restaurants/",
                'link_text': "Parcourir les restaurants"
            }

    if any(k in text for k in ['poisson', 'brais', 'carpe', 'bar ']):
        dishes = Dish.objects.filter(
            name__iregex=r'(poisson|brais|carpe|bar)',
            is_available=True
        ).select_related('restaurant')[:3]
        if dishes:
            cards = [f"• <strong>{d.name}</strong> ({d.price} FCFA) chez <em>{d.restaurant.name}</em> ({d.restaurant.neighborhood})" for d in dishes]
            first_resto = dishes[0].restaurant
            return {
                'reply': (
                    "Hum ! L'odeur de la braise au charbon de bois naturel !<br>"
                    "Les poissons et viandes sont marinés aux épices du pays (njangsa, rondelles, poivre blanc de Penja) puis dorés sur braises ardentes :<br><br>"
                    + "<br>".join(cards)
                ),
                'link': f"/restaurants/{first_resto.slug}/",
                'link_text': f"Commander chez {first_resto.name}"
            }
        else:
            return {
                'reply': (
                    "Hum ! Rien ne vaut un bon poisson braisé au feu de bois avec miondo et piment jaune pilé.<br>"
                    "Aucune grillade n'est actuellement au menu des établissements enregistrés. Vérifie la carte de nos restaurants !"
                ),
                'link': "/restaurants/",
                'link_text': "Consulter les restaurants"
            }

    if 'koki' in text:
        dishes = Dish.objects.filter(name__icontains='koki', is_available=True).select_related('restaurant')[:2]
        if dishes:
            cards = [f"• <strong>{d.name}</strong> ({d.price} FCFA) chez <em>{d.restaurant.name}</em>" for d in dishes]
            return {
                'reply': (
                    "Le Koki chaud dans la feuille de bananier avec l'huile rouge vierge non blanchie !<br>"
                    "Cuit à l'étouffée pour une texture fondante :<br><br>"
                    + "<br>".join(cards)
                ),
                'link': f"/restaurants/{dishes[0].restaurant.slug}/",
                'link_text': f"Voir le menu chez {dishes[0].restaurant.name}"
            }
        else:
            return {
                'reply': (
                    "Le Koki chaud dans la feuille de bananier avec l'huile rouge vierge ! "
                    "Ce plat du terroir n'est pas encore enregistré sur la plateforme par nos partenaires. "
                    "Explore nos restaurants pour découvrir les spécialités disponibles !"
                ),
                'link': "/restaurants/",
                'link_text': "Voir les restaurants"
            }

    if 'taro' in text or 'sauce jaune' in text:
        dishes = Dish.objects.filter(name__iregex=r'(taro|sauce jaune)', is_available=True).select_related('restaurant')[:2]
        if dishes:
            cards = [f"• <strong>{d.name}</strong> ({d.price} FCFA) chez <em>{d.restaurant.name}</em>" for d in dishes]
            return {
                'reply': (
                    "Le plat royal des Grassfields ! Taro pilé chaud nappé de sa sauce jaune aux épices ancestrales :<br><br>"
                    + "<br>".join(cards)
                ),
                'link': f"/restaurants/{dishes[0].restaurant.slug}/",
                'link_text': f"Commander chez {dishes[0].restaurant.name}"
            }
        else:
            return {
                'reply': (
                    "Le plat royal des Grassfields ! Le Taro pilé chaud nappé de son onctueuse sauce jaune aux 7 épices du village.<br>"
                    "Aucun établissement n'en propose sur sa carte pour le moment."
                ),
                'link': "/restaurants/",
                'link_text': "Découvrir nos restaurants"
            }

    if 'soya' in text or 'brochette' in text or 'kankan' in text:
        dishes = Dish.objects.filter(name__iregex=r'(soya|brochette|kankan)', is_available=True).select_related('restaurant')[:2]
        if dishes:
            cards = [f"• <strong>{d.name}</strong> ({d.price} FCFA) chez <em>{d.restaurant.name}</em>" for d in dishes]
            return {
                'reply': (
                    "Le vrai Soya de rue mariné au piment kankan pur !<br><br>" + "<br>".join(cards)
                ),
                'link': f"/restaurants/{dishes[0].restaurant.slug}/",
                'link_text': f"Voir chez {dishes[0].restaurant.name}"
            }
        else:
            return {
                'reply': (
                    "Le vrai Soya grillé au feu de bois et saupoudré de kankan artisanal ! "
                    "Nos braiseurs partenaires n'ont pas encore mis de brochettes en ligne aujourd'hui."
                ),
                'link': "/restaurants/",
                'link_text': "Consulter la liste des restaurants"
            }

    if 'poulet dg' in text or 'dg' in text or 'directeur' in text:
        dishes = Dish.objects.filter(name__icontains='dg', is_available=True).select_related('restaurant')[:2]
        if dishes:
            cards = [f"• <strong>{d.name}</strong> ({d.price} FCFA) chez <em>{d.restaurant.name}</em>" for d in dishes]
            return {
                'reply': (
                    "Le Poulet D.G. (Directeur Général) ! C'est le classique des grandes occasions avec plantains mûrs dorés et petits légumes :<br><br>"
                    + "<br>".join(cards)
                ),
                'link': f"/restaurants/{dishes[0].restaurant.slug}/",
                'link_text': f"Commander chez {dishes[0].restaurant.name}"
            }
        else:
            return {
                'reply': (
                    "Le savoureux Poulet D.G. (Directeur Général) ! Poêlée de poulet fermier doré, rondelles de plantain mûr fondant et réduction épicée.<br>"
                    "Ce plat n'est pas encore disponible sur les menus du jour."
                ),
                'link': "/restaurants/",
                'link_text': "Explorer nos cartes"
            }

    # 4. Filtre piment / enfants / doux
    if any(k in text for k in ['sans piment', 'pas de piment', 'enfant', 'doux', 'bebe']):
        mild_dishes = Dish.objects.filter(spice_level='doux', is_available=True).select_related('restaurant')[:3]
        if mild_dishes:
            items_desc = "<br>".join([f"• <strong>{d.name}</strong> ({d.price} FCFA chez {d.restaurant.name})" for d in mild_dishes])
            return {
                'reply': (
                    "Tu as raison mon cher, pour les enfants ou les estomacs délicats, voici nos plats sans piment piquant :<br><br>"
                    + items_desc + "<br><br>Tous ces plats sont garantis savoureux sans brûlure de piment !"
                ),
                'link': "/restaurants/",
                'link_text': "Choisir un restaurant"
            }
        else:
            return {
                'reply': (
                    "Pour les enfants ou les estomacs délicats, nos restaurateurs préparent souvent des sauces douces sur mesure. "
                    "N'hésite pas à le préciser dans les consignes de ta commande !"
                ),
                'link': "/restaurants/",
                'link_text': "Consulter les restaurants"
            }

    # 5. Petits budgets (< 3000 FCFA)
    if any(k in text for k in ['pas cher', 'petit budget', 'economique', 'etudiant', '1500', '2000', 'moins de 3000']):
        cheap_dishes = Dish.objects.filter(price__lte=3000, is_available=True).select_related('restaurant').order_by('price')[:3]
        if cheap_dishes:
            items_desc = "<br>".join([f"• <strong>{d.name}</strong> — {d.price} FCFA ({d.restaurant.name})" for d in cheap_dishes])
            return {
                'reply': (
                    "On mange bien à tous les prix chez nous ! Voici d'excellents plats authentiques à prix tout doux :<br><br>"
                    + items_desc + "<br><br>De quoi se régaler copieusement sans vider les poches !"
                ),
                'link': "/restaurants/",
                'link_text': "Voir les restaurants"
            }
        else:
            return {
                'reply': (
                    "Nos partenaires proposent régulièrement des plats et formules économiques. "
                    "Parcours nos établissements pour découvrir les tarifs du jour !"
                ),
                'link': "/restaurants/",
                'link_text': "Voir les restaurants"
            }

    # 6. Modes de paiement
    if any(k in text for k in ['payer', 'paiement', 'momo', 'orange', 'cinetpay', 'espece', 'cash']):
        return {
            'reply': (
                "Pour régler ta commande, c'est ultra simple et sécurisé :<br>"
                "1. <strong>MTN Mobile Money</strong> (*126#)<br>"
                "2. <strong>Orange Money</strong> (*150#)<br>"
                "3. <strong>CinetPay</strong> (Cartes bancaires / MoMo)<br>"
                "4. <strong>Paiement en espèces à la livraison</strong> directement au coursier.<br><br>"
                "Tu reçois la confirmation instantanément !"
            )
        }

    # 7. Zones et délais de livraison
    if any(k in text for k in ['livraison', 'delai', 'temps', 'combien de temps', 'quartier', 'zone', 'yaounde', 'douala']):
        return {
            'reply': (
                "Nos livreurs sillonnent les quartiers de <strong>Douala</strong> et <strong>Yaoundé</strong>.<br>"
                "Délai moyen constaté : <strong>35 à 50 minutes</strong> selon la cuisson du plat.<br>"
                "Les plats sont transportés dans des caissons isothermes pour arriver bien chauds !"
            )
        }

    # Réponse par défaut chaleureuse
    return {
        'reply': (
            "Bonjour ! Votre conseiller culinaire <strong>Le Gout</strong> est là pour vous guider.<br>"
            "Vous pouvez me poser des questions comme :<br>"
            "• <em>'Quel est le meilleur Ndolè ?'</em><br>"
            "• <em>'Un plat de poisson braisé au feu de bois'</em><br>"
            "• <em>'Un plat pas pimenté pour les enfants'</em><br>"
            "• <em>'Des plats à petit budget'</em><br>"
            "• <em>'Où en est ma commande ?'</em><br><br>"
            "Dites-moi ce qui vous ferait plaisir aujourd'hui !"
        ),
        'link': "/#menu",
        'link_text': "Consulter la carte Le Gout"
    }
