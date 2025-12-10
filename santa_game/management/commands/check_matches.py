from django.core.management.base import BaseCommand
from santa_game.models import Participant, SecretSantaMatch


class Command(BaseCommand):
    help = 'Проверить статус распределения Secret Santa'

    def handle(self, *args, **options):
        participants = Participant.objects.filter(is_active=True)
        matches = SecretSantaMatch.objects.all()
        
        self.stdout.write(f'\nВсего участников: {participants.count()}')
        self.stdout.write(f'Всего распределений: {matches.count()}\n')
        
        if matches.count() == 0:
            self.stdout.write(self.style.ERROR('Распределение не создано!'))
            return
        
        self.stdout.write(self.style.SUCCESS('Распределения:'))
        for match in matches:
            self.stdout.write(f'{match.giver.name} → {match.receiver.name}')
        
        # Проверяем участников без распределения
        participants_with_match = set(match.giver for match in matches)
        participants_without_match = set(participants) - participants_with_match
        
        if participants_without_match:
            self.stdout.write(self.style.WARNING('\nУчастники без распределения:'))
            for p in participants_without_match:
                self.stdout.write(f'  - {p.name}')
