# RestoGourmand Cameroun 🇨🇲
### Plateforme Web de Livraison de Repas du Terroir Camerounais & Africain

Application web monolithique Django complète, authentique et réaliste, inspirée de l'expérience culinaire camerounaise (Douala, Yaoundé, Kribi, Bafoussam). L'application respecte scrupuleusement les codes culturels, les prix réels en FCFA, les repères urbains locaux, et élimine tous les clichés et templates SaaS génériques.

---

## 🍛 1. Spécificités Culturelles & Données Réelles

* **Restaurants réels :** *Chez Maman Tantine - L'Oasis du Ndolè* (Akwa, Douala), *Le Braisier du Wouri* (Deido, Douala), *La Marmite Bamiléké* (Bonamoussadi, Douala), *O'Bastos Lounge* (Bastos, Yaoundé), *Le Palais du Soya* (Bépanda, Douala).
* **Plats patrimoniaux authentiques :**
  * Ndolè royal aux crevettes fraîches et silure fumé du Wouri
  * Bar de mer et carpes entières braisés au feu de bois et poivre blanc de Penja
  * Koki traditionnel dans sa feuille de bananier à l'huile rouge vierge
  * Taro sauce jaune bamiléké aux 7 épices et peaux de bœuf (canda)
  * Poulet D.G. (Directeur Général) aux plantains mûrs dorés
  * Soya de bœuf de Bépanda mariné au kankan pur de Maroua
  * Eru au waterleaf et fufu de manioc
  * Jus de Foléré (Bissap) artisanal et gingembre frais
* **Tarification locale réelle :** Prix réels en Francs CFA (de 1 500 FCFA à 8 500 FCFA selon la générosité des portions).
* **Repères de livraison camerounais :** Prise en compte des repères physiques ("Face pharmacie de la Paix", "Derrière station Total", "Barrière noire avec manguier").
* **Identité visuelle sobre et terrienne :** Palette chaleureuse (terracotta, ocre, vert ndolé, bois brûlé, fond lin/fufu clair), typographie Fraunces / Plus Jakarta Sans, aucune trame néon, zéro faux témoignage, zéro artifice.

---

## 👥 2. Les 4 Rôles & Accès de Démonstration

Des boutons de **connexion rapide en 1 clic** sont intégrés sur la page de connexion (`/comptes/connexion/`), ou vous pouvez utiliser les identifiants suivants (mot de passe universel de test : `passer123`) :

| Rôle | Identifiant | Mot de passe | Description & Espace |
| :--- | :--- | :--- | :--- |
| **Client Gourmand** | `client_sophie` | `passer123` | Navigation, panier, checkout MoMo/Orange, suivi GPS en direct, code secret PIN, avis, assistant IA. |
| **Restaurateur** | `maman_tantine` | `passer123` | Dashboard cuisine (`/dashboard/restaurant/`), commandes en attente, acceptation en 1 clic, gestion de la carte et ruptures de stock. |
| **Livreur Partenaire** | `livreur_martial` | `passer123` | Dashboard coursier (`/dashboard/livreur/`), acceptation des courses disponibles, guidage GPS, validation par code PIN client, gains en FCFA. |
| **Administrateur** | `admin` | `passer123` | Dashboard central (`/dashboard/admin/`), volume d'affaires (GMV), commissions (10%), modération des restaurants et utilisateurs + Admin Django (`/admin-technique/`). |

---

## 🛠️ 3. Architecture Technique (Apps Découplées)

```text
RestoGoumand/
├── accounts/      # CustomUser (client, restaurant, driver, admin), profils et adresses
├── restaurants/   # Restaurant, Category, Dish, menus, cartes publiques et filtrage
├── orders/        # Panier de session, Commande, LigneCommande, timeline, annulation
├── delivery/      # Mission de livraison, attribution livreur, GPS et validation PIN
├── payments/      # Intégrations MTN Mobile Money (*126#), Orange Money (*150#), CinetPay, Cash
├── reviews/       # Avis clients vérifiés et calcul dynamique des notes
├── chatbot/       # 'Tantie Ndolo', assistante culinaire et suivi de commande interactif
├── dashboard/     # Vues et contrôleurs dédiés pour Restaurateur, Livreur et Administrateur
├── core/          # Vitrine publique, sélecteur de ville (Douala/Yaoundé), CGU, Confidentialité, seed_data
└── templates/     # Templates Django modulaires (base storefront et base dashboards pro)
```

---

## 🚀 4. Lancement Rapide

1. **Vérifier les dépendances :**
   ```powershell
   pip install django djangorestframework pillow whitenoise
   ```

2. **Appliquer les migrations et alimenter la base de données :**
   ```powershell
   python manage.py migrate
   python manage.py seed_data
   ```

3. **Lancer la suite de tests automatisés :**
   ```powershell
   python manage.py test
   ```

4. **Démarrer le serveur de développement :**
   ```powershell
   python manage.py runserver
   ```

5. **Accéder à l'application :**
   * **Vitrine publique :** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   * **Assistant Tantie Ndolo :** [http://127.0.0.1:8000/assistant-culinaire/](http://127.0.0.1:8000/assistant-culinaire/)
   * **Tableau de Bord Métier :** [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
   * **Administration Technique Django :** [http://127.0.0.1:8000/admin-technique/](http://127.0.0.1:8000/admin-technique/)
