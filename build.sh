#!/usr/bin/env bash
# Arreter le script en cas d'erreur
set -o errexit

# 1. Installer les dependances du projet
pip install -r requirements.txt

# 2. Rassembler les fichiers statiques (CSS, JS, images)
python manage.py collectstatic --no-input

# 3. Detecter et appliquer les migrations de base de donnees
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# 4. Initialiser le restaurant et les donnees si la base est vide
python manage.py init_data
