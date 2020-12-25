from django.core.management.base import BaseCommand

from core.services.games_migrator import GamesMigrator


class Command(BaseCommand):
    help = 'Migrate games from old server to new one'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Start migration process'))
        migrator = GamesMigrator()
        try:
            results = migrator.start()
        except FileNotFoundError as err:
            self.stdout.write(self.style.ERROR(f'Migration error: not found - {err}'))
        except Exception as err:
            self.stdout.write(self.style.ERROR(f'Migration error: exception - {err}'))
        else:
            self.stdout.write(self.style.SUCCESS('Migration successfully finished'))
            for result_row in results:
                self.stdout.write(self.style.WARNING(f'  {result_row}'))
