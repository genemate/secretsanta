from django.db import models


class Participant(models.Model):
    """Участник игры Secret Santa"""
    name = models.CharField(max_length=200, verbose_name="Имя")
    phone_number = models.CharField(max_length=20, unique=True, verbose_name="Номер телефона")
    telegram_user_id = models.BigIntegerField(null=True, blank=True, unique=True, verbose_name="Telegram ID")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    
    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class SecretSantaMatch(models.Model):
    """Распределение Secret Santa - кто кому дарит подарок"""
    giver = models.OneToOneField(
        Participant, 
        on_delete=models.CASCADE, 
        related_name='giving_to',
        verbose_name="Даритель"
    )
    receiver = models.ForeignKey(
        Participant, 
        on_delete=models.CASCADE, 
        related_name='receiving_from',
        verbose_name="Получатель"
    )
    revealed = models.BooleanField(default=False, verbose_name="Показано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Распределение Secret Santa"
        verbose_name_plural = "Распределения Secret Santa"
    
    def __str__(self):
        return f"{self.giver.name} → {self.receiver.name}"


class GameSession(models.Model):
    """Игровая сессия Secret Santa"""
    name = models.CharField(max_length=200, verbose_name="Название игры")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    matches_generated = models.BooleanField(default=False, verbose_name="Распределение сделано")
    
    # Новые поля
    gift_date = models.DateField(null=True, blank=True, verbose_name="Дата вручения подарка")
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Бюджет на подарок")
    description = models.TextField(blank=True, verbose_name="Описание/Правила игры")
    reminder_enabled = models.BooleanField(default=True, verbose_name="Включить напоминания")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Игровая сессия"
        verbose_name_plural = "Игровые сессии"
        ordering = ['-created_at']
    
    def __str__(self):
        status = "Активна" if self.is_active else "Завершена"
        return f"{self.name} ({status})"
