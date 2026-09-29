# Le Gout Cameroun
### Restaurant de Gastronomie Camerounaise & Africaine Authentique

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
| **Client** | `client_sophie` | `passer123` | Navigation, panier, checkout MoMo/Orange, suivi GPS en direct, code secret PIN, avis, assistant IA. |
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

## 🚀 4. Installation Complète des Paquets & Démarrage

### Étape 1 : Création et activation de l'environnement virtuel

* **Créer l'environnement virtuel :**
  ```powershell
  python -m venv venv
  ```

* **Activer l'environnement virtuel :**
  * Sur **Windows (PowerShell)** :
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
  * Sur **Windows (Invite de commandes CMD)** :
    ```cmd
    venv\Scripts\activate.bat
    ```
  * Sur **Linux / macOS** :
    ```bash
    source venv/bin/activate
    ```

* **Mettre à jour pip :**
  ```powershell
  python -m pip install --upgrade pip
  ```

---

### Étape 2 : Téléchargement et installation des paquets requis

Vous pouvez installer l'ensemble des dépendances en une seule fois, via le fichier `requirements.txt`, ou paquet par paquet.

#### Option A — Installation globale en une seule commande (Recommandé) :
```powershell
pip install django djangorestframework pillow reportlab whitenoise python-dotenv tzdata
```

#### Option B — Installation via le fichier `requirements.txt` :
```powershell
pip install -r requirements.txt
```

#### Option C — Installation détaillée paquet par paquet (sans en sauter aucun) :

1. **Django** (Framework web applicatif principal) :
   ```powershell
   pip install django
   ```

2. **Django REST Framework** (API REST et sérialiseurs JSON) :
   ```powershell
   pip install djangorestframework
   ```

3. **Pillow** (Traitement et téléversement des photos des plats et logos `ImageField`) :
   ```powershell
   pip install pillow
   ```

4. **ReportLab** (Moteur de génération automatique des factures et reçus au format PDF) :
   ```powershell
   pip install reportlab
   ```

5. **WhiteNoise** (Service haute performance et mise en cache des fichiers statiques CSS/JS/images) :
   ```powershell
   pip install whitenoise
   ```

6. **Python-dotenv** (Gestion et chargement des variables d'environnement et clés secrètes) :
   ```powershell
   pip install python-dotenv
   ```

7. **Tzdata** (Base des fuseaux horaires IANA / Afrique Centrale pour Windows) :
   ```powershell
   pip install tzdata
   ```

---

### Étape 3 : Initialisation de la base de données & Tests

1. **Appliquer les migrations :**
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Vérifier l'intégrité du système (0 anomalie) :**
   ```powershell
   python manage.py check
   ```

3. **Exécuter la suite complète de tests unitaires :**
   ```powershell
   python manage.py test
   ```

---

### Étape 4 : Lancement du serveur de développement

```powershell
python manage.py runserver
```

---

### Étape 5 : Accès aux interfaces

* **Vitrine publique & Commande en ligne :** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
* **Assistant Culinaire en direct :** [http://127.0.0.1:8000/assistant-culinaire/](http://127.0.0.1:8000/assistant-culinaire/)
* **Tableau de Bord Métier (Restaurateur / Livreur / Admin) :** [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)
* **Administration Technique Django :** [http://127.0.0.1:8000/admin-technique/](http://127.0.0.1:8000/admin-technique/)
