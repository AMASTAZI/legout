#!/usr/bin/env bash
# Arrêter le script en cas d'erreur
set -o errexit

# 1. Installer les dépendances du projet
pip install -r requirements.txt

# 2. Rassembler les fichiers statiques (CSS, JS, images)
python manage.py collectstatic --no-input

# 3. Appliquer les migrations de base de données
python manage.py migrate

