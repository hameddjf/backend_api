"""
django command to wait for the dtabase to be available.
"""

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    "django command to wait for database"

    def handle(self , *args , **options):
        pass