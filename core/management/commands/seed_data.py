from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "COMMANDE DÉSACTIVÉE : La génération de données fictives ou de démonstration est strictement interdite dans ce projet."

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.ERROR(
                "[REFUSÉ] Aucune donnée fictive ou de démonstration n'est autorisée dans RestoGourmand.\n"
                "Toutes les données (utilisateurs, restaurants, plats, commandes) doivent être créées "
                "réellement par les utilisateurs ou enregistrées manuellement par un administrateur."
            )
        )
