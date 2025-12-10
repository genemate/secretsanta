from django.contrib import admin
from django.contrib import messages
from .models import Participant, SecretSantaMatch, GameSession
from .utils import generate_secret_santa_matches


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'telegram_user_id', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'phone_number', 'telegram_user_id')
    readonly_fields = ('telegram_user_id', 'created_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'phone_number', 'is_active')
        }),
        ('Telegram данные', {
            'fields': ('telegram_user_id',)
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SecretSantaMatch)
class SecretSantaMatchAdmin(admin.ModelAdmin):
    list_display = ('giver', 'receiver', 'revealed', 'created_at')
    list_filter = ('revealed', 'created_at')
    search_fields = ('giver__name', 'receiver__name')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        # Не позволяем добавлять вручную
        return False


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'gift_date', 'budget_range', 'is_active', 'matches_generated', 'created_at')
    list_filter = ('is_active', 'matches_generated', 'created_at', 'gift_date')
    search_fields = ('name', 'description')
    readonly_fields = ('matches_generated', 'created_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'is_active', 'matches_generated')
        }),
        ('Детали игры', {
            'fields': ('gift_date', 'budget', 'description', 'reminder_enabled')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def budget_range(self, obj):
        """Отображение бюджета"""
        if obj.budget:
            return f"{int(obj.budget):,} сум"
        return "-"
    budget_range.short_description = "Бюджет"
    
    actions = ['generate_matches']
    
    def generate_matches(self, request, queryset):
        """Генерация распределения Secret Santa"""
        if queryset.count() != 1:
            self.message_user(
                request, 
                "Выберите только одну игровую сессию", 
                level=messages.ERROR
            )
            return
        
        session = queryset.first()
        
        if session.matches_generated:
            self.message_user(
                request, 
                "Распределение уже было сделано для этой сессии", 
                level=messages.WARNING
            )
            return
        
        try:
            result = generate_secret_santa_matches()
            session.matches_generated = True
            session.save()
            
            self.message_user(
                request, 
                f"Успешно создано {result['matches_created']} распределений!", 
                level=messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request, 
                f"Ошибка при создании распределений: {str(e)}", 
                level=messages.ERROR
            )
    
    generate_matches.short_description = "Сгенерировать распределение Secret Santa"
