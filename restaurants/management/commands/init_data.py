from django.core.management.base import BaseCommand
from restaurants.models import Restaurant, Category, Dish

class Command(BaseCommand):
    help = "Initialise les donnees par defaut du restaurant Le Gout si la base est vide"

    def handle(self, *args, **kwargs):
        # 1. Creer le restaurant unique (singleton) s'il n'existe pas
        restaurant = Restaurant.get_solo()
        if not restaurant:
            restaurant = Restaurant.objects.create(
                name="Le Gout",
                tagline="Saveurs Authentiques du Terroir Camerounais",
                description="Véritable Ndolè aux crevettes côtières, poissons braisés marinés au poivre de Penja, Koki pilonné à l'huile vierge, jus naturels et rafraîchissements du terroir. Commandez en ligne, dégustez sur place ou faites-vous livrer chaud.",
                phone="+237 690 12 34 56",
                email="contact@legout.cm",
                city="Douala",
                neighborhood="Akwa",
                address="Boulevard de la Liberté, Akwa",
                price_range="$$",
                opening_time="10:30",
                closing_time="22:30",
                is_open=True,
                is_approved=True,
                delivery_fee=1000,
                min_order_amount=2000,
                delivery_zone="Douala & Yaoundé",
                estimated_delivery_time="35 - 50 min",
                rating=4.9,
                total_reviews=24,
            )
            self.stdout.write(self.style.SUCCESS(f"Restaurant '{restaurant.name}' cree avec succes."))
        else:
            self.stdout.write(f"Restaurant '{restaurant.name}' existe deja.")

        # 2. Creer des categories de base
        cat_plats, _ = Category.objects.get_or_create(name="Plats Chauds & Terroirs", defaults={'display_order': 1})
        cat_grillades, _ = Category.objects.get_or_create(name="Poissons & Grillades", defaults={'display_order': 2})
        cat_boissons, _ = Category.objects.get_or_create(name="Boissons & Rafraichissements", defaults={'display_order': 3})

        # 3. Creer des plats de demonstration si aucun n'existe
        if Dish.objects.count() == 0:
            Dish.objects.create(
                restaurant=restaurant,
                category=cat_plats,
                name="Ndole Royal aux Crevettes & Viande",
                description="Plat emblematique du littoral sawa, prepare avec des feuilles de ndole fraiches, pate d'arachide onctueuse, crevettes sechees et fraiches.",
                price=4500,
                product_type="plat",
                spice_level="moyen",
                authentic_origin="Littoral (Sawa)",
                sides_included="Miondo, Plantains murs frits (alloco), Manioc vapeur",
                is_available=True,
                is_featured=True,
            )
            Dish.objects.create(
                restaurant=restaurant,
                category=cat_grillades,
                name="Bar Braise au Poivre de Penja",
                description="Poisson bar frais marine aux epices du terroir camerounais, grille au feu de bois avec rondelles et pebe, accompagne de piment jaune.",
                price=5000,
                product_type="plat",
                spice_level="releve",
                authentic_origin="Littoral (Sawa)",
                sides_included="Plantains frits, Baton de manioc",
                is_available=True,
                is_featured=True,
            )
            Dish.objects.create(
                restaurant=restaurant,
                category=cat_plats,
                name="Koki Traditionnel du Terroir",
                description="Gateau de haricots niebe moelleux cuit a l'etouffee dans des feuilles de bananier avec huile de palme rouge vierge.",
                price=3000,
                product_type="plat",
                spice_level="doux",
                authentic_origin="Ouest (Bamiléké)",
                sides_included="Bananes plantains vapeur",
                is_available=True,
                is_featured=False,
            )
            Dish.objects.create(
                restaurant=restaurant,
                category=cat_boissons,
                name="Jus de Folere Artisanal (Bissap)",
                description="Infusion artisanale de fleurs d'hibiscus fraiches, menthe sauvage, clous de girofle et ananas naturel.",
                price=1000,
                product_type="boisson",
                spice_level="doux",
                authentic_origin="Pan-Africain",
                is_available=True,
                is_featured=True,
            )
            self.stdout.write(self.style.SUCCESS("Plats et boissons initiaux crees avec succes."))

