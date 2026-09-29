from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from restaurants.models import Restaurant, Dish, Category
from orders.models import Order, OrderItem
from delivery.models import Delivery
from payments.models import PaymentTransaction

User = get_user_model()

class MonoRestaurantTestSuite(TestCase):
    def setUp(self):
        self.c = Client()

        # 1. Utilisateurs
        self.client_user = User.objects.create_user(
            username='sophie_client',
            email='sophie@test.cm',
            password='Password123!',
            role='client',
            city='Douala',
            neighborhood='Bonapriso',
            phone='+237 694 00 11 22',
        )

        self.resto_user = User.objects.create_user(
            username='chef_pierre',
            email='chef@test.cm',
            password='Password123!',
            role='restaurateur',
            city='Douala',
            neighborhood='Akwa',
        )

        self.driver_user = User.objects.create_user(
            username='martial_coursier',
            email='martial@test.cm',
            password='Password123!',
            role='livreur',
            city='Douala',
            phone='+237 677 11 22 33',
        )

        self.admin_user = User.objects.create_superuser(
            username='admin_boss',
            email='admin@test.cm',
            password='Password123!',
        )

        # 2. Restaurant Singleton
        self.restaurant = Restaurant.objects.create(
            owner=self.resto_user,
            name='Le Gout',
            slug='le-gout',
            tagline='La haute gastronomie camerounaise',
            description='Recettes traditionnelles et braises au bois d\'arbre à pain.',
            city='Douala',
            neighborhood='Akwa',
            address='142 Boulevard de la Liberté',
            phone='+237 690 12 34 56',
            delivery_fee=1000,
            min_order_amount=2000,
            delivery_zone='Douala (Akwa, Bonapriso, Deido, Bonamoussadi)',
            is_open=True,
            is_approved=True,
        )

        self.cat_mets = Category.objects.create(name='Mets Traditionnels')
        self.cat_boissons = Category.objects.create(name='Boissons du Terroir')

        # 3. Plats & Boissons
        self.dish_ndole = Dish.objects.create(
            restaurant=self.restaurant,
            category=self.cat_mets,
            product_type='plat',
            name='Ndolè Royal Terroir',
            description='Feuilles fraîches, pâte d\'arachide et crevettes de Manoka',
            price=5000,
            spice_level='moyen',
            authentic_origin='Littoral (Sawa)',
            sides_included='Miondo d\'Édéa (4 bâtons)',
            is_available=True,
            is_featured=True,
        )

        self.drink_folere = Dish.objects.create(
            restaurant=self.restaurant,
            category=self.cat_boissons,
            product_type='boisson',
            name='Jus de Foléré Maison (1L)',
            description='Infusion d\'hibiscus sauvage et menthe fraîche',
            price=1500,
            spice_level='doux',
            authentic_origin='Nord (Sahel)',
            sides_included='Bouteille fraîche',
            is_available=True,
        )

    # ----------------------------------------------------
    # TEST 1: Inscription client (rôle non falsifiable)
    # ----------------------------------------------------
    def test_client_registration_role_cannot_be_tampered(self):
        """
        Vérifie qu'un attaquant tentant d'injecter role='admin' ou role='restaurateur'
        dans la requête POST d'inscription est strictement forcé en role='client'.
        """
        response = self.c.post(reverse('accounts:register'), {
            'username': 'hacker_user',
            'first_name': 'Tentative',
            'last_name': 'Hack',
            'email': 'hack@test.cm',
            'phone': '+237 699 99 99 99',
            'city': 'Douala',
            'neighborhood': 'Akwa',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
            'role': 'admin',  # Tentative d'élévation de privilèges
        })
        self.assertEqual(response.status_code, 302)
        created_user = User.objects.get(username='hacker_user')
        self.assertEqual(created_user.role, 'client')
        self.assertFalse(created_user.is_superuser)
        self.assertFalse(created_user.is_staff)

    # ----------------------------------------------------
    # TEST 2: CustomUserManager create_superuser
    # ----------------------------------------------------
    def test_createsuperuser_automatically_assigns_admin_role(self):
        """
        Vérifie que CustomUserManager surcharge create_superuser() pour
        affecter automatiquement role='admin'.
        """
        super_admin = User.objects.create_superuser(
            username='system_admin',
            email='sysadmin@test.cm',
            password='AdminPassword123!'
        )
        self.assertEqual(super_admin.role, 'admin')
        self.assertTrue(super_admin.is_staff)
        self.assertTrue(super_admin.is_superuser)

    # ----------------------------------------------------
    # TEST 3: Création de comptes staff par l'admin + must_change_password
    # ----------------------------------------------------
    def test_admin_creates_staff_user_with_forced_password_change(self):
        """
        L'admin crée un compte livreur avec un mot de passe temporaire.
        Le compte créé doit obligatoirement changer son mot de passe à la première connexion.
        """
        self.c.login(username='admin_boss', password='Password123!')
        create_resp = self.c.post(reverse('dashboard:admin_create_staff'), {
            'username': 'nouveau_livreur',
            'first_name': 'Alain',
            'last_name': 'Foko',
            'email': 'alain@test.cm',
            'phone': '+237 670 00 11 22',
            'role': 'livreur',
            'city': 'Douala',
            'neighborhood': 'Deido',
            'temporary_password': 'TempPassword123!',
        })
        self.assertEqual(create_resp.status_code, 302)
        new_driver = User.objects.get(username='nouveau_livreur')
        self.assertEqual(new_driver.role, 'livreur')
        self.assertTrue(new_driver.must_change_password)

        # Première connexion du livreur
        self.c.logout()
        login_resp = self.c.post(reverse('accounts:login'), {
            'username': 'nouveau_livreur',
            'password': 'TempPassword123!',
        })
        # Doit être redirigé vers le changement de mot de passe obligatoire
        self.assertRedirects(login_resp, reverse('accounts:force_password_change'))

        # Soumission du nouveau mot de passe
        change_resp = self.c.post(reverse('accounts:force_password_change'), {
            'new_password': 'DefinitivePassword123!',
            'confirm_password': 'DefinitivePassword123!',
        })
        new_driver.refresh_from_db()
        self.assertFalse(new_driver.must_change_password)
        # Redirigé vers son dashboard livreur
        self.assertRedirects(change_resp, reverse('dashboard:driver'))

    # ----------------------------------------------------
    # TEST 4: Redirection backend stricte par rôle
    # ----------------------------------------------------
    def test_backend_role_redirection_on_login(self):
        """Vérifie l'aiguillage automatique vers le dashboard adéquat selon le rôle en base"""
        # 1. Admin
        self.c.login(username='admin_boss', password='Password123!')
        resp = self.c.get(reverse('accounts:login'))
        self.assertRedirects(resp, reverse('dashboard:admin'))
        self.c.logout()

        # 2. Restaurateur
        self.c.login(username='chef_pierre', password='Password123!')
        resp = self.c.get(reverse('accounts:login'))
        self.assertRedirects(resp, reverse('dashboard:restaurant'))
        self.c.logout()

        # 3. Livreur
        self.c.login(username='martial_coursier', password='Password123!')
        resp = self.c.get(reverse('accounts:login'))
        self.assertRedirects(resp, reverse('dashboard:driver'))
        self.c.logout()

    # ----------------------------------------------------
    # TEST 5: Protection des dashboards (permissions mixins)
    # ----------------------------------------------------
    def test_dashboard_permission_protection(self):
        """Un client ne peut pas accéder aux dashboards d'administration ou de cuisine"""
        self.c.login(username='sophie_client', password='Password123!')
        
        admin_resp = self.c.get(reverse('dashboard:admin'))
        self.assertEqual(admin_resp.status_code, 302)  # Redirigé vers dispatch

        resto_resp = self.c.get(reverse('dashboard:restaurant'))
        self.assertEqual(resto_resp.status_code, 302)

        driver_resp = self.c.get(reverse('dashboard:driver'))
        self.assertEqual(driver_resp.status_code, 302)
        self.c.logout()

    # ----------------------------------------------------
    # TEST 6: Cycle de commande - Mode Livraison à domicile
    # ----------------------------------------------------
    def test_order_lifecycle_delivery_mode(self):
        """Cycle complet : ajout panier, commande livraison, acceptation coursier et validation PIN"""
        self.c.login(username='sophie_client', password='Password123!')

        # 1. Ajout au panier
        self.c.post(reverse('orders:add_to_cart', args=[self.dish_ndole.id]), {'quantity': 1})
        self.c.post(reverse('orders:add_to_cart', args=[self.drink_folere.id]), {'quantity': 1})

        # 2. Validation de commande en livraison
        checkout_resp = self.c.post(reverse('orders:checkout'), {
            'delivery_type': 'delivery',
            'delivery_city': 'Douala',
            'delivery_neighborhood': 'Bonapriso',
            'delivery_address': 'Rue des Manguiers',
            'delivery_landmark': 'Face pharmacie de l\'Aéroport',
            'delivery_phone': '+237 694 00 11 22',
            'payment_method': 'mtn_momo',
            'client_notes': 'Servir bien chaud',
        })
        self.assertEqual(checkout_resp.status_code, 302)
        order = Order.objects.get(client=self.client_user)
        self.assertEqual(order.delivery_type, 'delivery')
        self.assertEqual(order.delivery_fee, 1000)
        self.assertEqual(order.total_amount, 7500)  # 5000 (ndole) + 1500 (folere) + 1000 (livraison) = 7500
        
        # Mission de livraison créée
        delivery = Delivery.objects.get(order=order)
        self.assertEqual(delivery.status, 'recherche_livreur')
        self.c.logout()

        # 3. Le Restaurateur avance le statut en cuisine
        self.c.login(username='chef_pierre', password='Password123!')
        self.c.post(reverse('dashboard:restaurant_order_status', args=[order.id]), {'status': 'confirmee'})
        order.refresh_from_db()
        self.assertEqual(order.status, 'confirmee')
        self.c.post(reverse('dashboard:restaurant_order_status', args=[order.id]), {'status': 'prete'})
        order.refresh_from_db()
        self.assertEqual(order.status, 'prete')
        self.c.logout()

        # 4. Le Livreur accepte la course et valide avec le code PIN client
        self.c.login(username='martial_coursier', password='Password123!')
        self.c.post(reverse('dashboard:driver_accept', args=[delivery.id]))
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, 'assignee')
        self.assertEqual(delivery.driver, self.driver_user)

        # Validation PIN
        pin_resp = self.c.post(reverse('dashboard:driver_status', args=[delivery.id]), {
            'action': 'confirm_pin',
            'pin': order.delivery_pin,
        })
        order.refresh_from_db()
        delivery.refresh_from_db()
        self.assertEqual(order.status, 'livree')
        self.assertEqual(delivery.status, 'livree')
        self.c.logout()

    # ----------------------------------------------------
    # TEST 7: Cycle de commande - Mode Retrait sur place (À emporter)
    # ----------------------------------------------------
    def test_order_lifecycle_pickup_mode(self):
        """En mode retrait, aucun frais de livraison n'est facturé et aucune mission coursier n'est créée"""
        self.c.login(username='sophie_client', password='Password123!')

        self.c.post(reverse('orders:add_to_cart', args=[self.dish_ndole.id]), {'quantity': 1})
        checkout_resp = self.c.post(reverse('orders:checkout'), {
            'delivery_type': 'pickup',
            'delivery_phone': '+237 694 00 11 22',
            'payment_method': 'cash_on_delivery',
        })
        self.assertEqual(checkout_resp.status_code, 302)
        order = Order.objects.filter(client=self.client_user, delivery_type='pickup').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.delivery_fee, 0)
        self.assertEqual(order.total_amount, 5000)
        # Pas de mission de livraison
        self.assertFalse(Delivery.objects.filter(order=order).exists())

    # ----------------------------------------------------
    # TEST 8: Bonus de bienvenue simulé (10 000 FCFA attribués automatiquement)
    # ----------------------------------------------------
    def test_welcome_bonus_attribution_at_registration(self):
        """À l'inscription, chaque nouveau client reçoit automatiquement un solde fictif de 10 000 FCFA"""
        resp = self.c.post(reverse('accounts:register'), {
            'username': 'nouveau_client',
            'first_name': 'Mireille',
            'last_name': 'Ewonde',
            'email': 'mireille@test.cm',
            'phone': '+237 690 99 88 77',
            'city': 'Douala',
            'neighborhood': 'Bonamoussadi',
            'password': 'SecurePassword123!',
            'password_confirm': 'SecurePassword123!',
        })
        self.assertEqual(resp.status_code, 302)
        new_client = User.objects.get(username='nouveau_client')
        self.assertEqual(new_client.role, 'client')
        self.assertEqual(new_client.wallet_balance, 10000)

    # ----------------------------------------------------
    # TEST 9: Paiement par solde simulé & Génération automatique de facture PDF
    # ----------------------------------------------------
    def test_order_with_simulated_wallet_and_auto_invoice_pdf(self):
        """Le client paie avec son solde de test (10 000 FCFA), la facture est auto-générée et téléchargeable en PDF"""
        self.client_user.wallet_balance = 10000
        self.client_user.save()
        self.c.login(username='sophie_client', password='Password123!')

        # Panier : 1x Foléré (1500 FCFA) < 2000 FCFA -> En arrière-plan : 10% (150 F) + Livraison (1000 F) = 1150 F
        # Total : 1500 + 1150 = 2650 FCFA
        self.c.post(reverse('orders:add_to_cart', args=[self.drink_folere.id]), {'quantity': 1})
        checkout_resp = self.c.post(reverse('orders:checkout'), {
            'delivery_type': 'delivery',
            'delivery_city': 'Douala',
            'delivery_neighborhood': 'Bonapriso',
            'delivery_address': 'Rue des Palmiers',
            'delivery_landmark': 'Face pharmacie',
            'delivery_phone': '+237 694 00 11 22',
            'payment_method': 'wallet',
        })
        self.assertEqual(checkout_resp.status_code, 302)

        # Vérification débit du solde portefeuille
        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.wallet_balance, 7350)  # 10 000 - 2 650 = 7 350 FCFA

        # Commande payée et en attente de validation
        order = Order.objects.filter(client=self.client_user, payment_method='wallet').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.payment_status, 'paid')
        self.assertEqual(order.status, 'payee')
        self.assertEqual(order.delivery_fee, 1150)
        self.assertEqual(order.total_amount, 2650)

        # Facture générée automatiquement
        from orders.models import Invoice
        self.assertTrue(hasattr(order, 'invoice'))
        invoice = order.invoice
        self.assertEqual(invoice.total_amount, 2650)
        self.assertFalse(invoice.is_refunded)
        self.assertTrue(invoice.invoice_number.startswith('FAC-'))

        # Téléchargement PDF
        pdf_resp = self.c.get(reverse('orders:invoice_pdf', args=[order.order_number]))
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp['Content-Type'], 'application/pdf')
        self.assertTrue(len(pdf_resp.content) > 1000)

        # Consultation HTML
        html_resp = self.c.get(reverse('orders:invoice_detail', args=[order.order_number]))
        self.assertEqual(html_resp.status_code, 200)
        self.c.logout()

    # ----------------------------------------------------
    # TEST 10: Rejet si solde portefeuille insuffisant
    # ----------------------------------------------------
    def test_order_rejected_if_wallet_balance_insufficient(self):
        """Le client ne peut pas commander avec le portefeuille si son solde est inférieur au total"""
        self.client_user.wallet_balance = 1000  # Moins que les 2500 FCFA nécessaires
        self.client_user.save()
        self.c.login(username='sophie_client', password='Password123!')

        self.c.post(reverse('orders:add_to_cart', args=[self.drink_folere.id]), {'quantity': 1})
        resp = self.c.post(reverse('orders:checkout'), {
            'delivery_type': 'delivery',
            'delivery_city': 'Douala',
            'delivery_neighborhood': 'Bonapriso',
            'delivery_address': 'Rue des Palmiers',
            'delivery_landmark': 'Face pharmacie',
            'delivery_phone': '+237 694 00 11 22',
            'payment_method': 'wallet',
        })
        # Reste sur la page avec message d'erreur
        self.assertEqual(resp.status_code, 200)
        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.wallet_balance, 1000)
        self.assertFalse(Order.objects.filter(client=self.client_user, payment_method='wallet').exists())
        self.c.logout()

    # ----------------------------------------------------
    # TEST 11: Workflow Restaurateur (Validation -> Livreur, Refus -> Remboursement automatique)
    # ----------------------------------------------------
    def test_restaurateur_validation_and_refusal_refund_workflow(self):
        """Vérifie la validation vers les livreurs et le refus avec remboursement automatique du solde"""
        # 1. Le client passe une commande payée par solde
        self.client_user.wallet_balance = 10000
        self.client_user.save()
        self.c.login(username='sophie_client', password='Password123!')
        self.c.post(reverse('orders:add_to_cart', args=[self.dish_ndole.id]), {'quantity': 1})
        self.c.post(reverse('orders:checkout'), {
            'delivery_type': 'delivery',
            'delivery_city': 'Douala',
            'delivery_neighborhood': 'Bonapriso',
            'delivery_address': 'Rue des Palmiers',
            'delivery_landmark': 'Face pharmacie',
            'delivery_phone': '+237 694 00 11 22',
            'payment_method': 'wallet',
        })
        order = Order.objects.filter(client=self.client_user, payment_method='wallet').first()
        self.assertEqual(order.status, 'payee')
        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.wallet_balance, 4000)  # 10000 - 6000 (5000+1000) = 4000
        self.c.logout()

        # 2. Le restaurateur valide d'abord la commande -> transmise aux livreurs
        self.c.login(username='chef_pierre', password='Password123!')
        val_resp = self.c.post(reverse('dashboard:restaurant_validate_order', args=[order.id]))
        self.assertEqual(val_resp.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'validee')
        self.assertTrue(Delivery.objects.filter(order=order, status='recherche_livreur').exists())

        # 3. Si rupture d'ingrédient imprévue : le restaurateur refuse la commande -> remboursement automatique
        ref_resp = self.c.post(reverse('dashboard:restaurant_refuse_order', args=[order.id]), {
            'reason': 'Rupture de feuilles de Ndolè fraîches'
        })
        self.assertEqual(ref_resp.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'refusee')
        self.assertEqual(order.payment_status, 'refunded')

        # Vérification que le solde du client a été recrédité de 6 000 FCFA (4000 + 6000 = 10 000 FCFA)
        self.client_user.refresh_from_db()
        self.assertEqual(self.client_user.wallet_balance, 10000)

        # Facture marquée comme remboursée
        self.assertTrue(order.invoice.is_refunded)

        # Mission de livraison annulée
        self.assertEqual(order.delivery_mission.status, 'echec')
        self.c.logout()

    # ----------------------------------------------------
    # TEST 12: Aucun blocage de commande minimum & Frais 10% + 1000 F en arrière-plan si < 2000 F
    # ----------------------------------------------------
    def test_small_order_under_2000_surcharge_and_no_blocking_message(self):
        """Vérifie qu'il n'y a plus de message bloquant et que 10% + 1000 F de livraison s'appliquent discrètement"""
        self.c.login(username='sophie_client', password='Password123!')

        # Ajout d'un article inférieur à 2000 FCFA (Foléré à 1500 FCFA)
        self.c.post(reverse('orders:add_to_cart', args=[self.drink_folere.id]), {'quantity': 1})

        # Consultation du panier
        cart_resp = self.c.get(reverse('orders:cart'))
        self.assertEqual(cart_resp.status_code, 200)

        # Aucun message de blocage de commande minimum
        self.assertNotContains(cart_resp, 'Le montant minimum de commande')
        self.assertNotContains(cart_resp, 'Montant minimum non atteint')
        self.assertContains(cart_resp, 'Passer à la livraison')

        # Calcul financier discret en arrière-plan : 1500 F + (1000 F + 150 F) = 2650 FCFA
        self.assertEqual(cart_resp.context['subtotal'], 1500)
        self.assertEqual(cart_resp.context['delivery_fee'], 1150)
        self.assertEqual(cart_resp.context['total_amount'], 2650)
        self.assertTrue(cart_resp.context['can_checkout'])

        # Validation de la commande
        checkout_resp = self.c.post(reverse('orders:checkout'), {
            'delivery_type': 'delivery',
            'delivery_city': 'Douala',
            'delivery_neighborhood': 'Akwa',
            'delivery_address': 'Rue Joss',
            'delivery_landmark': 'Face pharmacie',
            'delivery_phone': '+237 694 00 11 22',
            'payment_method': 'cash_on_delivery',
        })
        self.assertEqual(checkout_resp.status_code, 302)

        order = Order.objects.filter(client=self.client_user, payment_method='cash_on_delivery').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.subtotal, 1500)
        self.assertEqual(order.delivery_fee, 1150)
        self.assertEqual(order.total_amount, 2650)
        self.c.logout()
