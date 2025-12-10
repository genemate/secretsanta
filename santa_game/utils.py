import random
from .models import Participant, SecretSantaMatch


def generate_secret_santa_matches():
    """
    Генерирует распределение Secret Santa
    Каждый участник получает случайного получателя подарка (не самого себя)
    """
    # Удаляем предыдущие распределения
    SecretSantaMatch.objects.all().delete()
    
    # Получаем всех активных участников
    participants = list(Participant.objects.filter(is_active=True))
    
    if len(participants) < 2:
        raise ValueError("Недостаточно участников для игры (минимум 2)")
    
    # Создаем копию списка для перемешивания
    receivers = participants.copy()
    
    # Пытаемся создать валидное распределение
    max_attempts = 100
    for attempt in range(max_attempts):
        random.shuffle(receivers)
        
        # Проверяем, что никто не получил самого себя
        valid = all(giver != receiver for giver, receiver in zip(participants, receivers))
        
        if valid:
            break
    else:
        raise ValueError("Не удалось создать валидное распределение после множества попыток")
    
    # Создаем распределения
    matches_created = 0
    for giver, receiver in zip(participants, receivers):
        SecretSantaMatch.objects.create(
            giver=giver,
            receiver=receiver
        )
        matches_created += 1
    
    return {
        'matches_created': matches_created,
        'participants_count': len(participants)
    }


def get_participant_match(telegram_user_id):
    """
    Получает информацию о том, кому данный участник должен дарить подарок
    """
    try:
        participant = Participant.objects.get(telegram_user_id=telegram_user_id, is_active=True)
        match = SecretSantaMatch.objects.get(giver=participant)
        
        # Отмечаем, что информация была показана
        if not match.revealed:
            match.revealed = True
            match.save()
        
        return {
            'success': True,
            'receiver': match.receiver
        }
    except Participant.DoesNotExist:
        return {
            'success': False,
            'error': 'participant_not_found'
        }
    except SecretSantaMatch.DoesNotExist:
        return {
            'success': False,
            'error': 'match_not_generated'
        }


def link_telegram_user(phone_number, telegram_user_id):
    """
    Связывает участника с его Telegram аккаунтом
    """
    try:
        participant = Participant.objects.get(phone_number=phone_number, is_active=True)
        participant.telegram_user_id = telegram_user_id
        participant.save()
        
        return {
            'success': True,
            'participant': participant
        }
    except Participant.DoesNotExist:
        return {
            'success': False,
            'error': 'participant_not_found'
        }
