from django.core.management.base import BaseCommand
from santa_game.utils import generate_secret_santa_matches


class Command(BaseCommand):
    help = 'Сгенерировать распределение Secret Santa'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Генерация распределения Secret Santa...')
            result = generate_secret_santa_matches()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Успешно создано {result["matches_created"]} распределений!\n'
                    f'Участников: {result["participants_count"]}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n✗ Ошибка: {str(e)}')
            )
