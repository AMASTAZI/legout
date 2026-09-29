from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='fcfa')
def fcfa(value):
    """Formate un nombre en devise FCFA: 4500 -> 4 500 FCFA"""
    try:
        val = int(value)
        formatted = f"{val:,}".replace(",", " ")
        return f"{formatted} FCFA"
    except (ValueError, TypeError):
        return f"{value} FCFA"

@register.filter(name='multiply')
def multiply(qty, price):
    try:
        return int(qty) * int(price)
    except (ValueError, TypeError):
        return 0

@register.filter(name='status_badge')
def status_badge(status):
    """Génère le badge HTML avec style sobre et authentique selon le statut"""
    badges = {
        'en_attente_paiement': ('bg-amber-50 text-amber-800 border-amber-300', 'En attente de paiement'),
        'payee': ('bg-blue-100 text-blue-900 border-blue-300', 'Payée - À valider'),
        'en_attente': ('bg-amber-100 text-amber-900 border-amber-300', 'En attente'),
        'validee': ('bg-emerald-100 text-emerald-900 border-emerald-300', 'Validée cuisine'),
        'confirmee': ('bg-emerald-100 text-emerald-900 border-emerald-300', 'Confirmée'),
        'en_preparation': ('bg-orange-100 text-orange-900 border-orange-300', 'En préparation'),
        'prete': ('bg-cyan-100 text-cyan-900 border-cyan-300', 'Prête en cuisine'),
        'en_livraison': ('bg-indigo-100 text-indigo-900 border-indigo-300', 'En cours de livraison'),
        'livree': ('bg-stone-200 text-stone-900 border-stone-400', 'Livrée'),
        'refusee': ('bg-rose-100 text-rose-900 border-rose-300 font-bold', 'Refusée & Remboursée'),
        'annulee': ('bg-rose-100 text-rose-900 border-rose-300', 'Annulée'),
    }
    css_class, label = badges.get(status, ('bg-stone-100 text-stone-800 border-stone-300', status))
    html = f'<span class="inline-flex items-center px-2.5 py-1 text-xs font-semibold rounded-md border {css_class}">{label}</span>'
    return mark_safe(html)

@register.filter(name='get_item')
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        val = dictionary.get(str(key), dictionary.get(key))
        if isinstance(val, dict):
            return val.get('quantity', 1)
        return val
    return None

